import uuid

from django.db import models

from apps.egresso.models import Egresso


class Formulario(models.Model):
    STATUS_ATIVO = 'ativo'
    STATUS_INATIVO = 'inativo'

    STATUS_CHOICES = [
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_INATIVO, 'Inativo'),
    ]

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ATIVO)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Pergunta(models.Model):
    TIPO_TEXTO = 'texto'
    TIPO_NUMERO = 'numero'
    TIPO_ESCOLHA = 'escolha'
    TIPO_ESCALA = 'escala'

    TIPOS = [
        (TIPO_TEXTO, 'Texto'),
        (TIPO_NUMERO, 'Numero'),
        (TIPO_ESCOLHA, 'Multipla escolha'),
        (TIPO_ESCALA, 'Escala de 1 a 5'),
    ]

    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='perguntas')
    texto = models.CharField(max_length=300)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    obrigatoria = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField()

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.texto


class Opcao(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name='opcoes')
    texto = models.CharField(max_length=200)

    def __str__(self):
        return self.texto


class RespostaFormulario(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='links', verbose_name='Questionario')
    egresso = models.ForeignKey(Egresso, models.CASCADE, related_name='links', verbose_name='Egresso')

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    utilizado = models.BooleanField('Utilizado', default=False)

    def __str__(self):
        return f'Link #{self.egresso.nome_completo} - {self.formulario.titulo}'


class Resposta(models.Model):
    resposta_formulario = models.OneToOneField(
        RespostaFormulario,
        on_delete=models.CASCADE,
        related_name='resposta',
        verbose_name='Resposta do Formulario',
    )
    enviado_em = models.DateTimeField('Enviado em', auto_now_add=True)

    class Meta:
        ordering = ['-enviado_em']
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'

    def __str__(self):
        return (
            f'{self.resposta_formulario.egresso.nome_completo} -> '
            f'{self.resposta_formulario.formulario.titulo}'
        )


class RespostaPergunta(models.Model):
    resposta = models.ForeignKey(
        Resposta,
        on_delete=models.CASCADE,
        related_name='alternativas',
        verbose_name='Resposta',
    )
    pergunta = models.ForeignKey(
        Pergunta,
        on_delete=models.CASCADE,
        verbose_name='Pergunta',
    )
    # Armazena o valor como texto independente do tipo da pergunta
    valor = models.TextField('Valor da Resposta')

    class Meta:
        verbose_name = 'Resposta da Pergunta'
        verbose_name_plural = 'Respostas das Perguntas'

    def __str__(self):
        return f'Resposta para: {self.pergunta.texto[:40]}'
