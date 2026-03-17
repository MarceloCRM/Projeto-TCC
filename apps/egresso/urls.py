from django.contrib import admin
from django.urls import path, include
from apps.egresso.views import listar_egresso, new_egresso

app_name = "egresso"

urlpatterns = [
    path('listar_egresso/', listar_egresso, name='listar_egresso'),
    # path('new_egresso/', new_egresso, name='new_egresso'),

]