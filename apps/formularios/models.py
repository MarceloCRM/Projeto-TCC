from django.db import models
from apps.egresso.models import Egresso
import uuid


class Formulario(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
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
        return f"Link #{self.egresso.nome_completo} - {self.formulario.titulo}"


class Resposta(models.Model):
    """
    Conjunto de respostas de um egresso a um formulario.
    Cada egresso só pode responder uma vez por formulario.
    """

    formulario = models.ForeignKey(
        Formulario,
        on_delete=models.CASCADE,
        related_name='respostas',
        verbose_name='Formulario',
    )
    egresso = models.ForeignKey(
        Egresso,
        on_delete=models.CASCADE,
        related_name='respostas',
        verbose_name='Egresso',
    )
    enviado_em = models.DateTimeField('Enviado em', auto_now_add=True)

    class Meta:
        # Garante unicidade: um egresso responde uma vez por formulario
        unique_together = ['formulario', 'egresso']
        ordering = ['-enviado_em']
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'

    def __str__(self):
        return f'{self.egresso.nome_completo} → {self.questionario.titulo}'

    def __str__(self):
        return f"Resposta a pergunta {self.pergunta.id}"

class Alternativa(models.Model):
    """Alternativa individual de uma Resposta para uma Pergunta."""

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
        verbose_name = 'Alternativa'
        verbose_name_plural = 'Alternativas'

    def __str__(self):
        return f'Resposta para: {self.questao.texto[:40]}'
