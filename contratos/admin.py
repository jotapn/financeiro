from decimal import Decimal

from django.contrib import admin
from django.db.models import Q, Sum
from django.urls import reverse
from django.utils.html import format_html

from .models import Contrato, ContratoDocumento, ItemContrato, Servico


# --- INLINES ---
class ItemContratoInline(admin.TabularInline):
    model = ItemContrato
    extra = 0
    autocomplete_fields = ["servico"]
    fields = ("servico", "tipo", "valor_acordado", "observacoes")
    verbose_name = "Item do Contrato"
    verbose_name_plural = "Itens do Contrato (Servicos)"


class ContratoDocumentoInline(admin.StackedInline):
    model = ContratoDocumento
    extra = 0
    fields = ("arquivo", "nome", "observacoes")


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor_padrao", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "cliente_link",
        "data_inicio",
        "data_fim",
        "dia_vencimento",
        "status_vigencia",
        "total_pendente",
        "total_pago",
        "link_lancamentos",
    )
    list_filter = ("ativo", "dia_vencimento", "criado_em")
    search_fields = ("nome", "cliente__nome")
    inlines = [ItemContratoInline, ContratoDocumentoInline]
    autocomplete_fields = ["cliente"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            total_pendente=Sum("lancamentos__valor", filter=Q(lancamentos__situacao="PENDENTE")),
            total_pago=Sum("lancamentos__valor", filter=Q(lancamentos__situacao="PAGO")),
        )

    def cliente_link(self, obj):
        return format_html('<a href="/admin/clientes/cliente/{}/change/">{}</a>', obj.cliente.id, obj.cliente.nome)

    cliente_link.short_description = "Cliente"

    def status_vigencia(self, obj):
        if obj.vigente_hoje:
            return format_html('<span style="color: green;">Vigente</span>')
        return format_html('<span style="color: red;">Encerrado/Inativo</span>')

    status_vigencia.short_description = "Vigencia"

    def total_pendente(self, obj):
        valor = obj.total_pendente or Decimal("0")
        return format_html('<span style="color: red;">R$ {:.2f}</span>', valor)

    total_pendente.short_description = "Pendentes"

    def total_pago(self, obj):
        valor = obj.total_pago or Decimal("0")
        return format_html('<span style="color: green;">R$ {:.2f}</span>', valor)

    total_pago.short_description = "Pagos"

    def link_lancamentos(self, obj):
        url = f"{reverse('admin:financeiro_lancamento_changelist')}?contrato__id__exact={obj.id}"
        return format_html('<a href="{}">Ver lancamentos</a>', url)

    link_lancamentos.short_description = "Lancamentos"
