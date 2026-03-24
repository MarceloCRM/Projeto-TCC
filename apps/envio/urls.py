from django.urls import path
from . import views

app_name = 'envio'

urlpatterns = [
    path('enviar/', views.enviar_formulario, name='enviar_formulario'),
]
