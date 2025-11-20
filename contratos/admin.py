from django.contrib import admin
from .models import Servico, Contrato, ItemContrato, ContratoDocumento


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor_padrao", "ativo", "criado_em")
    search_fields = ("nome", "descricao")
    list_filter = ("ativo",)
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(ItemContrato)
class ItemContratoAdmin(admin.ModelAdmin):
    list_display = ("contrato", "servico", "tipo", "valor_acordado")
    list_filter = ("tipo", "contrato")
    search_fields = ("contrato__nome", "servico__nome")
    autocomplete_fields = ("contrato", "servico")


class ItemContratoInline(admin.TabularInline):
    model = ItemContrato
    extra = 0
    autocomplete_fields = ("servico",)
    fields = ("servico", "tipo", "valor_acordado", "observacoes")
    show_change_link = True


class ContratoDocumentoInline(admin.TabularInline):
    model = ContratoDocumento
    extra = 0
    fields = ("arquivo", "nome", "observacoes", "criado_em")
    readonly_fields = ("criado_em",)


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "cliente",
        "data_inicio",
        "data_fim",
        "dia_vencimento",
        "ativo",
    )
    list_filter = ("ativo", "data_inicio", "data_fim")
    search_fields = ("nome", "cliente__nome")
    date_hierarchy = "data_inicio"
    inlines = [ItemContratoInline, ContratoDocumentoInline]
    readonly_fields = ("criado_em", "atualizado_em")
