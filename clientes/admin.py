from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo_pessoa",
        "documento",
        "email",
        "telefone",
        "ativo",
        "criado_em",
    )
    list_filter = ("tipo_pessoa", "ativo")
    search_fields = ("nome", "documento", "email", "telefone")
    ordering = ("nome",)
    readonly_fields = ("criado_em", "atualizado_em")
