from django import forms
from django.forms import NumberInput, Select, TextInput

from .models import Egresso


class EgressoForm(forms.ModelForm):
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
            'curso': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Curso'
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
            'placeholder': 'Buscar por nome'
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
