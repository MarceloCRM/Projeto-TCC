from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg
from .models import (
    Formulario,
    Pergunta,
    RespostaFormulario,
    Resposta
)
from .forms import FormularioDinamico

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

            return redirect('sucesso')

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

        # Múltipla escolha
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

        # Número (média)
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

        # Booleano (sim / não)
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

        # Texto (contagem simples)
        elif pergunta.tipo == Pergunta.TIPO_TEXTO:
            total = Resposta.objects.filter(pergunta=pergunta).count()

            estatisticas.append({
                'pergunta': pergunta.texto,
                'tipo': 'texto',
                'total': total
            })

    return render(request, 'formularios/estatisticas.html', {
        'formulario': formulario,
        'estatisticas': estatisticas
    })



def sucesso(request):
    return render(request, 'formularios/sucesso.html')
