from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from apps.core.decorators import role_admin_required
from apps.curso.forms import CursoFiltroForm, CursoForm
from apps.curso.models import Curso

@login_required
def listar_curso(request):
    cursos = Curso.objects.annotate(total_egressos=Count('egressos', distinct=True)).order_by('-criado_em')
    form_filtro = CursoFiltroForm(request.GET)

    if form_filtro.is_valid():
        busca = form_filtro.cleaned_data.get('busca')
        criado_em = form_filtro.cleaned_data.get('criado_em')
        status = form_filtro.cleaned_data.get('status')

        if busca:
            cursos = cursos.filter(nome__icontains=busca)

        if criado_em:
            cursos = cursos.filter(criado_em__date=criado_em)

        if status:
            cursos = cursos.filter(status=status)

    context = {
        'cursos': cursos,
        'form_filtro': form_filtro,
        'total': cursos.count(),
    }

    return render(request, 'curso/listar_curso.html', context)

@role_admin_required
def criar_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('curso:listar_curso')
    else:
        form = CursoForm()

    return render(request, 'curso/criar_curso.html', {'form': form})

@role_admin_required
def editar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            return redirect('curso:listar_curso')
    else:
        form = CursoForm(instance=curso)

    context = {
        'form': form,
        'curso': curso,
        'total_egressos': curso.egressos.count(),
    }

    return render(request, 'curso/editar_curso.html', context)

@login_required
def detalhe_curso(request, pk):
    curso = get_object_or_404(
        Curso.objects.annotate(total_egressos=Count('egressos', distinct=True)),
        pk=pk,
    )
    egressos = curso.egressos.all().order_by('-criado_em', 'nome_completo')

    context = {
        'curso': curso,
        'egressos': egressos,
        'possui_egressos': curso.total_egressos > 0,
    }

    return render(request, 'curso/detalhe_curso.html', context)
