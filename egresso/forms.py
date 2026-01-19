from django import forms
from django.forms import TextInput, NumberInput
from .models import Egresso

class EgressoForm(forms.ModelForm):
    class Meta:
        model = Egresso
        fields = ['fullName', 'birthDate', 'gender', 'status', 'email', 'number']
        widgets = {
            'fullName': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome Completo'
            }),
            'birthDate': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gênero'
            }),
            'status': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Status'
            }),
            'email': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'number': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de Telefone'
            }),
        }
        labels = {
            'fullName': 'Nome Completo',
            'birthDate': 'Data de Nascimento',
            'gender': 'Gênero',
            'status': 'Status',
            'email': 'Email',
            'number': 'Número de Telefone',
        }
