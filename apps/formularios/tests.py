from django.test import TestCase
from django.urls import reverse

from apps.curso.models import Curso
from apps.egresso.models import Egresso

from .models import Formulario, FormularioEgresso, Opcao, Pergunta, Resposta


class PerguntaObrigatoriaTests(TestCase):
    def setUp(self):
        self.formulario = Formulario.objects.create(
            titulo='Pesquisa de acompanhamento',
            descricao='Formulario de teste',
            status=Formulario.STATUS_ATIVO,
        )

    def test_bloqueia_primeira_pergunta_opcional_na_criacao(self):
        response = self.client.post(
            reverse('formularios:criar_pergunta', args=[self.formulario.id]),
            data={
                'texto': 'Como avalia o curso?',
                'tipo': Pergunta.TIPO_TEXTO,
                'ordem': 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'O formulário precisa ter pelo menos uma pergunta obrigatória.',
        )
        self.assertEqual(self.formulario.perguntas.count(), 0)

    def test_permite_criar_pergunta_opcional_quando_ja_existe_uma_obrigatoria(self):
        Pergunta.objects.create(
            formulario=self.formulario,
            texto='Pergunta obrigatória',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=1,
            obrigatoria=True,
        )

        response = self.client.post(
            reverse('formularios:criar_pergunta', args=[self.formulario.id]),
            data={
                'texto': 'Pergunta opcional',
                'tipo': Pergunta.TIPO_TEXTO,
                'ordem': 2,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.formulario.perguntas.count(), 2)
        self.assertTrue(self.formulario.perguntas.filter(obrigatoria=True).exists())

    def test_bloqueia_edicao_da_ultima_pergunta_obrigatoria_para_opcional(self):
        pergunta = Pergunta.objects.create(
            formulario=self.formulario,
            texto='Pergunta obrigatória',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=1,
            obrigatoria=True,
        )

        response = self.client.post(
            reverse('formularios:editar_pergunta', args=[pergunta.id]),
            data={
                'texto': pergunta.texto,
                'tipo': pergunta.tipo,
                'ordem': pergunta.ordem,
            },
        )

        pergunta.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'O formulário precisa ter pelo menos uma pergunta obrigatória.',
        )
        self.assertTrue(pergunta.obrigatoria)


class PerguntaMultiplaEscolhaTests(TestCase):
    def setUp(self):
        self.formulario = Formulario.objects.create(
            titulo='Pesquisa de acompanhamento',
            descricao='Formulario de teste',
            status=Formulario.STATUS_ATIVO,
        )

    def test_bloqueia_criacao_de_multipla_escolha_com_menos_de_duas_opcoes(self):
        response = self.client.post(
            reverse('formularios:criar_pergunta', args=[self.formulario.id]),
            data={
                'texto': 'Qual turno você prefere?',
                'tipo': Pergunta.TIPO_ESCOLHA,
                'ordem': 1,
                'obrigatoria': 'on',
                'opcoes': ['Manhã'],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Perguntas de múltipla escolha devem ter pelo menos duas opções de resposta.',
        )
        self.assertEqual(self.formulario.perguntas.count(), 0)

    def test_permite_criar_multipla_escolha_com_duas_opcoes(self):
        response = self.client.post(
            reverse('formularios:criar_pergunta', args=[self.formulario.id]),
            data={
                'texto': 'Qual turno você prefere?',
                'tipo': Pergunta.TIPO_ESCOLHA,
                'ordem': 1,
                'obrigatoria': 'on',
                'opcoes': ['Manhã', 'Noite'],
            },
        )

        self.assertEqual(response.status_code, 302)
        pergunta = self.formulario.perguntas.get()
        self.assertEqual(pergunta.opcoes.count(), 2)

    def test_bloqueia_edicao_de_multipla_escolha_com_menos_de_duas_opcoes(self):
        pergunta = Pergunta.objects.create(
            formulario=self.formulario,
            texto='Qual turno você prefere?',
            tipo=Pergunta.TIPO_ESCOLHA,
            ordem=1,
            obrigatoria=True,
        )
        Opcao.objects.create(pergunta=pergunta, texto='Manhã')

        response = self.client.post(
            reverse('formularios:editar_pergunta', args=[pergunta.id]),
            data={
                'texto': pergunta.texto,
                'tipo': pergunta.tipo,
                'ordem': pergunta.ordem,
                'obrigatoria': 'on',
                'opcao_id': [str(opcao.id) for opcao in pergunta.opcoes.all()],
                f'opcao_texto_{pergunta.opcoes.first().id}': 'Manhã',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Perguntas de múltipla escolha devem ter pelo menos duas opções de resposta.',
        )
        self.assertEqual(pergunta.opcoes.count(), 1)


class ResponderQuestionarioTests(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(nome='Sistemas de Informação')
        self.egresso = Egresso.objects.create(
            nome_completo='Ana Silva',
            email='ana@example.com',
            whatsapp='+5511999999999',
            curso=self.curso,
            ano_conclusao=2024,
            status=Egresso.STATUS_ATIVO,
        )
        self.formulario = Formulario.objects.create(
            titulo='Pesquisa de acompanhamento',
            descricao='Formulario de teste',
            status=Formulario.STATUS_ATIVO,
        )
        self.pergunta_obrigatoria = Pergunta.objects.create(
            formulario=self.formulario,
            texto='Como avalia o curso?',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=1,
            obrigatoria=True,
        )
        self.pergunta_opcional = Pergunta.objects.create(
            formulario=self.formulario,
            texto='Deseja deixar um comentário?',
            tipo=Pergunta.TIPO_TEXTO,
            ordem=2,
            obrigatoria=False,
        )
        self.link = FormularioEgresso.objects.create(
            formulario=self.formulario,
            egresso=self.egresso,
        )

    def test_nao_envia_sem_responder_pergunta_obrigatoria(self):
        response = self.client.post(
            reverse('formularios:responder', args=[self.link.token]),
            data={
                f'pergunta_{self.pergunta_opcional.pk}': 'Resposta opcional',
            },
        )

        self.link.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Responda todas as perguntas obrigatórias antes de enviar.',
        )
        self.assertContains(response, 'Esta pergunta é obrigatória.')
        self.assertContains(response, 'Resposta opcional')
        self.assertFalse(self.link.utilizado)
        self.assertEqual(Resposta.objects.count(), 0)

    def test_envia_quando_responde_todas_as_perguntas_obrigatorias(self):
        response = self.client.post(
            reverse('formularios:responder', args=[self.link.token]),
            data={
                f'pergunta_{self.pergunta_obrigatoria.pk}': 'Muito bom',
                f'pergunta_{self.pergunta_opcional.pk}': 'Comentário livre',
            },
        )

        self.link.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.link.utilizado)
        self.assertEqual(Resposta.objects.count(), 2)
