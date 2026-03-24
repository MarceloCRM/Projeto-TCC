from django.contrib import admin
from django.urls import path, include
from apps.egresso.views import listar_egresso, criar_egresso, editar_egresso, excluir_egresso, detalhe_egresso

app_name = "egresso"

urlpatterns = [
    path('listar_egresso/', listar_egresso, name='listar_egresso'),
    path('criar_egresso/', criar_egresso, name='criar_egresso'),
    path('editar_egresso/<int:pk>/', editar_egresso, name='editar_egresso'),
    path('excluir_egresso/<int:pk>/', excluir_egresso, name='excluir_egresso'),
    path('detalhe_egresso/<int:pk>/', detalhe_egresso, name='detalhe_egresso')

]