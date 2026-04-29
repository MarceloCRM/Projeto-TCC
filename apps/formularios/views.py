from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import FormularioFiltroForm, FormularioForm, PerguntaForm
from .models import Formulario, FormularioEgresso, Opcao, Pergunta, Resposta


def _get_valid_option_texts(option_values):
    return [texto.strip() for texto in option_values if texto.strip()]


def _validate_multiple_choice_options(form, option_count):
    if form.cleaned_data.get('tipo') == Pergunta.TIPO_ESCOLHA and option_count < 2:
        form.add_error(
            None,
            'Perguntas de múltipla escolha devem ter pelo menos duas opções de resposta.',
        )
        return False

    return True


def _get_submitted_answers(request, perguntas):
    respostas_enviadas = {}

    for pergunta in perguntas:
        valor = request.POST.get(f'pergunta_{pergunta.pk}', '')
        respostas_enviadas[pergunta.pk] = valor.strip() if isinstance(valor, str) else valor

    return respostas_enviadas


def _validate_required_answers(perguntas, respostas_enviadas):
    erros_pergunta = {}

    for pergunta in perguntas:
        valor = respostas_enviadas.get(pergunta.pk, '')
        if pergunta.obrigatoria and not valor:
            erros_pergunta[pergunta.pk] = 'Esta pergunta é obrigatória.'

    return erros_pergunta


def _apply_answer_state(perguntas, respostas_enviadas, erros_pergunta):
    for pergunta in perguntas:
        pergunta.resposta_enviada = respostas_enviadas.get(pergunta.pk, '')
        pergunta.erro_resposta = erros_pergunta.get(pergunta.pk, '')


def listar_formularios(request):
    formularios = Formulario.objects.all()
    form_filtro = FormularioFiltroForm(request.GET)

    if form_filtro.is_valid():
        busca = form_filtro.cleaned_data.get('busca')
        status = form_filtro.cleaned_data.get('status')
        criado_em = form_filtro.cleaned_data.get('criado_em')

        if busca:
            formularios = formularios.filter(
                Q(titulo__icontains=busca) |
                Q(descricao__icontains=busca)
            )

        if status:
            formularios = formularios.filter(status=status)

        if criado_em:
            formularios = formularios.filter(criado_em__date=criado_em)

    formularios = formularios.order_by('-criado_em')

    return render(request, 'formularios/listar_formularios.html', {
        'formularios': formularios,
        'form_filtro': form_filtro,
        'total': formularios.count(),
    })


def detalhe_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    perguntas = formulario.perguntas.all()
    total_perguntas = perguntas.count()

    return render(request, 'formularios/detalhe_formulario.html', {
        'formulario': formulario,
        'perguntas': perguntas,
        'total_perguntas': total_perguntas,
    })


def criar_formulario(request):
    if request.method == 'POST':
        form = FormularioForm(request.POST)
        if form.is_valid():
            formulario = form.save()
            return redirect('formularios:criar_pergunta', formulario_id=formulario.id)
    else:
        form = FormularioForm()

    return render(request, 'formularios/criar_formulario.html', {'form': form})


def editar_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    form_formulario = FormularioForm(instance=formulario)
    form_pergunta = PerguntaForm(formulario=formulario)

    if request.method == 'POST':
        if 'salvar_formulario' in request.POST:
            form_formulario = FormularioForm(request.POST, instance=formulario)
            if form_formulario.is_valid():
                form_formulario.save()
                return redirect('formularios:editar_formulario', formulario_id=formulario.id)

        elif 'salvar_pergunta' in request.POST:
            form_pergunta = PerguntaForm(request.POST, formulario=formulario)
            if form_pergunta.is_valid():
                opcoes = _get_valid_option_texts(request.POST.getlist('opcoes'))
                if not _validate_multiple_choice_options(form_pergunta, len(opcoes)):
                    perguntas = formulario.perguntas.all()
                    return render(request, 'formularios/editar_formulario.html', {
                        'formulario': formulario,
                        'form_formulario': form_formulario,
                        'form_pergunta': form_pergunta,
                        'perguntas': perguntas,
                    })

                pergunta = form_pergunta.save(commit=False)
                pergunta.formulario = formulario
                pergunta.save()

                if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                    for texto in opcoes:
                        Opcao.objects.create(
                            pergunta=pergunta,
                            texto=texto,
                        )

                return redirect('formularios:editar_formulario', formulario_id=formulario.id)

    perguntas = formulario.perguntas.all()

    return render(request, 'formularios/editar_formulario.html', {
        'formulario': formulario,
        'form_formulario': form_formulario,
        'form_pergunta': form_pergunta,
        'perguntas': perguntas,
    })


def criar_pergunta(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    if request.method == 'POST':
        form = PerguntaForm(request.POST, formulario=formulario)
        if form.is_valid():
            opcoes = _get_valid_option_texts(request.POST.getlist('opcoes'))
            if not _validate_multiple_choice_options(form, len(opcoes)):
                return render(request, 'formularios/criar_pergunta.html', {
                    'form': form,
                    'formulario': formulario,
                })

            pergunta = form.save(commit=False)
            pergunta.formulario = formulario
            pergunta.save()

            if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                for texto in opcoes:
                    Opcao.objects.create(
                        pergunta=pergunta,
                        texto=texto,
                    )

            return redirect('formularios:criar_pergunta', formulario_id=formulario.id)
    else:
        form = PerguntaForm(formulario=formulario)

    return render(request, 'formularios/criar_pergunta.html', {
        'form': form,
        'formulario': formulario,
    })


def editar_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    formulario = pergunta.formulario

    if request.method == 'POST':
        form = PerguntaForm(request.POST, instance=pergunta, formulario=formulario)

        if form.is_valid():
            novas_opcoes = _get_valid_option_texts(request.POST.getlist('novas_opcoes'))
            opcoes_existentes = pergunta.opcoes.count() if pergunta.tipo == Pergunta.TIPO_ESCOLHA else 0

            if form.cleaned_data.get('tipo') == Pergunta.TIPO_ESCOLHA and pergunta.tipo != Pergunta.TIPO_ESCOLHA:
                opcoes_existentes = 0

            if not _validate_multiple_choice_options(form, opcoes_existentes + len(novas_opcoes)):
                return render(request, 'formularios/editar_pergunta.html', {
                    'form': form,
                    'formulario': formulario,
                    'pergunta': pergunta,
                })

            pergunta = form.save()
            if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                opcao_ids = request.POST.getlist('opcao_id')

                for opcao_id in opcao_ids:
                    texto = request.POST.get(f'opcao_texto_{opcao_id}')
                    if texto:
                        Opcao.objects.filter(
                            id=opcao_id,
                            pergunta=pergunta,
                        ).update(texto=texto)

                for texto in novas_opcoes:
                    Opcao.objects.create(
                        pergunta=pergunta,
                        texto=texto,
                    )

            return redirect('formularios:editar_formulario', formulario_id=formulario.id)
    else:
        form = PerguntaForm(instance=pergunta, formulario=formulario)

    return render(request, 'formularios/editar_pergunta.html', {
        'form': form,
        'formulario': formulario,
        'pergunta': pergunta,
    })


def responder_questionario(request, token):
    link = get_object_or_404(FormularioEgresso, token=token)

    if link.utilizado:
        return render(request, 'formularios/ja_respondido.html', {'link': link})

    formulario = link.formulario
    perguntas = formulario.perguntas.prefetch_related('opcoes').all()

    if request.method == 'POST':
        respostas_enviadas = _get_submitted_answers(request, perguntas)
        erros_pergunta = _validate_required_answers(perguntas, respostas_enviadas)
        _apply_answer_state(perguntas, respostas_enviadas, erros_pergunta)

        if erros_pergunta:
            return render(request, 'formularios/responder.html', {
                'formulario': formulario,
                'perguntas': perguntas,
                'egresso': link.egresso,
                'erro_formulario': 'Responda todas as perguntas obrigatórias antes de enviar.',
            })

        respondido_em = timezone.now()
        link.respostas.all().delete()

        for pergunta in perguntas:
            valor = respostas_enviadas.get(pergunta.pk, '')
            if valor:
                Resposta.objects.create(
                    formulario_egresso=link,
                    pergunta=pergunta,
                    valor=valor,
                    respondido_em=respondido_em,
                )

        link.utilizado = True
        link.save(update_fields=['utilizado'])

        return redirect('formularios:obrigado')

    _apply_answer_state(perguntas, {}, {})

    return render(request, 'formularios/responder.html', {
        'formulario': formulario,
        'perguntas': perguntas,
        'egresso': link.egresso,
    })


def obrigado(request):
    return render(request, 'formularios/obrigado.html')
