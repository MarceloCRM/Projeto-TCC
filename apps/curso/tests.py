from django.test import TestCase
from django.urls import reverse

from apps.curso.models import Curso
from apps.egresso.models import Egresso


class CursoViewsTests(TestCase):
    def test_listar_curso_exibe_cursos_e_total_de_egressos(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao', status=Curso.STATUS_ATIVO)
        Egresso.objects.create(
            nome_completo='Ana Silva',
            email='ana@example.com',
            whatsapp='11999999999',
            curso=curso,
            ano_conclusao=2024,
            status=Egresso.STATUS_ATIVO,
        )

        response = self.client.get(reverse('curso:listar_curso'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'curso/listar_curso.html')
        self.assertContains(response, 'Sistemas de Informacao')
        self.assertEqual(response.context['total'], 1)

    def test_criar_curso_salva_e_redireciona_para_listagem(self):
        response = self.client.post(
            reverse('curso:criar_curso'),
            {'nome': 'Ciencia da Computacao', 'status': Curso.STATUS_INATIVO},
        )

        self.assertRedirects(response, reverse('curso:listar_curso'))
        self.assertTrue(Curso.objects.filter(nome='Ciencia da Computacao', status=Curso.STATUS_INATIVO).exists())

    def test_detalhe_curso_exibe_egressos_relacionados(self):
        curso = Curso.objects.create(nome='Analise e Desenvolvimento de Sistemas', status=Curso.STATUS_ATIVO)
        egresso = Egresso.objects.create(
            nome_completo='Bruno Souza',
            email='bruno@example.com',
            whatsapp='11888888888',
            curso=curso,
            ano_conclusao=2023,
            status=Egresso.STATUS_ATIVO,
        )

        response = self.client.get(reverse('curso:detalhe_curso', args=[curso.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'curso/detalhe_curso.html')
        self.assertContains(response, curso.nome)
        self.assertContains(response, egresso.nome_completo)

    def test_listar_curso_filtra_por_status(self):
        Curso.objects.create(nome='Engenharia de Software', status=Curso.STATUS_ATIVO)
        Curso.objects.create(nome='Redes de Computadores', status=Curso.STATUS_INATIVO)

        response = self.client.get(reverse('curso:listar_curso'), {'status': Curso.STATUS_INATIVO})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Redes de Computadores')
        self.assertNotContains(response, 'Engenharia de Software')
