from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from .forms import InvCientificaForm, InvComentarioForm, GlobalSettingsForm, PerfilForm, PerComentarioForm, ActComentarioForm, ActaPerfilForm
from .models import InvCientifica, ComentarioInvCientifica, HabilitarSeguimiento, PerfilProyecto, ComentarioPerfil, ComentarioProFinal

##############  permisos decoradores  para funciones y clases   ################  

#modalidad de graduación permigroup 
def permiso_M_G(user, ADMMGS):
    try:
        grupo = Group.objects.get(name=ADMMGS)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{ADMMGS}' no existe.")
    
    if grupo in user.groups.all():
        return True
    else:
        raise PermissionDenied
    
#permiso para docentes  
def permiso_Docentes(user, Docentes):
    try:
        grupo = Group.objects.get(name=Docentes)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{Docentes}' no existe.")
    
    if grupo in user.groups.all():
        return True
    else:
        raise PermissionDenied

#permiso para estudiantes
def permiso_Estudiantes(user, Estudiantes):
    try:
        grupo = Group.objects.get(name=Estudiantes)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{Estudiantes}' no existe.")
    
    if grupo in user.groups.all():
        return True
    else:
        raise PermissionDenied

#vista 403
def handle_permission_denied(request, exception):
    return render(request, '403.html', status=403)

################  vistas modalidad de graduación  ##########################

#vista agregar formulario alcance de proyecto 
@login_required
@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes')) 
def vista_investigacion(request):
    proyectos_usuario = InvCientifica.objects.filter(user=request.user).order_by('-invfecha_creacion').prefetch_related('comentarioinvcientifica_set')

    paginator = Paginator(proyectos_usuario, 1)  
    page_number = request.GET.get('page')
    proyectos_paginados = paginator.get_page(page_number)

    return render(request, 'invcientifica/vista_investigacion.html', {'proyectos': proyectos_paginados})

@method_decorator(user_passes_test(lambda u: permiso_M_G(u, 'ADMMGS')), name='dispatch')
class ProyectosParaAprobar(View):
    def get(self, request):
        proyectos = InvCientifica.objects.filter(investado='Pendiente')
        proyectos_con_formulario = {proyecto: InvComentarioForm() for proyecto in proyectos}
        
        context = {
            'proyectos': proyectos_con_formulario,
        }
        return render(request, 'invcientifica/ProyectosParaAprobar.html', context)
    
    def post(self, request):
        proyecto_id = request.POST.get('proyecto_id')
        comentario_texto = request.POST.get('invcomentario')
        invdocorregido = request.FILES.get('invdocorregido')
        
        if proyecto_id and comentario_texto:
            proyecto = get_object_or_404(InvCientifica, pk=proyecto_id)
            comentario = ComentarioInvCientifica(
                invcomentario=comentario_texto,
                user=request.user,
                invproyecto_relacionado=proyecto,
                invdocorregido=invdocorregido
            )
            comentario.save()
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'Hubo un error al agregar el comentario.')
            return redirect('ProyectosParaAprobar')
        
        if 'aprobar' in request.POST:
            return AprobarProyecto().post(request, proyecto_id)
        elif 'rechazar' in request.POST:
            return RechazarProyecto().post(request, proyecto_id)
        else:
            messages.error(request, 'Hubo un error al procesar la solicitud.')
            return redirect('ProyectosParaAprobar')

class AprobarProyecto(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(InvCientifica, pk=proyecto_id)
        proyecto.investado = 'Aprobado'
        proyecto.save()
        messages.success(request, '¡Proyecto aprobado exitosamente!')
        return redirect('ProyectosParaAprobar')

class RechazarProyecto(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(InvCientifica, pk=proyecto_id)
        proyecto.investado = 'Rechazado'
        proyecto.save()
        messages.error(request, '¡Proyecto rechazado!')
        return redirect('ProyectosParaAprobar')

@user_passes_test(lambda u: permiso_M_G(u, 'ADMMGS')) 
def global_settings_view(request):
    settings = HabilitarSeguimiento.objects.first()
    if not settings:
        settings = HabilitarSeguimiento()

    if request.method == 'POST':
        form = GlobalSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = GlobalSettingsForm(instance=settings)
    
    return render(request, 'invcientifica/global_settings.html', {'form': form, 'settings': settings})

@login_required
@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes')) 
def agregar_investigacion(request):
    settings = HabilitarSeguimiento.objects.first()
    
    if not settings:
        messages.error(request, 'No se encontró la configuración global. Por favor, contacta al administrador.')
        return redirect('global_settings')
    
    tiene_investigacion_aprobada = InvCientifica.objects.filter(user=request.user, investado='Aprobado').exists()
    
    form_disabled = not settings.habilitarInv or tiene_investigacion_aprobada
    
    if request.method == 'POST' and not form_disabled:
        form = InvCientificaForm(request.POST, request.FILES)
        if form.is_valid():
            proyecto = form.save(commit=False)
            
            slug = slugify(proyecto.invtitulo)
            counter = 1
            while InvCientifica.objects.filter(slug=slug).exists():
                slug = f"{slug}-{counter}"
                counter += 1
            proyecto.slug = slug
            
            proyecto.user = request.user
            proyecto.save()
            return redirect('dashboard')
    else:
        form = InvCientificaForm()
    
    if form_disabled:
        for field in form.fields.values():
            field.widget.attrs['disabled'] = 'disabled'
    
    return render(request, 'invcientifica/agregar_investigacion.html', {
        'form': form,
        'form_disabled': form_disabled,
    })

########  PERFIL DE PROYECTO M. G 2DA PARTE   #########
@login_required
@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes')) 
def vista_perfil(request):
    proyectos_usuario = PerfilProyecto.objects.filter(user=request.user).order_by('-perfecha_creacion').prefetch_related('comentarios')
    
    paginator = Paginator(proyectos_usuario, 1) 
    page_number = request.GET.get('page')
    proyectos_paginados = paginator.get_page(page_number)

    return render(request, 'perfil/vista_perfil.html', {'proyectos': proyectos_paginados})

@method_decorator(user_passes_test(lambda u: permiso_M_G(u, 'ADMMGS')), name='dispatch')
class PerfilesParaAprobar(View):
    def get(self, request):
        proyectos = PerfilProyecto.objects.filter(perestado='Pendiente')
        proyectos_con_formulario = {proyecto: PerComentarioForm() for proyecto in proyectos}
        
        context = {
            'proyectos': proyectos_con_formulario,
        }
        return render(request, 'perfil/PerfilesParaAprobar.html', context)
    
    def post(self, request):
        proyecto_id = request.POST.get('proyecto_id')
        comentario_texto = request.POST.get('comentario_texto')
        perdocorregido = request.FILES.get('perdocorregido')
        if proyecto_id and comentario_texto:
            proyecto = get_object_or_404(PerfilProyecto, pk=proyecto_id)
            ComentarioPerfil.objects.create(
                percomentario=comentario_texto, 
                user=request.user, 
                perproyecto_relacionado=proyecto,
                perdocorregido=perdocorregido
                )
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'Hubo un error al agregar el comentario.')
        
        if 'aprobar' in request.POST:
            return AprobarPerfil().post(request, proyecto_id)
        elif 'rechazar' in request.POST:
            return RechazarPerfil().post(request, proyecto_id)
        else:
            messages.error(request, 'Hubo un error al procesar la solicitud.')
            return redirect('PerfilesParaAprobar')
    
class AprobarPerfil(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(PerfilProyecto, pk=proyecto_id)
        proyecto.perestado = 'Aprobado'
        proyecto.save()
        messages.success(request, '¡Perfil aprobado exitosamente!')
        return redirect('PerfilesParaAprobar')

class RechazarPerfil(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(PerfilProyecto, pk=proyecto_id)
        proyecto.perestado = 'Rechazado'
        proyecto.save()
        messages.error(request, '¡Perfil rechazado!')
        return redirect('PerfilesParaAprobar')

@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes'))
def agregar_perfil(request):
    tiene_investigacion_aprobada = InvCientifica.objects.filter(user=request.user, investado='Aprobado').exists()
    tiene_perfil_aprobado = PerfilProyecto.objects.filter(user=request.user, perestado='Aprobado').exists()
    form_disabled = not tiene_investigacion_aprobada or tiene_perfil_aprobado

    if request.method == 'POST' and not form_disabled:
        formp = PerfilForm(request.POST, request.FILES)
        if formp.is_valid():
            proyecto = formp.save(commit=False)
            
            slug = slugify(proyecto.pertitulo)
            counter = 1
            while PerfilProyecto.objects.filter(slug=slug).exists():
                slug = f"{slug}-{counter}"
                counter += 1
            proyecto.slug = slug
            
            proyecto.user = request.user
            proyecto.save()
            return redirect('dashboard')
        else:
            print("Formulario no es válido:", formp.errors)
    else:
        formp = PerfilForm()

    if form_disabled:
        for field in formp.fields.values():
            field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'perfil/agregar_perfil.html', {
        'formp': formp,
        'form_disabled': form_disabled,
    })
    
#### acta de perfil de proyecto #####
def agregar_actaperfil(request):
    if request.method == 'POST':
        form = ActaPerfilForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Acta de perfil agregada exitosamente.')
            return redirect('dashboard')  
    else:
        form = ActaPerfilForm()

    return render(request, 'actas/agregar_actaperfil.html', {'form': form})

from .forms import ActaPrivadaForm ,ActaPublicaForm

def agregar_actaprivada(request):
    if request.method == 'POST':
        form = ActaPrivadaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Acta agregada exitosamente.')
            return redirect('dashboard')  # Assuming you have a list view for actas
    else:
        form = ActaPrivadaForm()

    return render(request, 'actas/agregar_actaprivada.html', {'form': form})

from django.http import JsonResponse
from .models import ActaProyectoPerfil, ActaPrivada

def buscar_estudiante_privada(request):
    estudiante_id = request.GET.get('id', None)
    if estudiante_id:
        try:
            # Filtra por estudiante_id y resultado='Suficiente'
            acta_proyecto = ActaProyectoPerfil.objects.filter(
                estudiante_id=estudiante_id, 
                resultado='Suficiente'
            ).first()  # Obtén el primer resultado que cumpla la condición

            if acta_proyecto:
                data = {
                    'acta': acta_proyecto.acta,
                    'titulo': acta_proyecto.titulo,
                    'lugar': acta_proyecto.lugar,
                    'tutor': acta_proyecto.tutor.id,
                    'jurado_1': acta_proyecto.jurado_1.id,
                    'jurado_2': acta_proyecto.jurado_2.id,
                    'jurado_3': acta_proyecto.jurado_3.id,
                    'modalidad': acta_proyecto.modalidad.id,
                }
            else:
                data = {}
        except ActaProyectoPerfil.DoesNotExist:
            data = {}
    else:
        data = {}

    return JsonResponse(data)

def buscar_estudiante_publica(request):
    estudiante_id = request.GET.get('id', None)
    if estudiante_id:
        try:
            # Filtra por estudiante_id y resultado='Suficiente'
            acta_proyecto = ActaPrivada.objects.filter(
                estudiante_id=estudiante_id, 
                resultado='Suficiente'
            ).first()  # Obtén el primer resultado que cumpla la condición

            if acta_proyecto:
                data = {
                    'acta': acta_proyecto.acta,
                    'titulo': acta_proyecto.titulo,
                    'lugar': acta_proyecto.lugar,
                    'tutor': acta_proyecto.tutor.id,
                    'jurado_1': acta_proyecto.jurado_1.id,
                    'jurado_2': acta_proyecto.jurado_2.id,
                    'jurado_3': acta_proyecto.jurado_3.id,
                    'modalidad': acta_proyecto.modalidad.id,
                    'calificacion1': acta_proyecto.calificacion1,
                }
            else:
                data = {}
        except ActaPrivada.DoesNotExist:
            data = {}
    else:
        data = {}

    return JsonResponse(data)

def agregar_actapublica(request):
    if request.method == 'POST':
        form = ActaPublicaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Acta agregada exitosamente.')
            return redirect('dashboard')  # Assuming you have a list view for actas
    else:
        form = ActaPublicaForm()

    return render(request, 'actas/agregar_actapublica.html', {'form': form})

from .models import ActaProyectoPerfil

def actaperfil_list(request):
    query = request.GET.get('q')  
    actas_list = ActaProyectoPerfil.objects.all()

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'perfil/actaperfil_list.html', {'actas': actas, 'query': query})

class Pdf_ReporteActa(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  
        acta = get_object_or_404(ActaProyectoPerfil, pk=acta_id)  
        
        context = {
            'acta': acta,
            'jurado_1_firma_url': request.build_absolute_uri(acta.jurado_1.firma.url) if acta.jurado_1.firma else None,
            'jurado_2_firma_url': request.build_absolute_uri(acta.jurado_2.firma.url) if acta.jurado_2.firma else None,
            'jurado_3_firma_url': request.build_absolute_uri(acta.jurado_3.firma.url) if acta.jurado_3.firma else None,
            'tutor_firma_url': request.build_absolute_uri(acta.tutor.firma.url) if acta.tutor.firma else None,
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActa.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
    
###########acta privada ###########################
def actaprivada_list(request):
    query = request.GET.get('q')  
    actas_list = ActaPrivada.objects.all()

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'proyectofinal/actaprivada_list.html', {'actas': actas, 'query': query})

class Pdf_ReporteActaPrivada(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  # Obtener el id desde la URL
        acta = get_object_or_404(ActaPrivada, pk=acta_id)  # Recuperar la instancia ActaPerfil
        
        # Construir URLs absolutas para las firmas
        context = {
            'acta': acta,
            'jurado_1_firma_url': request.build_absolute_uri(acta.jurado_1.firma.url) if acta.jurado_1.firma else None,
            'jurado_2_firma_url': request.build_absolute_uri(acta.jurado_2.firma.url) if acta.jurado_2.firma else None,
            'jurado_3_firma_url': request.build_absolute_uri(acta.jurado_3.firma.url) if acta.jurado_3.firma else None,
            'tutor_firma_url': request.build_absolute_uri(acta.tutor.firma.url) if acta.tutor.firma else None,
            
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActaPrivada.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
    

###########acta privada ###########################
def actapublica_list(request):
    query = request.GET.get('q')  
    actas_list = ActaPublica.objects.all()

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'proyectofinal/actapublica_list.html', {'actas': actas, 'query': query})

class Pdf_ReporteActaPublica(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  
        acta = get_object_or_404(ActaPublica, pk=acta_id)  
        
        context = {
            'acta': acta,
            'jurado_1_firma_url': request.build_absolute_uri(acta.jurado_1.firma.url) if acta.jurado_1.firma else None,
            'jurado_2_firma_url': request.build_absolute_uri(acta.jurado_2.firma.url) if acta.jurado_2.firma else None,
            'jurado_3_firma_url': request.build_absolute_uri(acta.jurado_3.firma.url) if acta.jurado_3.firma else None,
            'tutor_firma_url': request.build_absolute_uri(acta.tutor.firma.url) if acta.tutor.firma else None,
            'presidenteacta_firma_url': request.build_absolute_uri(acta.presidenteacta.firma.url) if acta.presidenteacta.firma else None,
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActaPublica.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
    

### VISTA PARA EL ESTUDIANTE ###
###############################################################

from .models import HabilitarProyectoFinal, ActaPublica
from .forms import ActividadControlForm, EditarActividadControlForm

#controlador de proyecto final
def crear_actividad_control(request):
    if request.method == 'POST':
        form = ActividadControlForm(request.POST)
        if form.is_valid():
            actividad_control = form.save()
            actividad_control.habilitar_actividad()
            return redirect('dashboard') 
    else:
        form = ActividadControlForm()
    
    return render(request, 'controlador/crear_actividad_control.html', {'form': form})

def buscar_estudiante_paractivar(request):
    estudiante_id = request.GET.get('id', None)
    if estudiante_id:
        try:
            # Filtra por estudiante_id y resultado='Suficiente'
            activar_estudiante = ActaProyectoPerfil.objects.filter(
                estudiante_id=estudiante_id, 
                resultado='Suficiente'
            ).first()  # Obtén el primer resultado que cumpla la condición

            if activar_estudiante:
                data = {
                    'tutor': activar_estudiante.tutor.id,
                    'jurado_1': activar_estudiante.jurado_1.id,
                    'jurado_2': activar_estudiante.jurado_2.id,
                    'jurado_3': activar_estudiante.jurado_3.id,
                    'modalidad': activar_estudiante.modalidad.id,
                }
            else:
                data = {}
        except ActaProyectoPerfil.DoesNotExist:
            data = {}
    else:
        data = {}

    return JsonResponse(data)

#lista de agregacion y proyectos finales
@login_required
def lista_actividad_control(request):
    actividades_control = HabilitarProyectoFinal.objects.all().order_by('-id').distinct()

    paginator = Paginator(actividades_control, 3) 
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number) 

    return render(request, 'controlador/lista_actividad_control.html', {'page_obj': page_obj})


@login_required
def editar_actividad_control(request, pk):
    actividad_control = get_object_or_404(HabilitarProyectoFinal, pk=pk)

    if request.method == 'POST':
        form = EditarActividadControlForm(request.POST, instance=actividad_control)
        if form.is_valid():
            form.save()
            return redirect('lista_actividad_control')
    else:
        form = EditarActividadControlForm(instance=actividad_control)

    return render(request, 'controlador/editar_actividad_control.html', {'form': form})


from .models import ProyectoFinal, RepositorioTitulados
from django.utils import timezone
from .forms import ActividadForm

@login_required
def crear_actividad(request):
    estudiante = request.user
    actividad = None
    form = None

    try:
        actividad = ProyectoFinal.objects.get(estudiante=estudiante)
    except ProyectoFinal.DoesNotExist:
        actividad = None

    # Verificar si el estudiante ya tiene un RepositorioTitulados asignado
    repositorio_asignado = RepositorioTitulados.objects.filter(estudiante=estudiante).first()

    if repositorio_asignado:
        # Si ya tiene un repositorio asignado, deshabilitar el formulario
        form = ActividadForm(instance=actividad)
        for field in form.fields.values():
            field.widget.attrs['disabled'] = True
    elif actividad and actividad.habilitada:
        if request.method == 'POST':
            form = ActividadForm(request.POST, request.FILES, instance=actividad)
            if form.is_valid():
                actividad = form.save(commit=False)
                actividad.fecha = timezone.now()
                #actividad.estado = 'Pendiente' 
                actividad.save()
                return redirect('dashboard')
        else:
            form = ActividadForm(instance=actividad)
    else:
        form = ActividadForm()

    return render(request, 'proyectofinal/crear_actividad.html', {
        'form': form,
        'actividad': actividad,
        'repositorio_asignado': repositorio_asignado
    })

def lista_actividad(request):
    user = request.user
    actividades = ProyectoFinal.objects.filter(estudiante=user).prefetch_related('comentarios').order_by('-fecha')
    return render(request, 'proyectofinal/lista_actividad.html', {'actividades': actividades})

from .models import ComentarioProFinal

@login_required
def revisar_actividad(request, actividad_id):
    actividad = get_object_or_404(ProyectoFinal, pk=actividad_id)
    user = request.user

    if request.method == 'POST':
        # Procesar el formulario de revisión y comentarios
        if user == actividad.jurado_1 and 'jurado_1_aprobado' in request.POST:
            actividad.jurado_1_aprobado = request.POST.get('jurado_1_aprobado') == 'on'

        if user == actividad.jurado_2 and 'jurado_2_aprobado' in request.POST:
            actividad.jurado_2_aprobado = request.POST.get('jurado_2_aprobado') == 'on'

        if user == actividad.jurado_3 and 'jurado_3_aprobado' in request.POST:
            actividad.jurado_3_aprobado = request.POST.get('jurado_3_aprobado') == 'on'

        # Guardar la actividad después de la revisión
        actividad.save()

        # Crear comentario si existe
        comentario_texto = request.POST.get('comentario_texto', '')
        actdocorregido = request.FILES.get('actdocorregido')
        if comentario_texto:
            comentario = ComentarioProFinal(
                actcomentario=comentario_texto,
                user=request.user,
                actproyecto_relacionado=actividad,
                actdocorregido=actdocorregido
            )
            comentario.save()

        messages.success(request, 'Revisión de actividad y comentario guardados correctamente.')
        return redirect('listaactividades')

    return render(request, 'proyectofinal/revisar_actividad.html', {'actividad': actividad})


def listaractividades(request):
    actividades = ProyectoFinal.objects.exclude(
        estado='Aprobado'
    ).order_by('-fecha')
    
    return render(request, 'controlador/listaractividades.html', {'actividades': actividades})

from django.db.models import Q
@login_required
def listaactividades(request):
    usuario = request.user
    actividades = ProyectoFinal.objects.filter(
        Q(tutor=usuario) | Q(jurado_1=usuario) | Q(jurado_2=usuario) | Q(jurado_3=usuario)
    ).exclude(
        estado='Aprobado'
    ).order_by('-fecha')
    return render(request, 'controlador/listaactividades.html', {'actividades': actividades})

@user_passes_test(lambda u: permiso_M_G(u, 'ADMMGS'))
def revision(request, actividad_id):
    actividad = get_object_or_404(ProyectoFinal, pk=actividad_id)
    user = request.user
    todos_aprobados = actividad.jurado_1_aprobado and actividad.jurado_2_aprobado and actividad.jurado_3_aprobado

    if request.method == 'POST':
        if 'cambiar_estado' in request.POST:
            if todos_aprobados:
                actividad.estado = 'Aprobado'
                actividad.save()
                messages.success(request, 'Estado de la actividad cambiado a Aprobado.')
            else:
                messages.error(request, 'Necesita que los 3 jurados aprueben la documentación para poder cambiar el estado.')
                
            return redirect('listaactividades')

    return render(request, 'controlador/revision.html', {'actividad': actividad, 'todos_aprobados': todos_aprobados})


from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from .models import Modalidad
from .forms import ModalidadForm

class ModalidadCreateView(CreateView):
    model = Modalidad
    form_class = ModalidadForm
    template_name = 'modalidad/modalidadagregar.html'
    success_url = reverse_lazy('listarmodalidades')

class ModalidadListView(ListView):
    model = Modalidad
    template_name = 'modalidad/listarmodalidades.html'
    context_object_name = 'modalidades'

class ModalidadUpdateView(UpdateView):
    model = Modalidad
    form_class = ModalidadForm
    template_name = 'modalidad/editarmodalidad.html'
    success_url = reverse_lazy('listarmodalidades')
    
def home_reporte(request):
   return render(request, "reportes/home_reporte.html")

# session de reportes

from django.http import HttpResponse
from .utils import render_pdf

class pdf_reporteinv(View):
    def get(self, request, *args, **kwargs):
        # Obtener la actividad específica
        actividad_id = self.kwargs.get('pk')  # Obtener el id desde la URL
        actividad = get_object_or_404(InvCientifica, pk=actividad_id)
        
        # Obtener los comentarios relacionados con la actividad
        comentarios = ComentarioInvCientifica.objects.filter(invproyecto_relacionado=actividad)

        # Añadir la URL completa de la firma al contexto
        for comentario in comentarios:
            if comentario.user.firma:
                comentario.user.firma_url = request.build_absolute_uri(comentario.user.firma.url)
            else:
                comentario.user.firma_url = None

        # Preparar los datos para pasar al template
        data = {
            'actividad': actividad,
            'comentarios': comentarios  # Incluir los comentarios en el contexto
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/pdf_reporteinv.html', data)
        
        # Devolver el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
 
from django.db import models

def listarinvcientifica(request):
    # Filtrado por nombre del usuario
    query = request.GET.get('q')
    if query:
        cientifica = InvCientifica.objects.filter(
            models.Q(user__nombre__icontains=query) |
            models.Q(user__apellido__icontains=query)
        )
    else:
        cientifica = InvCientifica.objects.all()

    # Ordenar por fecha de creación o id
    cientifica = cientifica.order_by('-id')

    # Paginación - Muestra 10 registros por página
    paginator = Paginator(cientifica, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'invcientifica/listarinvcientifica.html', context)

class Pdf_Reporte_InvFiltrado(View):
    def get(self, request, *args, **kwargs):
        # Filtrar por nombre y apellido
        query = request.GET.get('q')
        if query:
            cientifica = InvCientifica.objects.filter(
                models.Q(user__nombre__icontains=query) |
                models.Q(user__apellido__icontains=query)
            )
        else:
            cientifica = InvCientifica.objects.all()

        # Añadir la URL completa de la firma al contexto para cada comentario
        for actividad in cientifica:
            comentarios = ComentarioInvCientifica.objects.filter(invproyecto_relacionado=actividad)
            for comentario in comentarios:
                if comentario.user.firma:
                    comentario.user.firma_url = request.build_absolute_uri(comentario.user.firma.url)
                else:
                    comentario.user.firma_url = None
            actividad.comentarios = comentarios  # Agregar comentarios al objeto de actividad

        # Preparar los datos para pasar al template
        data = {
            'cientifica': cientifica,
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_Reporte_InvFiltrado.html', data)
        
        # Devolver el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
      
#reportes perfil de proyecto 
def listarperfiles(request):
    query = request.GET.get('q', '').strip()
    modalidad_id = request.GET.get('modalidad', None)

    perfiles = PerfilProyecto.objects.all()

    if query:
        perfiles = perfiles.filter(
            Q(user__nombre__icontains=query) |
            Q(user__apellido__icontains=query)
        )

    if modalidad_id and modalidad_id.isdigit():
        perfiles = perfiles.filter(permodalidad__id=int(modalidad_id))
    else:
        modalidad_id = None

    perfiles = perfiles.order_by('-id')
    paginator = Paginator(perfiles, 3)  # Paginación ajustada a 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    modalidades = Modalidad.objects.all()

    context = {
        'page_obj': page_obj,
        'query': query,
        'modalidad': modalidad_id,
        'modalidades': modalidades,
    }
    return render(request, 'perfil/listarperfiles.html', context)

from django.template.loader import render_to_string

class Pdf_Reporte_Perfiles(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        modalidad_id = request.GET.get('modalidad', '').strip()

        perfiles = PerfilProyecto.objects.all()

        if query:
            perfiles = perfiles.filter(
                Q(user__nombre__icontains=query) |
                Q(user__apellido__icontains=query)
            )

        if modalidad_id:
            try:
                modalidad_id = int(modalidad_id)
                perfiles = perfiles.filter(permodalidad__id=modalidad_id)
            except ValueError:
                perfiles = PerfilProyecto.objects.none()

        perfiles = perfiles.order_by('-id')

        for perfil in perfiles:
            comentarios = ComentarioPerfil.objects.filter(perproyecto_relacionado=perfil)
            for comentario in comentarios:
                if comentario.user.firma:
                    comentario.user.firma_url = request.build_absolute_uri(comentario.user.firma.url)
                else:
                    comentario.user.firma_url = None
            perfil.comentarios_list = comentarios

        data = {
            'perfiles': perfiles,
            'query': query,
            'modalidad_id': modalidad_id,
        }
        
        pdf = render_pdf('reportes/Pdf_Reporte_Perfiles.html', data)
        
        # Devolver el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
 

    
