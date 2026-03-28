from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FormularioFiltroForm, FormularioForm, PerguntaForm
from .models import Formulario, Opcao, Pergunta, Resposta, RespostaFormulario, RespostaPergunta


def listar_formularios(request):
    formularios = Formulario.objects.all().order_by('-criado_em')
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

    return render(request, 'formularios/listar_formularios.html', {
        'formularios': formularios,
        'form_filtro': form_filtro,
        'total': formularios.count(),
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

def estatisticas_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    estatisticas = []

    for pergunta in formulario.perguntas.all():
        # Caminho ORM: RespostaPergunta -> Resposta -> RespostaFormulario -> Formulario.
        respostas_pergunta = RespostaPergunta.objects.filter(
            resposta__resposta_formulario__formulario=formulario,
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

    # Conta Resposta vinculada a RespostaFormulario do formulario atual.
    total_envios = Resposta.objects.filter(
        resposta_formulario__formulario=formulario,
    ).count()

    return render(request, 'formularios/estatisticas.html', {
        'formulario': formulario,
        'estatisticas': estatisticas,
        'total_envios': total_envios,
    })


def responder_questionario(request, token):
    link = get_object_or_404(RespostaFormulario, token=token)

    if link.utilizado:
        return render(request, 'formularios/ja_respondido.html', {'link': link})

    formulario = link.formulario
    perguntas = formulario.perguntas.prefetch_related('opcoes').all()

    if request.method == 'POST':
        resposta, _ = Resposta.objects.get_or_create(
            resposta_formulario=link,
        )

        resposta.alternativas.all().delete()

        for pergunta in perguntas:
            valor = request.POST.get(f'pergunta_{pergunta.pk}', '').strip()
            if valor:
                RespostaPergunta.objects.create(
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


def obrigado(request):
    return render(request, 'formularios/obrigado.html')
