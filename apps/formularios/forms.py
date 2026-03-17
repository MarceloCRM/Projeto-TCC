from django import forms
from .models import Pergunta, Opcao, Formulario

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

class FormularioForm(forms.ModelForm):
    class Meta:
        model = Formulario
        fields = ['titulo', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do formulário'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do formulário',
                'rows': 3
            }),
        }


class PerguntaForm(forms.ModelForm):
    class Meta:
        model = Pergunta
        fields = ['texto', 'tipo', 'ordem']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o texto da pergunta'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordem da pergunta'
            }),
        }


class OpcaoForm(forms.ModelForm):
    class Meta:
        model = Opcao
        fields = ['texto']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto da opção'
            }),
        }
