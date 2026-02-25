from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "nome",
            "tipo_pessoa",
            "documento",
            "email",
            "telefone",
            "ativo",
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "input"}),
            "tipo_pessoa": forms.Select(attrs={"class": "input"}),
            "documento": forms.TextInput(attrs={"class": "input"}),
            "email": forms.EmailInput(attrs={"class": "input"}),
            "telefone": forms.TextInput(attrs={"class": "input"}),
            "ativo": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }
