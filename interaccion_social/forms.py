from django import forms
from .models import T_Proyectos_IIISP, HabilitarFechas, T_Tipo, T_Fase, T_Gestion, T_Semestre, T_Materia
from datetime import date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from datetime import date
        
#proyectos de interaccion social 
class T_ProyectosForm(forms.ModelForm):
    class Meta:
        model = T_Proyectos_IIISP
        fields = [
            'S_Titulo', 'Fecha_Inicio', 'Fecha_Finalizacion', 'S_Descripcion', 
            'S_Documentacion', 'S_Imagen', 'T_Fase_proyecto', 'T_Gestion', 
            'T_Tipo_Proyecto', 'T_Materia'
        ]
        widgets = {
            'Fecha_Inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'Fecha_Finalizacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(T_ProyectosForm, self).__init__(*args, **kwargs)
        all_gestion = T_Gestion.objects.all()
        self.fields['T_Gestion'].queryset = all_gestion  
        
        recent_gestion = all_gestion.order_by('-Id_Ges')[:4]
        self.fields['T_Gestion'].widget.choices = [(gestion.pk, gestion) for gestion in recent_gestion]

        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'S_Titulo',
            Row(
                Column('Fecha_Inicio', css_class='form-group col-md-6 mb-0'),
                Column('Fecha_Finalizacion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'S_Descripcion',
            'S_Documentacion',
            'S_Imagen',
            Row(
                Column('T_Fase_proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Gestion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('T_Tipo_Proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Materia', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )

        # Asegurar que todos los campos sean requeridos
        for field in self.fields:
            self.fields[field].required = True
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Deshabilitar los campos si la fecha no está dentro del rango permitido
        settings = HabilitarFechas.objects.first()
        if settings:
            hoy = date.today()
            if not (settings.fecha_inicio_habilitacion <= hoy <= settings.fecha_fin_habilitacion):
                for field in self.fields:
                    self.fields[field].disabled = True

#editar proyecto IIISP                  
class EditarT_ProyectosForm(forms.ModelForm):
    class Meta:
        model = T_Proyectos_IIISP
        fields = [
            'S_Titulo', 'Fecha_Inicio', 'Fecha_Finalizacion', 'S_Descripcion', 
            'S_Documentacion', 'S_Imagen', 'T_Fase_proyecto', 'T_Gestion', 
            'T_Tipo_Proyecto', 'T_Materia'
        ]
        widgets = {
            'Fecha_Inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'Fecha_Finalizacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditarT_ProyectosForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'S_Titulo',
            Row(
                Column('Fecha_Inicio', css_class='form-group col-md-6 mb-0'),
                Column('Fecha_Finalizacion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'S_Descripcion',
            'S_Documentacion',
            'S_Imagen',
            Row(
                Column('T_Fase_proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Gestion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('T_Tipo_Proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Materia', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )

        for field in self.fields:
            self.fields[field].required = True
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        settings = HabilitarFechas.objects.first()
        if settings:
            hoy = date.today()
            if not (settings.fecha_inicio_habilitacion <= hoy <= settings.fecha_fin_habilitacion):
                for field in self.fields:
                    self.fields[field].disabled = True
                
#Habilitacion de fechas 
class IntSocSettingsForm(forms.ModelForm):
    class Meta:
        model = HabilitarFechas
        fields = ['fecha_inicio_habilitacion', 'fecha_fin_habilitacion']
        widgets = {
            'fecha_inicio_habilitacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_fin_habilitacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(IntSocSettingsForm, self).__init__(*args, **kwargs)
        self.fields['fecha_inicio_habilitacion'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_fin_habilitacion'].input_formats = ['%Y-%m-%d']
        
#tipo 
class TipoProyectoForm(forms.ModelForm):
    class Meta:
        model = T_Tipo
        fields = ['S_Tipo']
#fase 
class FaseProyectoForm(forms.ModelForm):
    class Meta:
        model = T_Fase
        fields = ['S_Fase']
#gestion
class GestionForm(forms.ModelForm):
    class Meta:
        model = T_Gestion
        fields = ['S_Gestion']
#semestre
class SemestreForm(forms.ModelForm):
    class Meta:
        model = T_Semestre
        fields = ['S_Semestre']
#materia
class MateriaForm(forms.ModelForm):
    class Meta:
        model = T_Materia
        fields = ['S_Materia', 'T_Semestre']