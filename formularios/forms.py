from django import forms
from .models import Pergunta


class FormularioDinamico(forms.Form):

    def __init__(self, *args, perguntas=None, **kwargs):
        super().__init__(*args, **kwargs)

        for pergunta in perguntas:
            field_name = f'pergunta_{pergunta.id}'

            if pergunta.tipo == Pergunta.TIPO_TEXTO:
                self.fields[field_name] = forms.CharField(
                    label=pergunta.texto,
                    required=pergunta.obrigatoria
                )

            elif pergunta.tipo == Pergunta.TIPO_NUMERO:
                self.fields[field_name] = forms.FloatField(
                    label=pergunta.texto,
                    required=pergunta.obrigatoria
                )

            elif pergunta.tipo == Pergunta.TIPO_BOOLEANO:
                self.fields[field_name] = forms.BooleanField(
                    label=pergunta.texto,
                    required=False
                )

            elif pergunta.tipo == Pergunta.TIPO_ESCOLHA:
                self.fields[field_name] = forms.ChoiceField(
                    label=pergunta.texto,
                    choices=[
                        (op.id, op.texto) for op in pergunta.opcoes.all()
                    ],
                    widget=forms.RadioSelect,
                    required=pergunta.obrigatoria
                )
