from django.contrib import admin

from apps.egresso.models import Egresso

@admin.register(Egresso)
class EgressoAdmin(admin.ModelAdmin):
    list_display = (
        'nome_completo',
        'email',
        'status',
        'curso',
        'ano_conclusao',
    )

    search_fields = (
        'nome_completo',
        'email',
        'whatsapp',
        'curso__nome',
    )

    list_filter = (
        'status',
        'curso',
        'ano_conclusao',
    )

    ordering = ('nome_completo',)
