from django.contrib import admin

# Register your models here.
from .models import T_Fase, T_Tipo, T_Gestion, T_Proyectos_IIISP, T_Semestre, T_Materia
# Register interacion social
admin.site.register(T_Fase)
admin.site.register(T_Tipo)
admin.site.register(T_Gestion)
admin.site.register(T_Proyectos_IIISP)
admin.site.register(T_Semestre)
admin.site.register(T_Materia)

