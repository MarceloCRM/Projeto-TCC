from django import forms
from django.forms import NumberInput, Select, TextInput

from apps.curso.models import Curso

from .models import Egresso


class EgressoForm(forms.ModelForm):
    curso_nome = forms.CharField(
        label='Curso',
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Curso'
        })
    )

    class Meta:
        model = Egresso
        fields = [
            'nome_completo',
            'email',
            'whatsapp',
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
            'ano_conclusao': 'Ano de Conclusao',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.curso_id:
            self.fields['curso_nome'].initial = self.instance.curso.nome

    def clean_curso_nome(self):
        curso_nome = ' '.join((self.cleaned_data.get('curso_nome') or '').split())

        if not curso_nome:
            raise forms.ValidationError('Informe o curso.')

        return curso_nome

    def clean_email(self):
        email = self.cleaned_data.get('email')
        queryset = Egresso.objects.filter(email=email)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Este e-mail ja esta cadastrado.')

        return email

    def save(self, commit=True):
        curso_nome = self.cleaned_data['curso_nome']
        curso = Curso.objects.filter(nome__iexact=curso_nome).first()

        if curso is None:
            curso = Curso.objects.create(nome=curso_nome)

        egresso = super().save(commit=False)
        egresso.curso = curso

        if commit:
            egresso.save()

        return egresso


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
