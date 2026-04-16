from django.test import TestCase

from apps.curso.models import Curso

from .forms import EgressoForm
from .models import Egresso


class EgressoFormTests(TestCase):
    def test_form_cria_curso_automaticamente_ao_salvar(self):
        form = EgressoForm(data={
            'nome_completo': 'Ana Silva',
            'email': 'ana@example.com',
            'whatsapp': '11999999999',
            'curso_nome': 'Sistemas de Informacao',
            'ano_conclusao': 2024,
            'status': Egresso.STATUS_ATIVO,
        })

        self.assertTrue(form.is_valid(), form.errors)

        egresso = form.save()

        self.assertEqual(Curso.objects.count(), 1)
        self.assertEqual(egresso.curso.nome, 'Sistemas de Informacao')

    def test_form_reaproveita_curso_existente_ao_editar(self):
        curso = Curso.objects.create(nome='Sistemas de Informacao')
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
            'curso_nome': 'Sistemas de Informacao',
            'ano_conclusao': egresso.ano_conclusao,
            'status': egresso.status,
        }, instance=egresso)

        self.assertTrue(form.is_valid(), form.errors)

        egresso_atualizado = form.save()

        self.assertEqual(Curso.objects.count(), 1)
        self.assertEqual(egresso_atualizado.curso_id, curso.id)
