from django import forms
from django.forms import NumberInput, Select, TextInput

from apps.curso.models import Curso

from .models import Egresso


class EgressoForm(forms.ModelForm):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.none(),
        label='Curso',
        empty_label='Selecione um curso',
        widget=Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Egresso
        fields = [
            'nome_completo',
            'email',
            'whatsapp',
            'curso',
            'ano_conclusao',
            'status',
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
            'curso': Select(attrs={
                'class': 'form-select'
            }),
            'ano_conclusao': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ano de Conclusao'
            }),
            'status': Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'nome_completo': 'Nome Completo',
            'email': 'Email',
            'whatsapp': 'WhatsApp',
            'curso': 'Curso',
            'ano_conclusao': 'Ano de Conclusao',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].queryset = Curso.objects.order_by('nome')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        queryset = Egresso.objects.filter(email=email)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Este e-mail ja esta cadastrado.')

        return email


class EgressoFiltroForm(forms.Form):
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do egresso'
        })
    )

    curso = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do curso'
        })
    )

    ano_conclusao = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ano de conclusão'
        })
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Status')] + Egresso.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
