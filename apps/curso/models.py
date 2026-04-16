from django.db import models


class Curso(models.Model):
    STATUS_ATIVO = 'ativo'
    STATUS_INATIVO = 'inativo'

    STATUS_CHOICES = [
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_INATIVO, 'Inativo'),
    ]

    nome = models.CharField('Nome', max_length=255, unique=True)
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default=STATUS_ATIVO)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ('nome',)

    def __str__(self):
        return self.nome
