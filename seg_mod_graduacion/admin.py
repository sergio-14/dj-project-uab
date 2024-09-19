from django.contrib import admin
from .models import InvCientifica, Modalidad, ComentarioInvCientifica, ComentarioPerfil, PerfilProyecto

from .models import ProyectoFinal, HabilitarProyectoFinal,ComentarioProFinal,RepositorioTitulados
from .models import ActaProyectoPerfil, ActaGeneral,ActaPrivada, ActaPublica

admin.site.register(ProyectoFinal)
admin.site.register(HabilitarProyectoFinal)

# Registra tus modelos aquí
admin.site.register(InvCientifica)
admin.site.register(Modalidad)
admin.site.register(ComentarioInvCientifica)
admin.site.register(ComentarioPerfil)
admin.site.register(PerfilProyecto)
admin.site.register(ComentarioProFinal)
admin.site.register(RepositorioTitulados)
admin.site.register(ActaGeneral)
admin.site.register(ActaPublica)
admin.site.register(ActaPrivada)
admin.site.register(ActaProyectoPerfil)