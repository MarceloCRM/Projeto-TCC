from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.formularios.models import Formulario
from apps.egresso.models import Egresso

from .services import enviar_formulario_egresso


def enviar_formulario(request):
    formularios = Formulario.objects.all()
    egressos = Egresso.objects.all()

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
        egressos_selecionados = Egresso.objects.filter(pk__in=ids_egressos_selecionados)

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
    }

    return render(request, 'envio/enviar_formulario.html', contexto)