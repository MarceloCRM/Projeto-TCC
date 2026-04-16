from django.urls import path

from apps.curso.views import criar_curso, detalhe_curso, editar_curso, listar_curso

app_name = 'curso'

urlpatterns = [
    path('listar_curso/', listar_curso, name='listar_curso'),
    path('criar_curso/', criar_curso, name='criar_curso'),
    path('editar_curso/<int:pk>/', editar_curso, name='editar_curso'),
    path('detalhe_curso/<int:pk>/', detalhe_curso, name='detalhe_curso'),
]
