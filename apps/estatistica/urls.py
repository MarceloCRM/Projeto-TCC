from django.urls import path
from . import views

app_name = 'estatistica'

urlpatterns = [
    path('', views.index, name='index'),
]
