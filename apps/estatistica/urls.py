from django.urls import path
from . import views

app_name = 'estatistica'

urlpatterns = [
    path('lista_formularios/', views.lista_formularios, name='lista_formularios'),
    path('', views.index, name='index'),
    path('<int:formulario_id>/', views.detalhe_formulario, name='detalhe_formulario'),
    path(
        '<int:formulario_id>/respostas-por-usuario/',
        views.respostas_por_usuario,
        name='respostas_por_usuario',
    ),
    path(
        '<int:formulario_id>/respostas-por-usuario/<int:link_id>/',
        views.visualizar_respostas_usuario,
        name='visualizar_respostas_usuario',
    ),
    path(
        '<int:formulario_id>/perguntas/<int:pergunta_id>/respostas-texto/',
        views.listar_respostas_texto,
        name='listar_respostas_texto',
    ),
]
