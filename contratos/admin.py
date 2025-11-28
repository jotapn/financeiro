from django.contrib import admin
from django.utils.html import format_html
from .models import Servico, Contrato, ItemContrato, ContratoDocumento

# --- INLINES ---
# Permite adicionar Serviços dentro do Contrato
class ItemContratoInline(admin.TabularInline):
    model = ItemContrato
    extra = 0 # Não mostra linhas vazias extras, mantém limpo
    autocomplete_fields = ['servico'] # Requer que ServicoAdmin tenha search_fields
    fields = ('servico', 'tipo', 'valor_acordado', 'observacoes')
    verbose_name = "Item do Contrato"
    verbose_name_plural = "Itens do Contrato (Serviços)"

# Permite anexar arquivos dentro do Contrato
class ContratoDocumentoInline(admin.StackedInline):
    model = ContratoDocumento
    extra = 0
    fields = ('arquivo', 'nome', 'observacoes')

# --- ADMINS ---

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_padrao', 'ativo')
    search_fields = ('nome',) # CRUCIAL para o autocomplete funcionar
    list_filter = ('ativo',)

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 
        'cliente_link', 
        'data_inicio', 
        'data_fim', 
        'dia_vencimento', 
        'status_vigencia'
    )
    list_filter = ('ativo', 'dia_vencimento', 'criado_em')
    search_fields = ('nome', 'cliente__nome')
    
    # Configura os Inlines definidos acima
    inlines = [ItemContratoInline, ContratoDocumentoInline]
    
    # Campo de busca para selecionar cliente (útil se tiver milhares de clientes)
    autocomplete_fields = ['cliente']

    def cliente_link(self, obj):
        # Cria um link clicável para ir direto ao cadastro do cliente
        return format_html('<a href="/admin/clientes/cliente/{}/change/">{}</a>', obj.cliente.id, obj.cliente.nome)
    cliente_link.short_description = "Cliente"

    def status_vigencia(self, obj):
        if obj.vigente_hoje:
            return format_html('<span style="color: green;">✔ Vigente</span>')
        return format_html('<span style="color: red;">✖ Encerrado/Inativo</span>')
    status_vigencia.short_description = "Vigência"