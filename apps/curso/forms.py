from django import forms

from .models import Curso


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nome', 'status']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do curso'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'nome': 'Nome do curso',
            'status': 'Status',
        }

    def clean_nome(self):
        nome = ' '.join((self.cleaned_data.get('nome') or '').split())

        if not nome:
            raise forms.ValidationError('Informe o nome do curso.')

        queryset = Curso.objects.filter(nome__iexact=nome)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Ja existe um curso com esse nome.')

        return nome


class CursoFiltroForm(forms.Form):
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do curso'
        })
    )

    criado_em = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Status')] + Curso.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
