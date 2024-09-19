from seg_mod_graduacion.models import RepositorioTitulados, Modalidad
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
import datetime
from gestion_usuarios.models import User

current_year = datetime.datetime.now().year
YEAR_CHOICES = [(year, year) for year in range(2020, current_year + 1)]

class TransferirActividadForm(forms.Form):
    periodo = forms.CharField(
        max_length=50,
        label='Periodo y Gestion',
        widget=forms.TextInput(attrs={'placeholder': 'Asigne periodo/gestion'}) 
    ) 
    anio_egreso = forms.ChoiceField(
        label='Año de Egreso',
        choices=YEAR_CHOICES,
        initial=current_year,  
        widget=forms.Select(attrs={'id': 'anio_egreso', 'size': 1}) 
    )
    numero_acta = forms.CharField(label='Número de Acta', max_length=50)
    nota_aprobacion = forms.IntegerField(  
        label='Nota',
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'min': 50, 'max': 100})
    )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class ActividadRepositorioForm(forms.ModelForm):
    nota_aprobacion = forms.IntegerField(  
        label='Nota',
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'min': 50, 'max': 100})
    )

    def clean(self):
        cleaned_data = super().clean()
        anio_egreso = cleaned_data.get('anio_egreso')
        
        if anio_egreso is not None:
            try:
                anio_egreso = int(anio_egreso)
            except ValueError:
                raise ValidationError({'anio_egreso': 'El valor de año de egreso debe ser un número entero.'})

        cleaned_data['anio_egreso'] = anio_egreso

        return cleaned_data

    class Meta:
        model = RepositorioTitulados
        fields = ['periodo', 'anio_egreso', 'numero_acta', 'nota_aprobacion']
        labels = {
            'periodo': 'Periodo y Gestion',
            'anio_egreso': 'Año Egreso',
            'numero_acta': 'Número de Acta',
            'nota_aprobacion': 'Nota'
        }

class ActividadFilterForm(forms.Form):
    nombre_completo = forms.CharField(
        max_length=100, 
        required=False, 
        label='Nombre Completo',
        widget=forms.TextInput(attrs={'placeholder': 'Nombre y apellido del estudiante', 'class': 'form-control'}),
    )
    modalidad = forms.ModelChoiceField(
        queryset=Modalidad.objects.all(), 
        required=False, label='Modalidad',
        widget=forms.Select(attrs={'class': 'form-select'}),
        )
    periodo = forms.CharField(
        max_length=50,
        required=False,
        label='Gestion',
        widget=forms.TextInput(attrs={'placeholder': 'ejm: "1/año" o "2/año"  ','class': 'form-control'}),
    )

class AgregarForm(forms.ModelForm):
    nota_aprobacion = forms.IntegerField(  
        label='Nota',
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'min': 50, 'max': 100, 'class': 'form-control'}),
    )
    
    class Meta:
        model = RepositorioTitulados
        fields = [
            'estudiante', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3', 
            'titulo', 'resumen', 'modalidad', 
            'guia_externo', 'documentacion', 'periodo', 
            'anio_egreso', 'numero_acta', 'nota_aprobacion', 'fecha'
        ]
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'guia_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'documentacion': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control'}),
            'anio_egreso': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_acta': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            
        }
        labels = {
            'estudiante': 'Nombre Completo Egresado:',
            'tutor': 'Tutor Asignado:',
            'jurado_1': '1er. Tribunal Asignado:',
            'jurado_2': '2do. Tribunal Asignado:',
            'jurado_3': '3er. Tribunal Asignado:',
            'titulo': 'Titulo del Proyecto:',
            'resumen': 'Descripción Breve del Proyecto:',
            'modalidad': 'Modalidad:',
            'guia_externo': 'Tutor Externo:',
            'documentacion': 'Documentación:',
            'periodo': 'Periodo y Gestion:',
            'anio_egreso': 'Año de Egreso',
            'numero_acta': 'Número de Acta',
            'nota_aprobacion': 'Nota',
            'fecha': 'Fecha'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        estudiantes = User.objects.filter(groups__name='Estudiantes').exclude(repo_estudiante__isnull=False)
        self.fields['estudiante'].queryset = estudiantes

        docentes = User.objects.filter(groups__name='Docentes')
        self.fields['tutor'].queryset = docentes
        self.fields['jurado_1'].queryset = docentes
        self.fields['jurado_2'].queryset = docentes
        self.fields['jurado_3'].queryset = docentes
        
        EXCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['modalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['modalidad'].choices
            if choice_label not in EXCLUDED_MODALITIES
        ]
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.habilitada = True
        instance.jurado_1_aprobado = True
        instance.jurado_2_aprobado = True
        instance.jurado_3_aprobado = True
        instance.estado = 'Aprobado'
        if commit:
            instance.save()
        return instance
    
    def clean(self):
        cleaned_data = super().clean()
        anio_egreso = cleaned_data.get('anio_egreso')
        
        if anio_egreso is not None:
            try:
                anio_egreso = int(anio_egreso)
            except ValueError:
                raise ValidationError({'anio_egreso': 'El valor de año de egreso debe ser un número entero.'})

        cleaned_data['anio_egreso'] = anio_egreso

        return cleaned_data
