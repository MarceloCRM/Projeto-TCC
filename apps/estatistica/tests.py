import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.egresso.models import Egresso
from apps.formularios.models import Formulario, FormularioEgresso, Pergunta, Resposta


class PainelEstatisticaTests(TestCase):
    def test_painel_exibe_metricas_zeradas_sem_dados(self):
        response = self.client.get(reverse('estatistica:painel'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estatistica/painel.html')
        self.assertEqual(response.context['total_egressos'], 0)
        self.assertEqual(response.context['links_enviados'], 0)
        self.assertEqual(response.context['questionarios_respondidos'], 0)
        self.assertEqual(response.context['total_respostas'], 0)
        self.assertEqual(response.context['taxa_resposta'], 0)
        self.assertEqual(len(json.loads(response.context['labels_respostas'])), 30)
        self.assertFalse(response.context['possui_respostas_recentes'])

    def test_painel_agrega_dados_de_envio_resposta_e_curso(self):
        egresso_1 = Egresso.objects.create(
            nome_completo='Ana Silva',
            email='ana@example.com',
            whatsapp='11999999999',
            curso='Sistemas de Informacao',
            ano_conclusao=2023,
            status=Egresso.STATUS_ATIVO,
        )
        egresso_2 = Egresso.objects.create(
            nome_completo='Bruno Souza',
            email='bruno@example.com',
            whatsapp='11888888888',
            curso='Ciencia da Computacao',
            ano_conclusao=2022,
            status=Egresso.STATUS_ATIVO,
        )

        formulario_ativo = Formulario.objects.create(
            titulo='Pesquisa 2026',
            descricao='Acompanhamento anual',
            status=Formulario.STATUS_ATIVO,
        )
        Formulario.objects.create(
            titulo='Formulario inativo',
            descricao='Arquivo',
            status=Formulario.STATUS_INATIVO,
        )

        pergunta_escala = Pergunta.objects.create(
            formulario=formulario_ativo,
            texto='Como voce avalia o curso?',
            tipo=Pergunta.TIPO_ESCALA,
            ordem=1,
        )
        pergunta_texto = Pergunta.objects.create(
            formulario=formulario_ativo,
            texto='Conte sua experiencia profissional',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=2,
        )

        link_respondido = FormularioEgresso.objects.create(
            formulario=formulario_ativo,
            egresso=egresso_1,
            utilizado=True,
        )
        FormularioEgresso.objects.create(
            formulario=formulario_ativo,
            egresso=egresso_2,
            utilizado=False,
        )

        respondido_em = timezone.now()
        Resposta.objects.create(
            formulario_egresso=link_respondido,
            pergunta=pergunta_escala,
            valor='5',
            respondido_em=respondido_em,
        )
        Resposta.objects.create(
            formulario_egresso=link_respondido,
            pergunta=pergunta_texto,
            valor='Foi uma boa experiencia.',
            respondido_em=respondido_em,
        )

        response = self.client.get(reverse('estatistica:painel'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_egressos'], 2)
        self.assertEqual(response.context['questionarios_ativos'], 1)
        self.assertEqual(response.context['links_enviados'], 2)
        self.assertEqual(response.context['questionarios_respondidos'], 1)
        self.assertEqual(response.context['total_respostas'], 2)
        self.assertEqual(response.context['taxa_resposta'], 50.0)
        self.assertTrue(response.context['possui_respostas_recentes'])
        self.assertTrue(response.context['possui_ranking_formularios'])
        self.assertTrue(response.context['possui_cursos'])

        dados_respostas = json.loads(response.context['dados_respostas'])
        dados_cursos = json.loads(response.context['dados_cursos'])
        dados_formularios = json.loads(response.context['dados_formularios'])

        self.assertEqual(sum(dados_respostas), 1)
        self.assertEqual(sum(dados_cursos), 2)
        self.assertEqual(dados_formularios, [1])
