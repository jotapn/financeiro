from django.contrib import admin
from django.utils.html import format_html

from .models import Banco, Categoria, CentroCusto, ContaBancaria, Lancamento


# --- ACOES EM MASSA ---
@admin.action(description='Marcar selecionados como PAGO')
def marcar_como_pago(modeladmin, request, queryset):
    updated = queryset.update(situacao='PAGO')
    modeladmin.message_user(request, f'{updated} lancamentos marcados como PAGO com sucesso.')


@admin.action(description='Marcar selecionados como PENDENTE')
def marcar_como_pendente(modeladmin, request, queryset):
    updated = queryset.update(situacao='PENDENTE')
    modeladmin.message_user(request, f'{updated} lancamentos marcados como PENDENTE.')


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = (
        'descricao',
        'data_vencimento',
        'valor_colorido',
        'tipo',
        'situacao',
        'situacao_icon',
        'conta',
        'nota_fiscal_emitida',
    )
    list_display_links = ('descricao',)
    list_filter = (
        'situacao',
        'tipo',
        'data_vencimento',
        'categoria',
        'conta',
        'nota_fiscal_emitida',
        'centro_custo',
    )
    search_fields = ('descricao', 'cliente__nome', 'contrato__nome')

    list_editable = ('situacao', 'nota_fiscal_emitida', 'data_vencimento')

    date_hierarchy = 'data_vencimento'
    list_per_page = 50
    actions = [marcar_como_pago, marcar_como_pendente]

    fieldsets = (
        ('Basico', {'fields': (('tipo', 'situacao'), 'descricao', 'valor', 'data_vencimento', 'data')}),
        ('Classificacao', {'fields': ('categoria', 'centro_custo', 'conta')}),
        ('Vinculos (Opcional)', {'fields': ('cliente', 'contrato', 'item_contrato')}),
        ('Fiscal e Controle', {'fields': ('nota_fiscal_emitida', 'eh_extra', 'aviso_vencimento_enviado')}),
    )

    def valor_colorido(self, obj):
        color = 'green' if obj.tipo == 'ENTRADA' else 'red'
        return format_html(f'<span style="color: {color}; font-weight: bold;">R$ {obj.valor}</span>')

    valor_colorido.short_description = 'Valor'

    def situacao_icon(self, obj):
        if obj.situacao == 'PAGO':
            return format_html('Pago')
        if obj.situacao == 'CANCELADO':
            return format_html('Cancelado')
        return format_html('Pendente')

    situacao_icon.short_description = 'Situacao'


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'banco', 'tipo_conta', 'exibir_saldo')

    def exibir_saldo(self, obj):
        saldo = obj.saldo_atual
        color = 'blue' if saldo >= 0 else 'red'
        return format_html(f'<span style="color: {color}; font-weight: bold;">R$ {saldo:.2f}</span>')

    exibir_saldo.short_description = "Saldo Atual (Calculado)"


admin.site.register(Categoria)
admin.site.register(CentroCusto)
admin.site.register(Banco)
