from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FormularioForm, PerguntaForm
from .models import Alternativa, Formulario, Opcao, Pergunta, Resposta, RespostaFormulario


def criar_pergunta(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    if request.method == 'POST':
        form = PerguntaForm(request.POST)
        if form.is_valid():
            pergunta = form.save(commit=False)
            pergunta.formulario = formulario
            pergunta.save()

            if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                opcoes = request.POST.getlist('opcoes')
                for texto in opcoes:
                    if texto.strip():
                        Opcao.objects.create(
                            pergunta=pergunta,
                            texto=texto,
                        )

            return redirect('formularios:criar_pergunta', formulario_id=formulario.id)
    else:
        form = PerguntaForm()

    return render(request, 'formularios/criar_pergunta.html', {
        'form': form,
        'formulario': formulario,
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


def listar_formularios(request):
    formularios = Formulario.objects.all()
    return render(request, 'formularios/listar_formularios.html', {'formularios': formularios})


def obrigado(request):
    return render(request, 'formularios/obrigado.html')


# def responder_formulario(request, formulario_id):
#     formulario = get_object_or_404(Formulario, id=formulario_id)
#     perguntas = formulario.perguntas.all()

#     if request.method == 'POST':
#         form = FormularioDinamico(request.POST, perguntas=perguntas)

#         if form.is_valid():
#             egresso = form.cleaned_data['egresso']
#             resposta_form = RespostaFormulario.objects.create(
#                 formulario=formulario,
#                 egresso=egresso,
#             )

#             for pergunta in perguntas:
#                 field_name = f'pergunta_{pergunta.id}'
#                 valor = form.cleaned_data.get(field_name)

#                 Alternativa.objects.create(
#                     resposta=Resposta.objects.get_or_create(
#                         formulario=formulario,
#                         egresso=egresso,
#                     )[0],
#                     pergunta=pergunta,
#                     valor=str(valor) if valor is not None else '',
#                 )

#             resposta_form.utilizado = True
#             resposta_form.save(update_fields=['utilizado'])

#             return redirect('formularios:obrigado')
#     else:
#         form = FormularioDinamico(perguntas=perguntas)

#     return render(request, 'formularios/responder_simples.html', {
#         'formulario': formulario,
#         'form': form,
#     })


def estatisticas_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    estatisticas = []

    for pergunta in formulario.perguntas.all():
        respostas_pergunta = Alternativa.objects.filter(
            resposta__formulario=formulario,
            pergunta=pergunta,
        )
        total_respostas = respostas_pergunta.count()

        if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
            dados = (
                respostas_pergunta
                .values('valor')
                .annotate(total=Count('id'))
            )

            for dado in dados:
                dado['porcentagem'] = (dado['total'] / total_respostas * 100) if total_respostas > 0 else 0
                dado['valor_opcao__texto'] = dado['valor']

            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'escolha',
                'dados': dados,
                'total_geral': total_respostas,
            })

        elif pergunta.tipo == Pergunta.TIPO_NUMERO:
            valores = [float(item.valor) for item in respostas_pergunta if item.valor not in ('', None)]
            media = sum(valores) / len(valores) if valores else None
            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'numero',
                'media': media,
                'total_geral': total_respostas,
            })

        elif pergunta.tipo == Pergunta.TIPO_ESCALA:
            contagens = {}
            for item in respostas_pergunta:
                if item.valor not in ('', None):
                    nota = float(item.valor)
                    contagens[nota] = contagens.get(nota, 0) + 1

            dados = []
            for nota in sorted(contagens.keys()):
                total = contagens[nota]
                dados.append({
                    'valor_numero': nota,
                    'total': total,
                    'porcentagem': (total / total_respostas * 100) if total_respostas > 0 else 0,
                })

            media = (
                sum(float(item.valor) for item in respostas_pergunta if item.valor not in ('', None)) / total_respostas
                if total_respostas > 0 else None
            )

            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'escala',
                'dados': dados,
                'media': media,
                'total_geral': total_respostas,
            })

        elif pergunta.tipo == Pergunta.TIPO_TEXTO:
            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'texto',
                'total': total_respostas,
                'total_geral': total_respostas,
            })

    total_envios = formulario.respostas.count()

    return render(request, 'formularios/estatisticas.html', {
        'formulario': formulario,
        'estatisticas': estatisticas,
        'total_envios': total_envios,
    })


def editar_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    form_formulario = FormularioForm(instance=formulario)
    form_pergunta = PerguntaForm()

    if request.method == 'POST':
        if 'salvar_formulario' in request.POST:
            form_formulario = FormularioForm(request.POST, instance=formulario)
            if form_formulario.is_valid():
                form_formulario.save()
                return redirect('formularios:editar_formulario', formulario_id=formulario.id)

        elif 'salvar_pergunta' in request.POST:
            form_pergunta = PerguntaForm(request.POST)
            if form_pergunta.is_valid():
                pergunta = form_pergunta.save(commit=False)
                pergunta.formulario = formulario
                pergunta.save()

                if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                    opcoes = request.POST.getlist('opcoes')
                    for texto in opcoes:
                        if texto.strip():
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


def editar_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    formulario = pergunta.formulario

    if request.method == 'POST':
        form = PerguntaForm(request.POST, instance=pergunta)

        if form.is_valid():
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

                novas_opcoes = request.POST.getlist('novas_opcoes')

                for texto in novas_opcoes:
                    if texto.strip():
                        Opcao.objects.create(
                            pergunta=pergunta,
                            texto=texto,
                        )

            return redirect('formularios:editar_formulario', formulario_id=formulario.id)
    else:
        form = PerguntaForm(instance=pergunta)

    return render(request, 'formularios/editar_pergunta.html', {
        'form': form,
        'formulario': formulario,
        'pergunta': pergunta,
    })


def responder_questionario(request, token):
    link = get_object_or_404(RespostaFormulario, token=token)

    if link.utilizado:
        return render(request, 'formularios/ja_respondido.html', {'link': link})

    formulario = link.formulario
    perguntas = formulario.perguntas.prefetch_related('opcoes').all()

    if request.method == 'POST':
        resposta, _ = Resposta.objects.get_or_create(
            formulario=formulario,
            egresso=link.egresso,
        )

        resposta.alternativas.all().delete()

        for pergunta in perguntas:
            valor = request.POST.get(f'pergunta_{pergunta.pk}', '').strip()
            if valor:
                Alternativa.objects.create(
                    resposta=resposta,
                    pergunta=pergunta,
                    valor=valor,
                )

        link.utilizado = True
        link.save(update_fields=['utilizado'])

        return redirect('formularios:obrigado')

    return render(request, 'formularios/responder.html', {
        'formulario': formulario,
        'perguntas': perguntas,
        'egresso': link.egresso,
    })
