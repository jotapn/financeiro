from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Colunas visíveis na lista
    list_display = ('nome', 'tipo_pessoa', 'documento_formatado', 'email', 'telefone', 'ativo', 'status_icon')

    # Filtros laterais
    list_filter = ('ativo', 'tipo_pessoa', 'criado_em')

    # Campo de busca (permite buscar por nome ou documento)
    search_fields = ('nome', 'documento', 'email')

    # Permite editar o status sem entrar no cadastro
    list_editable = ('ativo',)

    # Paginação (útil se tiver muitos clientes)
    list_per_page = 25

    fieldsets = (
        ('Dados Principais', {'fields': ('nome', 'tipo_pessoa', 'documento', 'ativo')}),
        ('Contato', {'fields': ('email', 'telefone')}),
    )

    def status_icon(self, obj):
        return "Ativo" if obj.ativo else "Inativo"

    status_icon.short_description = 'Status'

    def documento_formatado(self, obj):
        # Exibe o documento cru; formatação pode ser adicionada depois se necessário.
        return obj.documento

    documento_formatado.short_description = 'Documento'
