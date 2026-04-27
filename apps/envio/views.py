from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.curso.models import Curso
from apps.formularios.models import Formulario
from apps.egresso.forms import EgressoFiltroForm
from apps.egresso.models import Egresso

from .services import enviar_formulario_egresso


def enviar_formulario(request):
    formularios = Formulario.objects.filter(status=Formulario.STATUS_ATIVO)
    egressos = Egresso.objects.select_related('curso').filter(status=Egresso.STATUS_ATIVO)
    form_filtro = EgressoFiltroForm(request.GET)
    cursos_disponiveis = Curso.objects.order_by('nome')
    cursos_selecionados = [
        curso_id for curso_id in request.GET.getlist('cursos') if curso_id.isdigit()
    ]
    formulario_id_get = request.GET.get('formulario_id')
    canais_get = request.GET.getlist('canais')

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

    if request.method == 'POST':
        formulario_id = request.POST.get('formulario_id')
        ids_egressos_selecionados = request.POST.getlist('ids_egressos')
        canais = request.POST.getlist('canais')

        if not formulario_id:
            messages.error(request, 'Selecione um questionário.')
            return redirect('envio:enviar_formulario')

        if not ids_egressos_selecionados:
            messages.error(request, 'Selecione pelo menos um egresso.')
            return redirect('envio:enviar_formulario')

        if not canais:
            messages.error(request, 'Selecione pelo menos um canal de envio.')
            return redirect('envio:enviar_formulario')

        formulario = get_object_or_404(Formulario, pk=formulario_id)
        egressos_selecionados = Egresso.objects.select_related('curso').filter(pk__in=ids_egressos_selecionados)

        resultados = enviar_formulario_egresso(
            formulario,
            egressos_selecionados,
            canais
        )

        messages.success(
            request,
            f'Questionário enviado! WhatsApp: {resultados["whatsapp_sent"]}, '
            f'Email: {resultados["email_sent"]} de {resultados["total"]} egressos.'
        )

        if resultados['errors']:
            for erro in resultados['errors'][:5]:
                messages.warning(request, erro)

        return redirect('envio:enviar_formulario')

    contexto = {
        'formularios': formularios,
        'egressos': egressos,
        'form_filtro': form_filtro,
        'cursos_disponiveis': cursos_disponiveis,
        'cursos_selecionados': cursos_selecionados,
        'formulario_id_get': formulario_id_get,
        'canais_get': canais_get,
    }

    return render(request, 'envio/enviar_formulario.html', contexto)
