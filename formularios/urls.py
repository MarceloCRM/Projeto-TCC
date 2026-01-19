from django.urls import path
from . import views

urlpatterns = [
    path('<int:formulario_id>/responder/', views.responder_formulario, name='responder'),
    path('<int:formulario_id>/estatisticas/', views.estatisticas_formulario, name='estatisticas'),
    path('sucesso/', views.sucesso, name='sucesso'),
]
