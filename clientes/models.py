import re

from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.

# ============================
# Funções utilitárias: CPF / CNPJ
# ============================

def valida_cpf(cpf: str) -> bool:
    """
    Validação de CPF apenas pela regra dos dígitos verificadores.
    Não consulta Receita, apenas matemática.
    """
    cpf = re.sub(r"\D", "", cpf or "")

    if len(cpf) != 11:
        return False

    # rejeita sequências do tipo 00000000000, 11111111111 etc.
    if cpf == cpf[0] * 11:
        return False

    def calc_digito(cpf_slice, fator_inicial):
        total = 0
        fator = fator_inicial
        for dig in cpf_slice:
            total += int(dig) * fator
            fator -= 1
        resto = total % 11
        return "0" if resto < 2 else str(11 - resto)

    d1 = calc_digito(cpf[:9], 10)
    d2 = calc_digito(cpf[:10], 11)

    return cpf[-2:] == d1 + d2


def valida_cnpj(cnpj: str) -> bool:
    """
    Validação de CNPJ apenas pela regra dos dígitos verificadores.
    Não consulta Receita, apenas matemática.
    """
    cnpj = re.sub(r"\D", "", cnpj or "")

    if len(cnpj) != 14:
        return False

    # rejeita sequências repetidas
    if cnpj == cnpj[0] * 14:
        return False

    def calc_digito(cnpj_slice, pesos):
        total = sum(int(d) * p for d, p in zip(cnpj_slice, pesos))
        resto = total % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    d1 = calc_digito(cnpj[:12], pesos1)
    d2 = calc_digito(cnpj[:13], pesos2)

    return cnpj[-2:] == d1 + d2


# ============================
# Modelos de domínio
# ============================


class Cliente(models.Model):
    TIPO_PESSOA_CHOICES = (
        ("PF", "Pessoa Física"),
        ("PJ", "Pessoa Jurídica"),
    )

    tipo_pessoa = models.CharField(
        max_length=2,
        choices=TIPO_PESSOA_CHOICES,
        help_text="Define se o cliente é PF ou PJ para validar CPF/CNPJ.",
    )
    nome = models.CharField(max_length=255)
    documento = models.CharField(
        max_length=20,
        help_text="CPF ou CNPJ (apenas números ou formatado).",
        unique=True
    )
    email = models.EmailField(blank=True, default="")
    telefone = models.CharField(max_length=20, blank=True, default="")
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome

    def clean(self):
        """
        Garante que o documento é válido de acordo com o tipo de pessoa.
        """
        super().clean()

        if not self.documento:
            return

        doc = re.sub(r"\D", "", self.documento)

        if self.tipo_pessoa == "PF":
            if not valida_cpf(doc):
                raise ValidationError({"documento": "CPF inválido."})
        elif self.tipo_pessoa == "PJ":
            if not valida_cnpj(doc):
                raise ValidationError({"documento": "CNPJ inválido."})

    def save(self, *args, **kwargs):
        """
        Normaliza o documento para apenas dígitos antes de salvar.
        """
        if self.documento:
            self.documento = re.sub(r"\D", "", self.documento)
        super().save(*args, **kwargs)
