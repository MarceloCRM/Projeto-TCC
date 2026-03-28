from django.urls import path

from apps.egresso.views import criar_egresso, detalhe_egresso, editar_egresso, listar_egresso

app_name = 'egresso'

urlpatterns = [
    path('listar_egresso/', listar_egresso, name='listar_egresso'),
    path('criar_egresso/', criar_egresso, name='criar_egresso'),
    path('editar_egresso/<int:pk>/', editar_egresso, name='editar_egresso'),
    path('detalhe_egresso/<int:pk>/', detalhe_egresso, name='detalhe_egresso'),
]
