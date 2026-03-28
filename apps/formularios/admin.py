from django.contrib import admin
from .models import Formulario, Pergunta, Opcao


class OpcaoInline(admin.TabularInline):
    model = Opcao
    extra = 1


class PerguntaInline(admin.TabularInline):
    model = Pergunta
    extra = 1
    ordering = ['ordem']


@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'criado_em')
    list_filter = ('status',)
    inlines = [PerguntaInline]


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('texto', 'formulario', 'tipo', 'ordem')
    list_filter = ('tipo', 'formulario')
    inlines = [OpcaoInline]
