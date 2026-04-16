import json
from collections import Counter
from datetime import timedelta

from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from apps.egresso.models import Egresso
from apps.formularios.models import Formulario, FormularioEgresso, Pergunta, Resposta


def _calcular_percentual(parte, total):
    if not total:
        return 0
    return round((parte / total) * 100, 1)


def _formatar_percentual_css(valor):
    return f'{valor:.1f}'.rstrip('0').rstrip('.')


def index(request):
    hoje = timezone.localdate()
    inicio_periodo = hoje - timedelta(days=29)

    total_egressos = Egresso.objects.count()
    questionarios_ativos = Formulario.objects.filter(status=Formulario.STATUS_ATIVO).count()
    links_enviados = FormularioEgresso.objects.count()
    questionarios_respondidos = FormularioEgresso.objects.filter(respostas__isnull=False).distinct().count()
    total_respostas = Resposta.objects.count()
    taxa_resposta = _calcular_percentual(questionarios_respondidos, links_enviados)

    respostas_com_data = (
        FormularioEgresso.objects.filter(respostas__isnull=False)
        .annotate(ultima_resposta_em=Max('respostas__respondido_em'))
        .filter(
            ultima_resposta_em__date__gte=inicio_periodo,
            ultima_resposta_em__date__lte=hoje,
        )
        .values_list('ultima_resposta_em', flat=True)
    )

    respostas_por_data = Counter()
    for data_resposta in respostas_com_data:
        if not data_resposta:
            continue

        if timezone.is_aware(data_resposta):
            data_resposta = timezone.localtime(data_resposta)

        respostas_por_data[data_resposta.date()] += 1

    labels_respostas = []
    dados_respostas = []
    for deslocamento in range(30):
        data_atual = inicio_periodo + timedelta(days=deslocamento)
        labels_respostas.append(data_atual.strftime('%d/%m'))
        dados_respostas.append(respostas_por_data.get(data_atual, 0))

    cursos = (
        Egresso.objects.values('curso__nome')
        .annotate(total=Count('id'))
        .order_by('-total', 'curso__nome')[:8]
    )
    labels_cursos = [curso['curso__nome'] or 'Nao informado' for curso in cursos]
    dados_cursos = [curso['total'] for curso in cursos]

    formularios_populares = (
        Formulario.objects.annotate(
            total_respondidos=Count(
                'links',
                filter=Q(links__respostas__isnull=False),
                distinct=True,
            )
        )
        .filter(total_respondidos__gt=0)
        .order_by('-total_respondidos', 'titulo')[:6]
    )
    labels_formularios = [formulario.titulo for formulario in formularios_populares]
    dados_formularios = [
        formulario.total_respondidos for formulario in formularios_populares
    ]

    respostas_recentes = list(
        FormularioEgresso.objects.filter(respostas__isnull=False)
        .select_related('egresso__curso', 'formulario')
        .annotate(ultima_resposta_em=Max('respostas__respondido_em'))
        .order_by('-ultima_resposta_em')[:8]
    )

    context = {
        'total_egressos': total_egressos,
        'questionarios_ativos': questionarios_ativos,
        'links_enviados': links_enviados,
        'questionarios_respondidos': questionarios_respondidos,
        'total_respostas': total_respostas,
        'taxa_resposta': taxa_resposta,
        'labels_respostas': json.dumps(labels_respostas, ensure_ascii=False),
        'dados_respostas': json.dumps(dados_respostas),
        'labels_cursos': json.dumps(labels_cursos, ensure_ascii=False),
        'dados_cursos': json.dumps(dados_cursos),
        'labels_formularios': json.dumps(labels_formularios, ensure_ascii=False),
        'dados_formularios': json.dumps(dados_formularios),
        'labels_engajamento': json.dumps(['Respondidos', 'Pendentes']),
        'dados_engajamento': json.dumps(
            [
                questionarios_respondidos,
                max(links_enviados - questionarios_respondidos, 0),
            ]
        ),
        'respostas_recentes': respostas_recentes,
        'possui_respostas_recentes': bool(respostas_recentes),
        'possui_ranking_formularios': bool(dados_formularios),
        'possui_cursos': bool(dados_cursos),
    }
    return render(request, 'estatistica/index.html', context)


def lista_formularios(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    
    formularios = Formulario.objects.annotate(
        total_respostas=Count(
            'links',
            filter=Q(links__respostas__isnull=False),
            distinct=True,
        )
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
    total_respostas = (
        FormularioEgresso.objects.filter(
            formulario=formulario,
            respostas__isnull=False,
        )
        .distinct()
        .count()
    )
    
    # Total de perguntas
    perguntas = formulario.perguntas.all()
    total_perguntas = perguntas.count()
    
    # Perguntas obrigatórias e opcionais
    perguntas_obrigatorias = perguntas.filter(obrigatoria=True).count()
    perguntas_opcionais = perguntas.filter(obrigatoria=False).count()
    
    # Data da última resposta
    ultima_resposta = Resposta.objects.filter(
        formulario_egresso__formulario=formulario
    ).order_by('-respondido_em').first()

    # Processamento de estatísticas por pergunta
    estatisticas_perguntas = []
    
    for pergunta in perguntas:
        dados_pergunta = {
            'pergunta': pergunta,
            'total_respostas_pergunta': 0,
            'stats': {},
            'tem_respostas': False
        }
        
        respostas_qs = Resposta.objects.filter(pergunta=pergunta)
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
                    percentual = round(percentual, 1)
                    distribuicao.append({
                        'texto': opcao.texto,
                        'quantidade': count,
                        'percentual': percentual,
                        'percentual_css': _formatar_percentual_css(percentual),
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
                        percentual = round((count / len(valores) * 100), 1)
                        distribuicao[i] = {
                            'quantidade': count,
                            'percentual': percentual,
                            'percentual_css': _formatar_percentual_css(percentual),
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
                dados_pergunta['stats']['ultimas_respostas'] = respostas_qs.order_by('-respondido_em')[:5]
        
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


def listar_respostas_texto(request, formulario_id, pergunta_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    pergunta = get_object_or_404(
        Pergunta,
        id=pergunta_id,
        formulario=formulario,
        tipo=Pergunta.TIPO_TEXTO,
    )

    respostas = (
        Resposta.objects.filter(pergunta=pergunta)
        .select_related('formulario_egresso__egresso')
        .order_by('-respondido_em')
    )

    context = {
        'formulario': formulario,
        'pergunta': pergunta,
        'respostas': respostas,
        'total_respostas': respostas.count(),
    }
    return render(request, 'estatistica/listar_respostas_texto.html', context)
