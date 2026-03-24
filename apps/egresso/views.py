from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from apps.egresso.forms import EgressoForm, EgressoFiltroForm
from apps.egresso.models import Egresso


def listar_egresso(request):
    egressos = Egresso.objects.all().order_by('-criado_em')

    form_filtro = EgressoFiltroForm(request.GET)

    if form_filtro.is_valid():
        busca = form_filtro.cleaned_data.get('busca')
        curso = form_filtro.cleaned_data.get('curso')
        ano = form_filtro.cleaned_data.get('ano_conclusao')
        situacao = form_filtro.cleaned_data.get('situacao_profissional')

        if busca:
            egressos = egressos.filter(
                Q(nome_completo__icontains=busca) |
                Q(email__icontains=busca) |
                Q(curso__icontains=busca)
            )

        if curso:
            egressos = egressos.filter(curso__icontains=curso)

        if ano:
            egressos = egressos.filter(ano_conclusao=ano)

        if situacao:
            egressos = egressos.filter(situacao_profissional=situacao)

    context = {
        'egressos': egressos,
        'form_filtro': form_filtro,
        'total': egressos.count()
    }

    return render(request, 'egresso/listar_egresso.html', context)

def criar_egresso(request):
    if request.method == "POST":
        form = EgressoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('egresso:listar_egresso')
    else:
        form = EgressoForm()

    return render(request, template_name="egresso/criar_egresso.html", context={"form": form})

def editar_egresso(request, pk):
    egresso = get_object_or_404(Egresso, pk=pk)
    if request.method == "POST":
        form = EgressoForm(request.POST, instance=egresso)
        if form.is_valid():
            form.save()
            return redirect('egresso:listar_egresso')
    else:
        form = EgressoForm(instance=egresso)
    
    context = {
        "form" : form,
        "egressos": egresso
    }

    return render(request, template_name="egresso/editar_egresso.html", context=context)

def excluir_egresso(request, pk):
    egresso = get_object_or_404(Egresso, pk=pk)

    if request.method == "POST":
        egresso.delete()
        return redirect('egresso:listar_egresso')

    return render(
        request,
        template_name="egresso/confirmar_exclusao.html",
        context={"egresso": egresso},
    )

def detalhe_egresso(request, pk):
    egresso = get_object_or_404(Egresso, pk=pk)

    return render(
        request,
        template_name="egresso/detalhe_egresso.html",
        context={"egresso": egresso},
    )
