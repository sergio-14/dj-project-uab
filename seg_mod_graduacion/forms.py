from django import forms
from django.contrib.auth.models import Group
from gestion_usuarios.models import User 
from .models import InvCientifica, ComentarioInvCientifica, HabilitarProyectoFinal,HabilitarSeguimiento
from .models import PerfilProyecto, ComentarioPerfil, RepositorioTitulados, ProyectoFinal, ComentarioProFinal
from .models import ActaProyectoPerfil,HabilitarProyectoFinal, Modalidad, ActaPublica, ActaPrivada
from django.utils.text import slugify

class ModalidadForm(forms.ModelForm):
    class Meta:
        model = Modalidad
        fields = ['nombre']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.nombre)
        if commit:
            instance.save()
        return instance
  
# área de investigación científica 
class InvCientificaForm(forms.ModelForm):
    class Meta:
        model = InvCientifica
        fields = ['invtitulo', 'invdescripcion', 'invdocumentacion']
        widgets = {
            'invdescripcion': forms.Textarea(attrs={'class': 'descripcion-field'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invtitulo'].required = True
        self.fields['invdescripcion'].required = True
        self.fields['invdocumentacion'].required = True
        
class InvComentarioForm(forms.ModelForm):
    class Meta:
        model = ComentarioInvCientifica
        fields = ['invcomentario','invdocorregido'] 
        widgets = {
            'invcomentario': forms.Textarea(attrs={'class': 'comentari-field'}),
        }

class GlobalSettingsForm(forms.ModelForm):
    class Meta:
        model = HabilitarSeguimiento
        fields = ['habilitarInv']

    def __init__(self, *args, **kwargs):
        super(GlobalSettingsForm, self).__init__(*args, **kwargs)
        
# área de perfil de proyecto 
class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilProyecto
        fields = ['pertitulo', 'perdescripcion', 'perdocumentacion', 'permodalidad']
        widgets = {
            'perdescripcion': forms.Textarea(attrs={'class': 'descripcion-field'}),
        }

    def __init__(self, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        
         # Set all fields as required
        self.fields['pertitulo'].required = True
        self.fields['perdescripcion'].required = True
        self.fields['perdocumentacion'].required = True
        self.fields['permodalidad'].required = True
        
        INCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['permodalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['permodalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
      
class PerComentarioForm(forms.ModelForm):
    class Meta:
        model = ComentarioPerfil
        fields = ['percomentario','perdocorregido'] 
        widgets = {
            'percomentario': forms.Textarea(attrs={'class': 'comentari-field'}),
        }

#acta perfil de proyecto 
class ActaPerfilForm(forms.ModelForm):
    class Meta:
        model = ActaProyectoPerfil
        fields = [
            'perperiodo','acta', 'facultad', 'carrera', 'estudiante', 'titulo', 'lugar', 
            'fechadefensa', 'horainicio', 'horafin', 'tutor', 
            'jurado_1', 'jurado_2', 'jurado_3', 'modalidad', 
            'resultado','observacion_1', 'observacion_2', 'observacion_3'
        ]
        labels = {
            'perperiodo': 'Periodo y Gestión',
            'acta': 'Número de Acta',
            'facultad': 'Facultad',
            'carrera': 'Carrera',
            'estudiante': 'Postulante',
            'titulo': 'Título del Proyecto',
            'lugar': 'Lugar de Defensa',
            'fechadefensa': 'Fecha de Defensa',
            'horainicio': 'Hora de Inicio',
            'horafin': 'Hora de Finalización',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primer Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione Modalidad',
            'resultado': 'Resultado de la Defensa',
            'observacion_1': 'Observación del Primer Tribunal',
            'observacion_2': 'Observación del Segundo Tribunal',
            'observacion_3': 'Observación del Tercer Tribunal',
        }
        widgets = {
            'perperiodo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'facultad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'tutor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'resultado': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'observacion_1': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_2': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_3': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        usuarios_con_actividad = HabilitarProyectoFinal.objects.values_list('estudiante', flat=True)
        usuarios_con_perfil_aprobado = PerfilProyecto.objects.filter(perestado='Aprobado').values_list('user', flat=True).distinct() 
        usuarios_con_resultado_suficiente = ActaProyectoPerfil.objects.filter(resultado='Suficiente').values_list('estudiante', flat=True)
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).exclude(
            id__in=usuarios_con_resultado_suficiente
        ).exclude(
            id__in=usuarios_con_actividad
        ).filter(
            id__in=usuarios_con_perfil_aprobado
        ).filter(
            is_active=True  
        )
        
        INCLUDED_RESULT = ['Insuficiente', 'Suficiente']
        self.fields['resultado'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['resultado'].choices
            if choice_label in INCLUDED_RESULT
        ]
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        
#actas defensa privada
class ActaPublicaForm(forms.ModelForm):
    class Meta:
        model = ActaPublica
        fields = [
            'perperiodo','acta', 'facultad', 'carrera', 'estudiante', 'titulo', 'lugar', 
            'fechadefensa', 'horainicio', 'horafin', 'tutor', 
            'jurado_1', 'jurado_2', 'jurado_3', 'modalidad', 
            'resultado','calificacion1', 'calificacion2','notatotal', 'observacion_1', 'observacion_2', 'observacion_3', 'presidenteacta'
        ]
        labels = {
            'perperiodo': 'Periodo y Gestión',
            'acta': 'Número de Acta',
            'facultad': 'Facultad',
            'carrera': 'Carrera',
            'estudiante': 'Postulante',
            'titulo': 'Título del Proyecto',
            'lugar': 'Lugar de Defensa',
            'fechadefensa': 'Fecha de Defensa',
            'horainicio': 'Hora de Inicio',
            'horafin': 'Hora de Finalización',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primer Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione Modalidad',
            'resultado': 'Resultado de la Defensa',
            'calificacion1': '1er. Valor Cuantitativo',
            'calificacion2': '2do. Valor Cuantitativo',
            'notatotal': 'Calificación Total',
            'observacion_1': '1er. Comentario evaluativo',
            'observacion_2': '2do. Comentario evaluativo',
            'observacion_3': '3er. Comentario evaluativo',
            'presidenteacta': 'Asignar Presidente',
        }
        widgets = {
            'perperiodo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'facultad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'tutor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'resultado': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'calificacion1': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '30'}),
            'calificacion2': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '70'}),
            'notatotal': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '100'}),
            'observacion_1': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_2': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_3': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'presidenteacta': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        calificacion1 = cleaned_data.get('calificacion1', 0)
        calificacion2 = cleaned_data.get('calificacion2', 0)
        notatotal = calificacion1 + calificacion2
        cleaned_data['notatotal'] = notatotal
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not self.instance.pk:  # Only set notatotal if instance is new
            instance.notatotal = self.cleaned_data.get('notatotal', 0)
        if commit:
            instance.save()
        return instance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        presidentes_group = Group.objects.get(name="Presidentes Defensas")
        
        # Obtiene los IDs de los usuarios que ya tienen una actividad asignada
        usuarios_con_actividad = RepositorioTitulados.objects.values_list('estudiante', flat=True)
        
       
        # Obtiene los IDs de los usuarios que ya tienen un resultado = 'Suficiente'
        usuarios_con_actapublica = ActaPublica.objects.filter(resultado='Aprobado').values_list('estudiante', flat=True)
        #Filtra los usuarios del grupo "Estudiantes" que cumplan con todos los filtros
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).exclude(
            id__in=usuarios_con_actapublica
        ).exclude(
            id__in=usuarios_con_actividad
        ).filter(
            is_active=True  
        )
        
        INCLUDED_RESULT = ['Aprobado', 'Reprobado','Postergado']
        self.fields['resultado'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['resultado'].choices
            if choice_label in INCLUDED_RESULT
        ]
        # Filtra los usuarios del grupo "Docentes"
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['presidenteacta'].queryset = User.objects.filter(groups=presidentes_group, is_active=True)

#actas defensa publica
class ActaPrivadaForm(forms.ModelForm):
    class Meta:
        model = ActaPrivada
        fields = [
            'perperiodo','acta', 'facultad', 'carrera', 'estudiante', 'titulo', 'lugar', 
            'fechadefensa', 'horainicio', 'horafin', 'tutor', 
            'jurado_1', 'jurado_2', 'jurado_3', 'modalidad', 
            'resultado','calificacion1', 'observacion_1', 'observacion_2', 'observacion_3'
        ]
        labels = {
            'perperiodo': 'Periodo y Gestión',
            'acta': 'Número de Acta',
            'facultad': 'Facultad',
            'carrera': 'Carrera',
            'estudiante': 'Postulante',
            'titulo': 'Título del Proyecto',
            'lugar': 'Lugar de Defensa',
            'fechadefensa': 'Fecha de Defensa',
            'horainicio': 'Hora de Inicio',
            'horafin': 'Hora de Finalización',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primer Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione Modalidad',
            'resultado': 'Resultado de la Defensa',
            'calificacion1': 'Calificacion',
            'observacion_1': 'Observación del Primer Tribunal',
            'observacion_2': 'Observación del Segundo Tribunal',
            'observacion_3': 'Observación del Tercer Tribunal',
        }
        widgets = {
            'perperiodo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'facultad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'tutor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'resultado': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'calificacion1': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '30'}),
            'observacion_1': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_2': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_3': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        
        usuarios_con_repositorio = RepositorioTitulados.objects.values_list('estudiante', flat=True)
        
        usuarios_con_resultado_Suficiente = ActaPrivada.objects.filter(resultado='Suficiente').values_list('estudiante', flat=True).distinct() 
        
        usuarios_con_resultado_Suficienteperfil = ActaProyectoPerfil.objects.filter(resultado='Suficiente').values_list('estudiante', flat=True).distinct() 
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).exclude(
            id__in=usuarios_con_repositorio
        ).exclude(
            id__in=usuarios_con_resultado_Suficiente
        ).filter(
            id__in=usuarios_con_resultado_Suficienteperfil
        )
        
        INCLUDED_RESULT = ['Insuficiente', 'Suficiente']
        self.fields['resultado'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['resultado'].choices
            if choice_label in INCLUDED_RESULT
        ]
        # Filtra los usuarios del grupo "Docentes"
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group)


class ActividadControlForm(forms.ModelForm):
    class Meta:
        model = HabilitarProyectoFinal
        fields = ['estudiante', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3', 'modalidad']
        labels = {
            'estudiante': 'Postulante',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primero Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione modalidad ',
        }
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        usuarios_con_actividad = HabilitarProyectoFinal.objects.values_list('estudiante', flat=True)
        usuarios_con_perfil_aprobado = PerfilProyecto.objects.filter(perestado='Aprobado').values_list('user', flat=True).distinct()
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).exclude(id__in=usuarios_con_actividad).filter(id__in=usuarios_con_perfil_aprobado)
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group)
          
class EditarActividadControlForm(forms.ModelForm):
    class Meta:
        model = HabilitarProyectoFinal
        fields = ['estudiante', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3','modalidad']
        labels = {
            'estudiante': 'Postulante',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primero Tribumal Designado',
            'jurado_2': 'Segundo Tribumal Designado',
            'jurado_3': 'Tercer Tribumal Designado',
            'modalidad': 'Seleccione modalidad ',
        }
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        docentes_group = Group.objects.get(name="Docentes")
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group)
        
      
        if self.instance and self.instance.pk:
          self.fields['estudiante'].disabled = True
             
class ActividadForm(forms.ModelForm):
    class Meta:
        model = ProyectoFinal
        fields = ['estudiante', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3', 'titulo', 'resumen', 'modalidad', 'guia_externo', 'documentacion']
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'tutor': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'jurado_1': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'jurado_2': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'jurado_3': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'modalidad': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'guia_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'documentacion': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class ActComentarioForm(forms.ModelForm):
    class Meta:
        model = ComentarioProFinal
        fields = ['actcomentario','actdocorregido'] 
        widgets = {
            'actcomentario': forms.Textarea(attrs={'class': 'comentari-field'}),
        }
        
