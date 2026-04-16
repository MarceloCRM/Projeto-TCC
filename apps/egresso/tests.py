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

    def test_form_inicia_codigo_do_brasil_como_padrao(self):
        form = EgressoForm()

        self.assertEqual(form.initial['country_code'], 'BR')

    def test_form_salva_egresso_com_curso_existente(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')

        form = EgressoForm(data={
            'nome_completo': 'Ana Silva',
            'email': 'ana@example.com',
            'country_code': 'BR',
            'whatsapp': '11999999999',
            'curso': curso.id,
            'ano_conclusao': 2024,
            'status': Egresso.STATUS_ATIVO,
        })

        self.assertTrue(form.is_valid(), form.errors)

        egresso = form.save()

        self.assertEqual(Curso.objects.count(), 1)
        self.assertEqual(egresso.curso.nome, 'Sistemas de Informacao')
        self.assertEqual(egresso.whatsapp, '+5511999999999')

    def test_form_salva_egresso_com_codigo_de_outro_pais(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')

        form = EgressoForm(data={
            'nome_completo': 'Ana Silva',
            'email': 'ana@example.com',
            'country_code': 'PT',
            'whatsapp': '912345678',
            'curso': curso.id,
            'ano_conclusao': 2024,
            'status': Egresso.STATUS_ATIVO,
        })

        self.assertTrue(form.is_valid(), form.errors)

        egresso = form.save()

        self.assertEqual(egresso.whatsapp, '+351912345678')

    def test_form_edita_egresso_usando_curso_existente(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')
        novo_curso = Curso.objects.create(nome='Ciencia da Computacao')
        egresso = Egresso.objects.create(
            nome_completo='Ana Silva',
            email='ana@example.com',
            whatsapp='+5511999999999',
            curso=curso,
            ano_conclusao=2024,
            status=Egresso.STATUS_ATIVO,
        )

        form = EgressoForm(data={
            'nome_completo': egresso.nome_completo,
            'email': egresso.email,
            'country_code': 'BR',
            'whatsapp': '21999999999',
            'curso': novo_curso.id,
            'ano_conclusao': egresso.ano_conclusao,
            'status': egresso.status,
        }, instance=egresso)

        self.assertTrue(form.is_valid(), form.errors)

        egresso_atualizado = form.save()

        self.assertEqual(Curso.objects.count(), 2)
        self.assertEqual(egresso_atualizado.curso_id, novo_curso.id)
        self.assertEqual(egresso_atualizado.whatsapp, '+5521999999999')

    def test_formata_whatsapp_existente_para_exibicao(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')
        egresso = Egresso.objects.create(
            nome_completo='Ana Silva',
            email='ana@example.com',
            whatsapp='+351912345678',
            curso=curso,
            ano_conclusao=2024,
            status=Egresso.STATUS_ATIVO,
        )

        form = EgressoForm(instance=egresso)

        self.assertEqual(form.initial['country_code'], 'PT')
        self.assertEqual(form.initial['whatsapp'], '912345678')

    def test_rejeita_whatsapp_fora_do_formato_esperado(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')

        form = EgressoForm(data={
            'nome_completo': 'Ana Silva',
            'email': 'ana@example.com',
            'country_code': 'BR',
            'whatsapp': '999',
            'curso': curso.id,
            'ano_conclusao': 2024,
            'status': Egresso.STATUS_ATIVO,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('whatsapp', form.errors)
