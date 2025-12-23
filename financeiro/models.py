from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone

class Categoria(models.Model):
    """
    Categoria financeira (tanto de entrada quanto de saída).
    Exemplo: 'Receita de clientes', 'Impostos', 'Assinaturas', etc.
    """

    TIPO_LANCAMENTO_CHOICES = (
        ("ENTRADA", "Entrada"),
        ("SAIDA", "Saída"),
    )

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=7, choices=TIPO_LANCAMENTO_CHOICES)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return f"{self.nome} ({self.tipo})"


class CentroCusto(models.Model):
    """
    Centro de custos, para agrupar despesas/receitas por área/projeto.
    """
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Centro de custo"
        verbose_name_plural = "Centros de custo"

    def __str__(self):
        return self.nome


class Banco(models.Model):
    """
    Cadastro de banco (Nubank, Inter, Itaú, etc.).
    Útil para ter 1..N contas por banco e, no futuro, definir regras de
    leitura de extrato (PDF/OFX) específicas por banco.
    """
    nome = models.CharField(max_length=100)
    codigo = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Código do banco (BACEN) ou identificador interno.",
    )
    # campo genérico para você usar depois nas regras de importação
    identificador_layout_extrato = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Identificador do layout de extrato (PDF/OFX) deste banco.",
    )

    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"

    def __str__(self):
        return f"{self.nome} ({self.codigo})" if self.codigo else self.nome


class ContaBancaria(models.Model):
    """
    Representa uma conta bancária (Nubank PJ, Inter PF, Itaú Poupança, etc.).
    Permite várias contas para o mesmo banco.
    """

    TIPO_CONTA_CHOICES = (
        ("CORRENTE", "Corrente"),
        ("POUPANCA", "Poupança"),
        ("OUTRA", "Outra"),
    )

    banco = models.ForeignKey(
        Banco,
        on_delete=models.PROTECT,
        related_name="contas",
    )
    nome = models.CharField(
        max_length=100,
        help_text="Apelido da conta: Nubank PJ, Inter PF, Itaú Poupança, etc.",
    )
    tipo_conta = models.CharField(
        max_length=10,
        choices=TIPO_CONTA_CHOICES,
        default="CORRENTE",
    )
    agencia = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    numero = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Número/identificação da conta (opcional).",
    )
    saldo_inicial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Saldo de abertura de controle no sistema.",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conta bancária"
        verbose_name_plural = "Contas bancárias"

    def __str__(self):
        return f"{self.nome} - {self.banco.nome}"

    @property
    def saldo_atual(self):
        """
        Calcula saldo atual com base nos lançamentos já pagos.
        Entradas - Saídas + saldo_inicial.
        """
        entradas = self.lancamentos.filter(
            tipo="ENTRADA", situacao="PAGO"
        ).aggregate(total=Sum("valor"))["total"] or Decimal("0")
        saidas = self.lancamentos.filter(
            tipo="SAIDA", situacao="PAGO"
        ).aggregate(total=Sum("valor"))["total"] or Decimal("0")
        return self.saldo_inicial + entradas - saidas



class Lancamento(models.Model):
    """
    Lançamento financeiro (entrada ou saída).
    Pode estar ligado a um cliente, contrato e item de contrato.
    """

    TIPO_CHOICES = (
        ("ENTRADA", "Entrada"),
        ("SAIDA", "Saída"),
    )

    SITUACAO_CHOICES = (
        ("PENDENTE", "Pendente"),
        ("PAGO", "Pago"),
        ("CANCELADO", "Cancelado"),
    )

    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lancamentos",
    )
    contrato = models.ForeignKey(
        "contratos.Contrato",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lancamentos",
    )
    item_contrato = models.ForeignKey(
        "contratos.ItemContrato",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lancamentos",
        help_text="Se este lançamento for decorrente de um contrato, vincule o item aqui.",
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="lancamentos",
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lancamentos",
    )
    conta = models.ForeignKey(
        ContaBancaria,
        on_delete=models.PROTECT,
        related_name="lancamentos",
    )

    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    competencia = models.DateField(
        null=True,
        blank=True,
        help_text="Para recorrencias: primeiro dia do mes de referencia.",
    )

    data = models.DateField(
        help_text="Data de competência ou da movimentação.",
    )
    data_vencimento = models.DateField(
        null=True,
        blank=True,
        help_text="Usado para controle de vencimento (ex: boletos a pagar/receber).",
    )
    situacao = models.CharField(
        max_length=10,
        choices=SITUACAO_CHOICES,
        default="PENDENTE",
    )

    nota_fiscal_emitida = models.BooleanField(
        default=False,
        help_text="Marque quando a NF referente a este lançamento for emitida.",
    )

    eh_extra = models.BooleanField(
        default=False,
        help_text="Marque se este lançamento é um serviço extra/pontual fora do combinado base.",
    )

    aviso_vencimento_enviado = models.BooleanField(
        default=False,
        help_text="Marcado quando já foi enviado aviso de vencimento.",
    )
    aviso_nf_enviado = models.BooleanField(
        default=False,
        help_text="Marcado quando já foi enviado aviso de emissão de NF pendente.",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lançamento"
        verbose_name_plural = "Lançamentos"
        ordering = ["-data", "-id"]
        constraints = [
            models.UniqueConstraint(
                condition=Q(item_contrato__isnull=False, competencia__isnull=False),
                fields=["item_contrato", "competencia", "tipo"],
                name="uniq_item_contrato_competencia_tipo",
            ),
        ]


    def clean(self):
        super().clean()
        errors = {}
        # Preenche vinculos a partir do contrato/ItemContrato quando possivel
        if self.item_contrato and not self.contrato:
            self.contrato = self.item_contrato.contrato
        if self.contrato and not self.cliente:
            self.cliente = self.contrato.cliente

        if self.item_contrato and self.contrato and self.item_contrato.contrato_id != self.contrato_id:
            errors["item_contrato"] = "Item do contrato nao pertence ao contrato selecionado."
        if self.contrato and self.cliente and self.contrato.cliente_id != self.cliente_id:
            errors["cliente"] = "Cliente precisa ser o mesmo do contrato."
        if self.categoria_id and self.categoria.tipo != self.tipo:
            errors["categoria"] = "Tipo do lancamento deve casar com o tipo da categoria."
        if self.situacao == "PENDENTE" and not self.data_vencimento:
            errors["data_vencimento"] = "Pendentes precisam de data de vencimento."
        if self.situacao == "PAGO" and self.data_vencimento and self.data_vencimento > timezone.now().date():
            errors["data_vencimento"] = "Nao marque como PAGO com vencimento futuro."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Garante coerencia basica mesmo se full_clean nao for chamado
        if self.item_contrato and not self.contrato:
            self.contrato = self.item_contrato.contrato
        if self.contrato and not self.cliente:
            self.cliente = self.contrato.cliente
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - {self.descricao} - {self.valor}"

    @property
    def tipo_servico_contratado(self):
        """
        Atalho útil: retorna RECORRENTE/ÚNICO se o lançamento estiver
        associado a um ItemContrato; caso contrário, None.
        """
        if self.item_contrato:
            return self.item_contrato.tipo
        return None