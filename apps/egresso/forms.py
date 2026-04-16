import re

import phonenumbers
import pycountry
from django import forms
from django.forms import NumberInput, Select, TextInput

from apps.curso.models import Curso

from .models import Egresso


def get_country_code_choices():
    countries = []

    for region_code in sorted(phonenumbers.SUPPORTED_REGIONS):
        country = pycountry.countries.get(alpha_2=region_code)
        if not country:
            continue

        calling_code = phonenumbers.country_code_for_region(region_code)
        if not calling_code:
            continue

        countries.append(
            (
                region_code,
                f'{country.name} (+{calling_code})',
                country.name,
            )
        )

    countries.sort(key=lambda item: (item[0] != 'BR', item[2]))
    return [(region_code, label) for region_code, label, _ in countries]


COUNTRY_CODE_CHOICES = get_country_code_choices()
COUNTRY_REGION_SET = {region_code for region_code, _ in COUNTRY_CODE_CHOICES}


class EgressoForm(forms.ModelForm):
    DEFAULT_REGION = 'BR'

    curso = forms.ModelChoiceField(
        queryset=Curso.objects.none(),
        label='Curso',
        empty_label='Selecione um curso',
        widget=Select(attrs={
            'class': 'form-select'
        })
    )

    country_code = forms.ChoiceField(
        label='Código do país',
        choices=COUNTRY_CODE_CHOICES,
        initial=DEFAULT_REGION,
        widget=Select(attrs={
            'class': 'form-select',
            'data-country-code-select': 'true',
        }),
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
                'placeholder': 'Ex.: Maria Aparecida da Silva'
            }),
            'email': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: maria.silva@email.com'
            }),
            'whatsapp': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: (11) 999999999',
                'inputmode': 'numeric',
                'maxlength': '18',
                'data-whatsapp-input': 'true',
            }),
            'curso': Select(attrs={
                'class': 'form-select'
            }),
            'ano_conclusao': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: 2024',
                'min': '1900',
                'max': '2100',
            }),
            'status': Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'nome_completo': 'Nome completo',
            'email': 'E-mail',
            'whatsapp': 'WhatsApp',
            'curso': 'Curso',
            'ano_conclusao': 'Ano de conclusão',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].queryset = Curso.objects.order_by('nome')

        if self.is_bound:
            return

        whatsapp = self.initial.get('whatsapp') or getattr(self.instance, 'whatsapp', '')
        region_code, numero = self.split_whatsapp(whatsapp)
        self.initial['country_code'] = region_code
        self.initial['whatsapp'] = numero

    @classmethod
    def split_whatsapp(cls, value):
        digits = re.sub(r'\D', '', value or '')
        if not digits:
            return cls.DEFAULT_REGION, ''

        try:
            phone_number = phonenumbers.parse(f'+{digits}', None)
        except phonenumbers.NumberParseException:
            return cls.DEFAULT_REGION, digits

        region_code = phonenumbers.region_code_for_number(phone_number) or cls.DEFAULT_REGION
        if region_code not in COUNTRY_REGION_SET:
            region_code = cls.DEFAULT_REGION

        national_number = str(phone_number.national_number or '')
        return region_code, national_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        queryset = Egresso.objects.filter(email=email)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')

        return email

    def clean_country_code(self):
        region_code = (self.cleaned_data.get('country_code') or '').upper()
        if region_code not in COUNTRY_REGION_SET:
            raise forms.ValidationError('Selecione um código de país válido.')
        return region_code

    def clean_whatsapp(self):
        whatsapp = re.sub(r'\D', '', self.cleaned_data.get('whatsapp') or '')
        if not whatsapp:
            return ''

        region_code = (self.data.get('country_code') or self.cleaned_data.get('country_code') or self.DEFAULT_REGION).upper()
        if region_code not in COUNTRY_REGION_SET:
            return whatsapp

        calling_code = phonenumbers.country_code_for_region(region_code)
        try:
            phone_number = phonenumbers.parse(f'+{calling_code}{whatsapp}', None)
        except phonenumbers.NumberParseException:
            raise forms.ValidationError('Informe um número válido para o país selecionado.')

        if phone_number.country_code != calling_code:
            raise forms.ValidationError('Informe um número válido para o país selecionado.')

        if not phonenumbers.is_possible_number(phone_number):
            raise forms.ValidationError('Informe um número válido para o país selecionado.')

        return str(phone_number.national_number)

    def clean(self):
        cleaned_data = super().clean()
        region_code = cleaned_data.get('country_code')
        whatsapp = cleaned_data.get('whatsapp')

        if whatsapp and region_code in COUNTRY_REGION_SET:
            calling_code = phonenumbers.country_code_for_region(region_code)
            cleaned_data['whatsapp'] = f'+{calling_code}{whatsapp}'

        return cleaned_data


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
            'placeholder': 'Ex.: 2024'
        })
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Status')] + Egresso.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
