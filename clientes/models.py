import re

from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.

# ============================
# Funções utilitárias: CPF / CNPJ
# ============================

def valida_cpf(cpf: str) -> bool:
    """
    Validate a Brazilian CPF number.
    
    Non-digit characters in the input are ignored. The function requires exactly 11 digits and rejects sequences where all digits are identical (e.g., '00000000000'). Validation is performed using the CPF check-digit rules.
    
    Parameters:
        cpf (str): The CPF value to validate; may include punctuation or whitespace.
    
    Returns:
        bool: `True` if the CPF is valid according to its check digits, `False` otherwise.
    """
    cpf = re.sub(r"\D", "", cpf or "")

    if len(cpf) != 11:
        return False

    # rejeita sequências do tipo 00000000000, 11111111111 etc.
    if cpf == cpf[0] * 11:
        return False

    def calc_digito(cpf_slice, fator_inicial):
        """
        Compute a single CPF check digit using the modulus-11 weighting method.
        
        Parameters:
            cpf_slice (str): Sequence of digits (as characters) used to calculate the check digit.
            fator_inicial (int): Starting weight applied to the first digit of `cpf_slice`; each subsequent digit uses a weight decremented by 1.
        
        Returns:
            str: The calculated check digit as a single-character string. Returns "0" when the modulus-11 remainder is less than 2, otherwise returns the string of (11 - remainder).
        """
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
    Validate a Brazilian CNPJ using its check-digit rules.
    
    Normalizes the input by removing non-digit characters, rejects values that are not 14 digits or that consist of a repeated digit, and verifies the two check digits using the standard modulo-11 algorithm.
    
    Parameters:
        cnpj (str): CNPJ string; may include punctuation (dots, slashes, hyphens) which will be ignored.
    
    Returns:
        bool: True if the CNPJ's check digits are valid, False otherwise.
    """
    cnpj = re.sub(r"\D", "", cnpj or "")

    if len(cnpj) != 14:
        return False

    # rejeita sequências repetidas
    if cnpj == cnpj[0] * 14:
        return False

    def calc_digito(cnpj_slice, pesos):
        """
        Compute the CNPJ check digit for a slice of digit characters using the provided weights.
        
        Parameters:
            cnpj_slice (Iterable[str]): Sequence of digit characters to use for the calculation (e.g., the first 12 or 13 digits).
            pesos (Iterable[int]): Sequence of integer weights to apply to each digit of `cnpj_slice`.
        
        Returns:
            str: Single-character check digit: `"0"` if the computed remainder is less than 2, otherwise the decimal digit resulting from `11 - remainder`.
        """
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
        """
        Provide the client's name for display.
        
        Returns:
            The client's `nome` value used as the model's string representation.
        """
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
        Ensure the instance's `documento` contains only digits before saving.
        
        If `documento` is set, strip all non-digit characters and persist the normalized value.
        """
        if self.documento:
            self.documento = re.sub(r"\D", "", self.documento)
        super().save(*args, **kwargs)