from django import forms
from django.forms import TextInput, NumberInput, Select
from .models import Egresso
from django.core.exceptions import ValidationError



class EgressoForm(forms.ModelForm):
    class Meta:
        model = Egresso
        fields = [
            'nome_completo',
            'email',
            'whatsapp',
            'curso',
            'ano_conclusao',
            'situacao_profissional',
            'empresa_atual',
            'faixa_salarial',
        ]

        widgets = {
            'nome_completo': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome Completo'
            }),
            'email': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'whatsapp': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WhatsApp'
            }),
            'curso': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Curso'
            }),
            'ano_conclusao': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ano de Conclusão'
            }),
            'situacao_profissional': Select(attrs={
                'class': 'form-select'
            }),
            'empresa_atual': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Empresa Atual'
            }),
            'faixa_salarial': Select(attrs={
                'class': 'form-select'
            }),
        }

        labels = {
            'nome_completo': 'Nome Completo',
            'email': 'Email',
            'whatsapp': 'WhatsApp',
            'curso': 'Curso',
            'ano_conclusao': 'Ano de Conclusão',
            'situacao_profissional': 'Situação Profissional',
            'empresa_atual': 'Empresa Atual',
            'faixa_salarial': 'Faixa Salarial',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Egresso.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email
    
class EgressoFiltroForm(forms.Form):
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome, email ou curso'
        })
    )

    curso = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Curso'
        })
    )

    ano_conclusao = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ano'
        })
    )

    situacao_profissional = forms.ChoiceField(
        required=False,
        choices=[('', 'Situação')] + Egresso.SITUACAO_PROFISSIONAL,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )