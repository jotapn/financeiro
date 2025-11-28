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
        if self.nome:
            return self.nome
        cliente_nome = self.cliente.nome if self.cliente_id else "sem cliente"
        if self.id:
            return f"Contrato {self.id} - {cliente_nome}"
    @property
    def vigente_hoje(self):
        """
        Exemplo de helper: verifica se o contrato está vigente hoje.
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
        return f"{self.servico.nome} ({self.tipo}) - {self.contrato}"


def contrato_documento_upload_to(instance, filename):
    """
    Organiza uploads por contrato em contratos/documentos/<contrato_id>/<arquivo>.
    Usa 'sem-contrato' como fallback para casos sem FK definida.
    """
    contrato_id = instance.contrato_id or "sem-contrato"
    return f"contratos/documentos/{contrato_id}/{filename}"


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
        upload_to=contrato_documento_upload_to,
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
        if self.nome:
            return self.nome
        if self.id:
            return f"Documento #{self.id} - {self.contrato}"
        return f"Documento (novo) - {self.contrato}"
