from django.db import models


class Egresso(models.Model):
    STATUS_ATIVO = 'ativo'
    STATUS_INATIVO = 'inativo'

    STATUS_CHOICES = [
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_INATIVO, 'Inativo'),
    ]

    SITUACAO_PROFISSIONAL = [
        ('empregado', 'Empregado (CLT)'),
        ('autonomo', 'Autonomo / Freelancer'),
        ('empresario', 'Empresario'),
        ('desempregado', 'Desempregado'),
        ('estudando', 'Estudando'),
        ('outro', 'Outro'),
    ]

    FAIXA_SALARIAL = [
        ('ate_2k', 'Ate R$ 2.000'),
        ('2k_4k', 'R$ 2.000 - R$ 4.000'),
        ('4k_7k', 'R$ 4.000 - R$ 7.000'),
        ('7k_12k', 'R$ 7.000 - R$ 12.000'),
        ('acima_12k', 'Acima de R$ 12.000'),
    ]

    nome_completo = models.CharField('Nome Completo', max_length=255)
    email = models.EmailField('E-mail', unique=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True, null=True)
    curso = models.CharField('Curso', max_length=255)
    ano_conclusao = models.IntegerField('Ano de Conclusao')
    situacao_profissional = models.CharField(
        'Situacao Profissional',
        max_length=20,
        choices=SITUACAO_PROFISSIONAL,
        default='desempregado',
    )
    empresa_atual = models.CharField('Empresa Atual', max_length=255, blank=True, null=True)
    faixa_salarial = models.CharField(
        'Faixa Salarial',
        max_length=20,
        choices=FAIXA_SALARIAL,
        blank=True,
        null=True,
    )
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default=STATUS_ATIVO)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Egresso'
        verbose_name_plural = 'Egressos'

    def __str__(self):
        return f'{self.nome_completo} ({self.ano_conclusao})'
