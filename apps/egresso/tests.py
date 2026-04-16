from django.test import TestCase

from apps.curso.models import Curso

from .forms import EgressoForm
from .models import Egresso


class EgressoFormTests(TestCase):
    def test_form_exibe_cursos_em_lista_para_selecao(self):
        curso_a = Curso.objects.create(nome='Analise e Desenvolvimento de Sistemas')
        curso_b = Curso.objects.create(nome='Sistemas de Informacao')

        form = EgressoForm()

        self.assertQuerySetEqual(
            form.fields['curso'].queryset,
            [curso_a, curso_b],
            transform=lambda item: item,
        )

    def test_form_salva_egresso_com_curso_existente(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')

        form = EgressoForm(data={
            'nome_completo': 'Ana Silva',
            'email': 'ana@example.com',
            'whatsapp': '11999999999',
            'curso': curso.id,
            'ano_conclusao': 2024,
            'status': Egresso.STATUS_ATIVO,
        })

        self.assertTrue(form.is_valid(), form.errors)

        egresso = form.save()

        self.assertEqual(Curso.objects.count(), 1)
        self.assertEqual(egresso.curso.nome, 'Sistemas de Informacao')

    def test_form_edita_egresso_usando_curso_existente(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')
        novo_curso = Curso.objects.create(nome='Ciencia da Computacao')
        egresso = Egresso.objects.create(
            nome_completo='Ana Silva',
            email='ana@example.com',
            whatsapp='11999999999',
            curso=curso,
            ano_conclusao=2024,
            status=Egresso.STATUS_ATIVO,
        )

        form = EgressoForm(data={
            'nome_completo': egresso.nome_completo,
            'email': egresso.email,
            'whatsapp': egresso.whatsapp,
            'curso': novo_curso.id,
            'ano_conclusao': egresso.ano_conclusao,
            'status': egresso.status,
        }, instance=egresso)

        self.assertTrue(form.is_valid(), form.errors)

        egresso_atualizado = form.save()

        self.assertEqual(Curso.objects.count(), 2)
        self.assertEqual(egresso_atualizado.curso_id, novo_curso.id)
