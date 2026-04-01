from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Max, Min, Q
from apps.formularios.models import Formulario, Pergunta, Resposta, RespostaPergunta, Opcao

def index(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    
    formularios = Formulario.objects.annotate(
        total_respostas=Count('links__resposta', distinct=True)
    )

    if query:
        formularios = formularios.filter(
            Q(titulo__icontains=query) | Q(descricao__icontains=query)
        )
    
    if status_filter:
        formularios = formularios.filter(status=status_filter)

    formularios = formularios.order_by('-criado_em')

    context = {
        'formularios': formularios,
    }
    return render(request, 'estatistica/lista_formularios.html', context)

def detalhe_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    
    # Total de respostas enviadas
    total_respostas = Resposta.objects.filter(resposta_formulario__formulario=formulario).count()
    
    # Total de perguntas
    perguntas = formulario.perguntas.all()
    total_perguntas = perguntas.count()
    
    # Perguntas obrigatórias e opcionais
    perguntas_obrigatorias = perguntas.filter(obrigatoria=True).count()
    perguntas_opcionais = perguntas.filter(obrigatoria=False).count()
    
    # Data da última resposta
    ultima_resposta = Resposta.objects.filter(
        resposta_formulario__formulario=formulario
    ).order_by('-enviado_em').first()

    # Processamento de estatísticas por pergunta
    estatisticas_perguntas = []
    
    for pergunta in perguntas:
        dados_pergunta = {
            'pergunta': pergunta,
            'total_respostas_pergunta': 0,
            'stats': {},
            'tem_respostas': False
        }
        
        respostas_qs = RespostaPergunta.objects.filter(pergunta=pergunta)
        dados_pergunta['total_respostas_pergunta'] = respostas_qs.count()
        
        if dados_pergunta['total_respostas_pergunta'] > 0:
            dados_pergunta['tem_respostas'] = True
            
            if pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                # Contagem por opção
                opcoes = pergunta.opcoes.all()
                distribuicao = []
                for opcao in opcoes:
                    count = respostas_qs.filter(valor=opcao.texto).count()
                    percentual = (count / dados_pergunta['total_respostas_pergunta'] * 100) if dados_pergunta['total_respostas_pergunta'] > 0 else 0
                    distribuicao.append({
                        'texto': opcao.texto,
                        'quantidade': count,
                        'percentual': round(percentual, 1)
                    })
                dados_pergunta['stats']['distribuicao'] = distribuicao
                
            elif pergunta.tipo == Pergunta.TIPO_ESCALA:
                # Média e distribuição
                valores = [int(r.valor) for r in respostas_qs if r.valor.isdigit()]
                if valores:
                    dados_pergunta['stats']['media'] = round(sum(valores) / len(valores), 2)
                    distribuicao = {}
                    for i in range(1, 6):
                        count = valores.count(i)
                        percentual = (count / len(valores) * 100)
                        distribuicao[i] = {
                            'quantidade': count,
                            'percentual': round(percentual, 1)
                        }
                    dados_pergunta['stats']['distribuicao'] = distribuicao

            elif pergunta.tipo == Pergunta.TIPO_NUMERO:
                # Média, Min, Max
                valores = []
                for r in respostas_qs:
                    try:
                        valores.append(float(r.valor.replace(',', '.')))
                    except ValueError:
                        continue
                
                if valores:
                    dados_pergunta['stats']['media'] = round(sum(valores) / len(valores), 2)
                    dados_pergunta['stats']['min'] = min(valores)
                    dados_pergunta['stats']['max'] = max(valores)
                    
            elif pergunta.tipo == Pergunta.TIPO_TEXTO:
                # Lista de respostas recentes
                dados_pergunta['stats']['ultimas_respostas'] = respostas_qs.order_by('-resposta__enviado_em')[:5]
        
        estatisticas_perguntas.append(dados_pergunta)

    context = {
        'formulario': formulario,
        'total_respostas': total_respostas,
        'total_perguntas': total_perguntas,
        'perguntas_obrigatorias': perguntas_obrigatorias,
        'perguntas_opcionais': perguntas_opcionais,
        'ultima_resposta': ultima_resposta,
        'estatisticas_perguntas': estatisticas_perguntas,
    }
    return render(request, 'estatistica/detalhe_formulario.html', context)
