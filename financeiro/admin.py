from django.contrib import admin
from .models import (
    Categoria,
    CentroCusto,
    Banco,
    ContaBancaria,
    Lancamento,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo")
    list_filter = ("tipo",)
    search_fields = ("nome",)


@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "identificador_layout_extrato", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "codigo")


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "banco",
        "tipo_conta",
        "agencia",
        "numero",
        "saldo_inicial",
        "saldo_atual",
        "criado_em",
    )
    list_filter = ("banco", "tipo_conta")
    search_fields = ("nome", "banco__nome", "numero")
    readonly_fields = ("saldo_atual", "criado_em", "atualizado_em")

@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "descricao",
        "valor",
        "data",
        "data_vencimento",
        "situacao",
        "conta",
        "categoria",
        "cliente",
        "contrato",
        "item_contrato",
        "nota_fiscal_emitida",
        "eh_extra",
    )
    list_filter = (
        "tipo",
        "situacao",
        "conta",
        "categoria",
        "nota_fiscal_emitida",
        "eh_extra",
    )
    search_fields = (
        "descricao",
        "cliente__nome",
        "contrato__nome",
    )
    date_hierarchy = "data"
    ordering = ("-data", "-id")
    autocomplete_fields = ("cliente", "contrato", "item_contrato")
    readonly_fields = (
        "criado_em",
        "atualizado_em",
        "aviso_vencimento_enviado",
        "aviso_nf_enviado",
    )
