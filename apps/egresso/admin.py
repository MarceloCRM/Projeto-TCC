from django.contrib import admin
from apps.egresso.models import Egresso

@admin.register(Egresso)
class EgressoAdmin(admin.ModelAdmin):
    list_display = (
        'nome_completo',
        'email',
        'curso',
        'ano_conclusao',
        'situacao_profissional',
        'empresa_atual',
        'faixa_salarial',
    )

    search_fields = (
        'nome_completo',
        'email',
        'whatsapp',
        'curso',
    )

    list_filter = (
        'situacao_profissional',
        'faixa_salarial',
        'curso',
        'ano_conclusao',
    )

    ordering = ('nome_completo',)
