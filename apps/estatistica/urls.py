from django.urls import path
from . import views

app_name = 'estatistica'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:formulario_id>/', views.detalhe_formulario, name='detalhe_formulario'),
]
