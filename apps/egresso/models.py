from django.db import models


class Egresso(models.Model):
    STATUS_ATIVO = 'ativo'
    STATUS_INATIVO = 'inativo'

    STATUS_CHOICES = [
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_INATIVO, 'Inativo'),
    ]

    nome_completo = models.CharField('Nome Completo', max_length=255)
    email = models.EmailField('E-mail', unique=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True, null=True)
    curso = models.CharField('Curso', max_length=255)
    ano_conclusao = models.IntegerField('Ano de Conclusao')
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default=STATUS_ATIVO)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Egresso'
        verbose_name_plural = 'Egressos'

    def __str__(self):
        return f'{self.nome_completo} ({self.ano_conclusao})'
