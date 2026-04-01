from django.urls import path
from . import views

app_name = 'formularios'

urlpatterns = [
    path('<int:formulario_id>/editar_formulario/', views.editar_formulario, name='editar_formulario'),
    path('<int:pergunta_id>/editar_pergunta/', views.editar_pergunta, name='editar_pergunta'),
    path('criar/', views.criar_formulario, name='criar_formulario'),
    path('listar/', views.listar_formularios, name='listar_formularios'),
    path('<int:formulario_id>/perguntas/', views.criar_pergunta, name='criar_pergunta'),
    path('responder/<uuid:token>/', views.responder_questionario, name='responder'),
    path('obrigado/', views.obrigado, name='obrigado'),
]
