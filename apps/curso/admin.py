from django.contrib import admin

from apps.curso.models import Curso


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'total_egressos')
    search_fields = ('nome',)
    list_filter = ('status',)
    ordering = ('nome',)

    def total_egressos(self, obj):
        return obj.egressos.count()

    total_egressos.short_description = 'Total de egressos'
