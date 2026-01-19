from django.db import models


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
    TIPO_BOOLEANO = 'booleano'

    TIPOS = [
        (TIPO_TEXTO, 'Texto'),
        (TIPO_NUMERO, 'Número'),
        (TIPO_ESCOLHA, 'Múltipla escolha'),
        (TIPO_BOOLEANO, 'Sim / Não'),
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
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resposta #{self.id} - {self.formulario.titulo}"


class Resposta(models.Model):
    resposta_formulario = models.ForeignKey(RespostaFormulario, on_delete=models.CASCADE, related_name='respostas')
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    valor_texto = models.TextField(null=True, blank=True)
    valor_numero = models.FloatField(null=True, blank=True)
    valor_opcao = models.ForeignKey(Opcao,null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Resposta à pergunta {self.pergunta.id}"
