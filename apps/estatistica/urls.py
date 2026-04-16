from django.urls import path
from . import views

app_name = 'estatistica'

urlpatterns = [
    path('lista_formularios/', views.lista_formularios, name='lista_formularios'),
    path('painel/', views.index, name='painel'),
    path('', views.index, name='index'),
    path('<int:formulario_id>/', views.detalhe_formulario, name='detalhe_formulario'),
    path(
        '<int:formulario_id>/perguntas/<int:pergunta_id>/respostas-texto/',
        views.listar_respostas_texto,
        name='listar_respostas_texto',
    ),
]
