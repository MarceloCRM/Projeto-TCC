from django.urls import path
from . import views

app_name = 'formularios'

urlpatterns = [
    path('<int:formulario_id>/responder/', views.responder_formulario, name='responder'),
    path('<int:formulario_id>/estatisticas/', views.estatisticas_formulario, name='estatisticas'),
    path('<int:formulario_id>/editar_formulario/', views.editar_formulario, name='editar_formulario'),
    path('<int:pergunta_id>/editar_pergunta/', views.editar_pergunta, name='editar_pergunta'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path('criar/', views.criar_formulario, name='criar_formulario'),
    path('listar/', views.listar_formularios, name='listar_formularios'),
    path('<int:formulario_id>/perguntas/', views.criar_pergunta, name='criar_pergunta'),
]
