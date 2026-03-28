import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def pegar_url_formulario(token):
    base_url = settings.SITE_URL.rstrip('/')
    path = f'/formularios/responder/{token}/'
    print(path)
    return f'{base_url}{path}'


def enviar_formulario_whatsapp(egresso, link_formulario):
    try:
        from twilio.rest import Client

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_WHATSAPP_FROM:
            logger.error('Twilio credentials are not configured')
            return False, 'Credenciais do Twilio nao configuradas'

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        formulario_url = pegar_url_formulario(link_formulario.token)

        message_body = (
            f'Ola, {egresso.nome_completo}! Tudo bem?\n\n'
            f'A sua instituição gostaria de ouvir você. '
            f'Preparamos um formulário rápido para acompanhar a trajetoria dos nossos egressos, '
            f'e sua participação é muito importante.\n\n'
            f'Para responder, basta acessar o link abaixo:\n'
            f'{formulario_url}\n\n'
            f'Leva só alguns minutos.\n\n'
            f'Agradecemos muito pela sua colaboração!'
        )

        to_number = egresso.whatsapp
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=to_number,
            body=message_body,
        )

        logger.info(f'WhatsApp sent to {egresso.email}: SID {message.sid}')
        return True, message.sid

    except ImportError:
        logger.error('twilio package not installed')
        return False, 'Twilio not installed'

    except Exception as e:
        logger.error(f'WhatsApp error for {egresso.email}: {e}')
        return False, str(e)


def enviar_formulario_egresso(form, egresso_list, channels):
    """
    Send a survey to a list of egresso via selected channels.
    """
    from apps.formularios.models import RespostaFormulario

    results = {
        'total': len(egresso_list),
        'whatsapp_sent': 0,
        'email_sent': 0,
        'errors': []
    }

    for egresso in egresso_list:
        link_formulario, _ = RespostaFormulario.objects.get_or_create(
            formulario=form,
            egresso=egresso,
        )

        if 'whatsapp' in channels and egresso.whatsapp:
            success, msg = enviar_formulario_whatsapp(egresso, link_formulario)
            if success:
                results['whatsapp_sent'] += 1
            else:
                results['errors'].append(
                    f'WhatsApp to {egresso.nome_completo}: {msg}'
                )

        # if 'email' in channels and egresso.email:
        #     success, msg = send_email_survey(egresso, link_formulario, form)
        #     if success:
        #         results['email_sent'] += 1
        #     else:
        #         results['errors'].append(
        #             f"Email to {egresso.nome_completo}: {msg}"
        #         )

    return results
