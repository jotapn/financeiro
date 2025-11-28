from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import FileExtensionValidator

class Servico(models.Model):
    """
    Catálogo de serviços que você oferece (ex: Ensaio Fotográfico, Cobertura de Evento).
    """
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    valor_padrao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Valor padrão sugerido para este serviço.",
    )

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"

    def __str__(self):
        """
        Provide a readable string representation of the service using its name.
        
        Returns:
            str: The value of the `nome` field.
        """
        return self.nome

class Contrato(models.Model):
    """
    Contrato entre você e um cliente.
    Pode ter vários itens (serviços) dentro, recorrentes ou únicos.
    """

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.CASCADE,
        related_name="contratos",
    )
    nome = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nome interno do contrato. Ex: Contrato 2025 - Loja X.",
    )
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    dia_vencimento = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Dia do mês para cobrança dos serviços recorrentes (1 a 31).",
        null=True,
        blank=True,
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        # Se não tiver nome, usa padrão Contrato {id} - {cliente}
        """
        Return the human-readable representation of the contract.
        
        Returns:
            str: The contract's `nome` if set; otherwise `Contrato {id} - {cliente_name}` when the instance has an `id`. If the contract has no associated client, `cliente_name` will be `"sem cliente"`.
        """
        if self.nome:
            return self.nome
        cliente_nome = self.cliente.nome if self.cliente_id else "sem cliente"
        if self.id:
            return f"Contrato {self.id} - {cliente_nome}"
    @property
    def vigente_hoje(self):
        """
        Determine whether the contract is active today.
        
        Checks the contract's `ativo` flag and whether today's date falls on or after `data_inicio`
        and on or before `data_fim` if `data_fim` is set.
        
        Returns:
            bool: `True` if the contract is active today, `False` otherwise.
        """
        from django.utils import timezone
        hoje = timezone.now().date()
        if self.data_fim:
            return self.ativo and self.data_inicio <= hoje <= self.data_fim
        return self.ativo and self.data_inicio <= hoje


class ItemContrato(models.Model):
    """
    Associação entre Contrato e Serviço.
    É aqui que você define se o serviço é RECORRENTE ou ÚNICO para aquele contrato.
    """

    TIPO_SERVICO_CHOICES = (
        ("RECORRENTE", "Recorrente"),
        ("UNICO", "Único"),
    )

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="itens",
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name="itens_contrato",
    )
    tipo = models.CharField(
        max_length=11,
        choices=TIPO_SERVICO_CHOICES,
        help_text="Define se, neste contrato, o serviço é recorrente ou pontual.",
    )
    valor_acordado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Valor combinado para este serviço neste contrato.",
    )
    observacoes = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de contrato"
        verbose_name_plural = "Itens de contrato"

    def __str__(self):
        """
        Return a human-readable representation of the contract item combining service name, type, and contract.
        
        Returns:
            str: A string in the format "<service name> (<tipo>) - <contrato>" where `<service name>` is `servico.nome`, `<tipo>` is the item's `tipo` value, and `<contrato>` is the associated `Contrato`'s string representation.
        """
        return f"{self.servico.nome} ({self.tipo}) - {self.contrato}"


class ContratoDocumento(models.Model):
    """
    Documentos anexados a um contrato.
    Ex: PDF do contrato assinado, aditivos, comprovantes etc.
    """

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="documentos",
    )
    arquivo = models.FileField(
        upload_to="contratos/%Y/%m/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        help_text="Envie o PDF assinado ou outro documento relacionado ao contrato.",
    )
    nome = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nome amigável do documento (opcional).",
    )
    observacoes = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento de contrato"
        verbose_name_plural = "Documentos de contrato"

    def __str__(self):
        """
        Human-readable representation of the document.
        
        Returns:
            str: The display name — `nome` if set; otherwise `"Documento #{id} - {contrato}"` when the instance has an `id`; otherwise `"Documento (novo) - {contrato}"`.
        """
        if self.nome:
            return self.nome
        if self.id:
            return f"Documento #{self.id} - {self.contrato}"
        return f"Documento (novo) - {self.contrato}"