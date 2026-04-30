from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from apps.core.decorators import role_admin_required
from apps.curso.models import Curso
from apps.egresso.forms import EgressoFiltroForm, EgressoForm
from apps.egresso.models import Egresso

@login_required
def listar_egresso(request):
    egressos = Egresso.objects.select_related('curso').all().order_by('-criado_em')
    form_filtro = EgressoFiltroForm(request.GET)
    cursos_disponiveis = Curso.objects.order_by('nome')
    cursos_selecionados = [
        curso_id for curso_id in request.GET.getlist('cursos') if curso_id.isdigit()
    ]

    if form_filtro.is_valid():
        busca = form_filtro.cleaned_data.get('busca')
        ano = form_filtro.cleaned_data.get('ano_conclusao')
        status = form_filtro.cleaned_data.get('status')

        if busca:
            egressos = egressos.filter(
                Q(nome_completo__icontains=busca) |
                Q(email__icontains=busca) |
                Q(curso__nome__icontains=busca)
            )

        if cursos_selecionados:
            egressos = egressos.filter(curso_id__in=cursos_selecionados)

        if ano:
            egressos = egressos.filter(ano_conclusao=ano)

        if status:
            egressos = egressos.filter(status=status)

    context = {
        'egressos': egressos,
        'form_filtro': form_filtro,
        'cursos_disponiveis': cursos_disponiveis,
        'cursos_selecionados': cursos_selecionados,
        'total': egressos.count(),
    }

    return render(request, 'egresso/listar_egresso.html', context)

@role_admin_required
def criar_egresso(request):
    if request.method == 'POST':
        form = EgressoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('egresso:listar_egresso')
    else:
        form = EgressoForm()

    return render(request, template_name='egresso/criar_egresso.html', context={'form': form})

@role_admin_required
def editar_egresso(request, pk):
    egresso = get_object_or_404(Egresso.objects.select_related('curso'), pk=pk)

    if request.method == 'POST':
        form = EgressoForm(request.POST, instance=egresso)
        if form.is_valid():
            form.save()
            return redirect('egresso:listar_egresso')
    else:
        form = EgressoForm(instance=egresso)

    context = {
        'form': form,
        'egressos': egresso,
    }

    return render(request, template_name='egresso/editar_egresso.html', context=context)

@login_required
def detalhe_egresso(request, pk):
    egresso = get_object_or_404(Egresso.objects.select_related('curso'), pk=pk)

    # Buscar links de formulários do egresso
    links = egresso.links.select_related('formulario').prefetch_related('respostas').order_by('-criado_em')

    total_formularios = links.count()
    respondidos = links.filter(utilizado=True).count()
    pendentes = total_formularios - respondidos
    
    taxa_resposta = 0
    if total_formularios > 0:
        taxa_resposta = int((respondidos / total_formularios) * 100)

    context = {
        'egresso': egresso,
        'links': links,
        'total_formularios': total_formularios,
        'respondidos': respondidos,
        'pendentes': pendentes,
        'taxa_resposta': taxa_resposta,
    }

    return render(
        request,
        template_name='egresso/detalhe_egresso.html',
        context=context,
    )
