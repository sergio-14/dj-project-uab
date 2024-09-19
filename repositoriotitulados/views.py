from django.shortcuts import render
from seg_mod_graduacion.models import RepositorioTitulados, ProyectoFinal, Modalidad, ActaPublica

from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.text import slugify
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from django.urls import reverse
from .forms import TransferirActividadForm, ActividadRepositorioForm

from django.http import HttpResponse
from .utils import render_pdf

#Repositorio publico
from .forms import ActividadFilterForm, AgregarForm
from django.db.models import Q

class TransferirActividadView(View):
    def get(self, request, actividad_id):
        actividad = get_object_or_404(ProyectoFinal, id=actividad_id, estado='Aprobado')
        form = TransferirActividadForm()
        return render(request, 'admrepositorio/transferir_actividad.html', {'form': form, 'actividad': actividad})

    def post(self, request, actividad_id):
        actividad = get_object_or_404(ProyectoFinal, id=actividad_id, estado='Aprobado')
        form = TransferirActividadForm(request.POST)
        if form.is_valid():
            anio_egreso = form.cleaned_data['anio_egreso']
            numero_acta = form.cleaned_data['numero_acta']
            nota_aprobacion = form.cleaned_data['nota_aprobacion']
          
            actividad.transferir_a_repositorio(
                form.cleaned_data['periodo'],  
                anio_egreso,
                numero_acta,
                nota_aprobacion
                )
            return redirect('dashboard')
        return render(request, 'admrepositorio/transferir_actividad.html', {'form': form, 'actividad': actividad})
      
def listaractividadesaprovadas(request):
    repositorios_existentes = RepositorioTitulados.objects.values_list('estudiante_id', flat=True)
    actividades_aprobadas = ProyectoFinal.objects.filter(
        estado='Aprobado'
    ).exclude(
        estudiante_id__in=repositorios_existentes
    )
    return render(request, 'admrepositorio/listaractividadesaprovadas.html', {'actividades_aprobadas': actividades_aprobadas})

def editar_actividad_repositorio(request, pk):
    actividad = get_object_or_404(RepositorioTitulados, pk=pk)
    
    if request.method == 'POST':
        form = ActividadRepositorioForm(request.POST, instance=actividad)
        if form.is_valid():
            form.save()
            return redirect('listarepositorios')
    else:
        form = ActividadRepositorioForm(instance=actividad)
    
    return render(request, 'admrepositorio/editar_actividad_repositorio.html', {'form': form, 'actividad': actividad})

def actividad_list(request):
    actividades = RepositorioTitulados.objects.all()
    form = ActividadFilterForm(request.GET)

    if form.is_valid():
        nombre_completo = form.cleaned_data.get('nombre_completo')
        modalidad = form.cleaned_data.get('modalidad')
        periodo = form.cleaned_data.get('periodo')

        if nombre_completo:
            nombres = nombre_completo.split()
            if len(nombres) == 2:
                nombre, apellido = nombres
                actividades = actividades.filter(Q(estudiante__nombre__icontains=nombre) & Q(estudiante__apellido__icontains=apellido))
            else:
                actividades = actividades.filter(
                    Q(estudiante__nombre__icontains=nombre_completo) |
                    Q(estudiante__apellido__icontains=nombre_completo)
                )
        if modalidad:
            actividades = actividades.filter(modalidad=modalidad)
        if periodo:
            actividades = actividades.filter(periodo=periodo)

    paginator = Paginator(actividades, 15)  
    page_number = request.GET.get('page')
    try:
        actividades_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        actividades_paginated = paginator.page(1)
    except EmptyPage:
        actividades_paginated = paginator.page(paginator.num_pages)

    return render(request, 'repositoriopublico/actividad_list.html', {'form': form, 'actividades': actividades_paginated})

def agregar_actividad_repositorio(request):
    if request.method == 'POST':
        form = AgregarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('listarepositorios'))
        else:
            print(form.errors)
    else:
        form = AgregarForm()
    
    return render(request, 'admrepositorio/agregar_actividad_repositorio.html', {'form': form})

def listarepositorios(request):
    query = request.GET.get('q', '').strip()
    modalidad_id = request.GET.get('modalidad', None)

    actividades_repositorio = RepositorioTitulados.objects.all()

    if query:
        actividades_repositorio = actividades_repositorio.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    if modalidad_id and modalidad_id.isdigit():
        actividades_repositorio = actividades_repositorio.filter(modalidad__id=int(modalidad_id))
    else:
        modalidad_id = None

    actividades_repositorio = actividades_repositorio.order_by('-id')
    paginator = Paginator(actividades_repositorio, 4)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    modalidades = Modalidad.objects.all()

    context = {
        'page_obj': page_obj,
        'query': query,
        'modalidad': modalidad_id,
        'modalidades': modalidades,
    }
    return render(request, 'admrepositorio/listarepositorios.html', context)

class pdf_reporte_repositorio(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        modalidad_id = request.GET.get('modalidad', '').strip()

        actividades_repositorio = RepositorioTitulados.objects.all()

        if query:
            actividades_repositorio = actividades_repositorio.filter(
                Q(estudiante__nombre__icontains=query) |
                Q(estudiante__apellido__icontains=query)
            )

        if modalidad_id:
            try:
                modalidad_id = int(modalidad_id)
                actividades_repositorio = actividades_repositorio.filter(modalidad__id=modalidad_id)
            except ValueError:
                actividades_repositorio = RepositorioTitulados.objects.none()

        actividades_repositorio = actividades_repositorio.order_by('-id')
        data = {
            'actividades_repositorio': actividades_repositorio,
            'query': query,
            'modalidad_id': modalidad_id,
        }
        
        pdf = render_pdf('admrepositorio/pdf_reporte_repositorio.html', data)
        
        # Devolver el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
    