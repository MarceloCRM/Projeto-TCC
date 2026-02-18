from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg
from .models import (
    Formulario,
    Pergunta,
    RespostaFormulario,
    Resposta, 
    Opcao
)
from .forms import FormularioDinamico, FormularioForm, PerguntaForm, OpcaoForm

def criar_pergunta(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    if request.method == 'POST':
        form = PerguntaForm(request.POST)
        if form.is_valid():
            pergunta = form.save(commit=False)
            pergunta.formulario = formulario
            pergunta.save()

            if pergunta.tipo == 'escolha':
                opcoes = request.POST.getlist('opcoes')
                for texto in opcoes:
                    if texto.strip():
                        Opcao.objects.create(
                            pergunta=pergunta,
                            texto=texto
                        )

            return redirect('formularios:criar_pergunta', formulario_id=formulario.id)
    else:
        form = PerguntaForm()

    return render(request, 'formularios/criar_pergunta.html', {
        'form': form,
        'formulario': formulario
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

def sucesso(request):
    return render(request, 'formularios/sucesso.html')

def responder_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    perguntas = formulario.perguntas.all()

    if request.method == 'POST':
        form = FormularioDinamico(request.POST, perguntas=perguntas)

        if form.is_valid():
            resposta_form = RespostaFormulario.objects.create(
                formulario=formulario
            )

            for pergunta in perguntas:
                field_name = f'pergunta_{pergunta.id}'
                valor = form.cleaned_data.get(field_name)

                Resposta.objects.create(
                    resposta_formulario=resposta_form,
                    pergunta=pergunta,
                    valor_texto=valor if pergunta.tipo == Pergunta.TIPO_TEXTO else None,
                    valor_numero=valor if pergunta.tipo == Pergunta.TIPO_NUMERO else None,
                    valor_opcao_id=valor if pergunta.tipo == Pergunta.TIPO_ESCOLHA else None,
                )

            return redirect('formularios:sucesso')

    else:
        form = FormularioDinamico(perguntas=perguntas)

    return render(request, 'formularios/responder.html', {
        'formulario': formulario,
        'form': form
    })

def estatisticas_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    estatisticas = []

    for pergunta in formulario.perguntas.all():

        if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
            dados = (
                Resposta.objects
                .filter(pergunta=pergunta)
                .values('valor_opcao__texto')
                .annotate(total=Count('id'))
            )

            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'escolha',
                'dados': dados
            })

        elif pergunta.tipo == Pergunta.TIPO_NUMERO:
            media = (
                Resposta.objects
                .filter(pergunta=pergunta)
                .aggregate(media=Avg('valor_numero'))
            )

            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'numero',
                'media': media['media']
            })

        elif pergunta.tipo == Pergunta.TIPO_BOOLEANO:
            dados = (
                Resposta.objects
                .filter(pergunta=pergunta)
                .values('valor_numero')
                .annotate(total=Count('id'))
            )

            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'booleano',
                'dados': dados
            })

        elif pergunta.tipo == Pergunta.TIPO_TEXTO:
            total = Resposta.objects.filter(pergunta=pergunta).count()

            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'texto',
                'total': total
            })

    return render(request, 'formularios/estatisticas.html', { 'formulario': formulario, 'estatisticas': estatisticas })

def editar_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    form_formulario = FormularioForm(instance=formulario)
    form_pergunta = PerguntaForm()

    if request.method == 'POST':

        # Atualizar dados do formulário
        if 'salvar_formulario' in request.POST:
            form_formulario = FormularioForm(
                request.POST, instance=formulario
            )
            if form_formulario.is_valid():
                form_formulario.save()
                return redirect('formularios:editar_formulario', formulario_id=formulario.id)

        # Criar nova pergunta
        elif 'salvar_pergunta' in request.POST:
            form_pergunta = PerguntaForm(request.POST)
            if form_pergunta.is_valid():
                pergunta = form_pergunta.save(commit=False)
                pergunta.formulario = formulario
                pergunta.save()

                if pergunta.tipo == 'multipla':
                    opcoes = request.POST.getlist('opcoes')
                    for texto in opcoes:
                        if texto.strip():
                            Opcao.objects.create(
                                pergunta=pergunta,
                                texto=texto
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
            if pergunta.tipo == 'escolha':
                opcao_ids = request.POST.getlist('opcao_id')

                for opcao_id in opcao_ids:
                    texto = request.POST.get(f'opcao_texto_{opcao_id}')
                    if texto:
                        Opcao.objects.filter(
                            id=opcao_id,
                            pergunta=pergunta
                        ).update(texto=texto)

                novas_opcoes = request.POST.getlist('novas_opcoes')

                for texto in novas_opcoes:
                    if texto.strip():
                        Opcao.objects.create(
                            pergunta=pergunta,
                            texto=texto
                        )

            return redirect(
                'formularios:editar_formulario',
                formulario_id=formulario.id
            )
    else:
        form = PerguntaForm(instance=pergunta)

    return render(request, 'formularios/editar_pergunta.html', {
        'form': form,
        'formulario': formulario,
        'pergunta': pergunta
    })

