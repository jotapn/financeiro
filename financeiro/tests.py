from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from clientes.models import Cliente
from contratos.models import Contrato, ItemContrato, Servico
from financeiro.models import Banco, Categoria, ContaBancaria, Lancamento
from financeiro.services import gerar_lancamentos_recorrentes


class LancamentoModelTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_pessoa="PF",
            nome="Cliente Teste",
            documento="39053344705",
        )
        self.banco = Banco.objects.create(nome="Banco X")
        self.conta = ContaBancaria.objects.create(banco=self.banco, nome="Conta X")
        self.cat_entrada = Categoria.objects.create(nome="Receita", tipo="ENTRADA")
        self.cat_saida = Categoria.objects.create(nome="Despesa", tipo="SAIDA")
        self.contrato = Contrato.objects.create(
            cliente=self.cliente,
            data_inicio=date(2025, 1, 1),
            dia_vencimento=10,
        )
        self.servico = Servico.objects.create(nome="Servico Recorrente")
        self.item = ItemContrato.objects.create(
            contrato=self.contrato,
            servico=self.servico,
            tipo="RECORRENTE",
            valor_acordado=Decimal("100.00"),
        )

    def test_item_contrato_deve_pertencer_ao_contrato(self):
        outro_contrato = Contrato.objects.create(
            cliente=self.cliente,
            data_inicio=date(2025, 1, 1),
            dia_vencimento=5,
        )
        lanc = Lancamento(
            tipo="ENTRADA",
            contrato=outro_contrato,
            item_contrato=self.item,
            categoria=self.cat_entrada,
            conta=self.conta,
            descricao="Teste incoerente",
            valor=Decimal("10"),
            data=date.today(),
            data_vencimento=date.today(),
        )
        with self.assertRaises(ValidationError):
            lanc.full_clean()

    def test_tipo_categoria_deve_bater(self):
        lanc = Lancamento(
            tipo="SAIDA",
            categoria=self.cat_entrada,
            conta=self.conta,
            descricao="Tipo errado",
            valor=Decimal("10"),
            data=date.today(),
            data_vencimento=date.today(),
        )
        with self.assertRaises(ValidationError):
            lanc.full_clean()

    def test_pendente_requer_vencimento(self):
        lanc = Lancamento(
            tipo="ENTRADA",
            categoria=self.cat_entrada,
            conta=self.conta,
            descricao="Sem vencimento",
            valor=Decimal("10"),
            data=date.today(),
        )
        with self.assertRaises(ValidationError):
            lanc.full_clean()

    def test_pago_nao_pode_ter_vencimento_futuro(self):
        futura = date.today() + timedelta(days=5)
        lanc = Lancamento(
            tipo="ENTRADA",
            categoria=self.cat_entrada,
            conta=self.conta,
            descricao="Futuro",
            valor=Decimal("10"),
            data=date.today(),
            data_vencimento=futura,
            situacao="PAGO",
        )
        with self.assertRaises(ValidationError):
            lanc.full_clean()

    def test_cliente_preenchido_a_partir_do_contrato_no_save(self):
        lanc = Lancamento(
            tipo="ENTRADA",
            contrato=self.contrato,
            categoria=self.cat_entrada,
            conta=self.conta,
            descricao="Auto cliente",
            valor=Decimal("10"),
            data=date.today(),
            data_vencimento=date.today(),
        )
        lanc.save()
        self.assertEqual(lanc.cliente, self.cliente)

    def test_saldo_atual_usa_decimal(self):
        Lancamento.objects.create(
            tipo="ENTRADA",
            categoria=self.cat_entrada,
            conta=self.conta,
            descricao="Entrada",
            valor=Decimal("100.50"),
            data=date.today(),
            data_vencimento=date.today(),
            situacao="PAGO",
        )
        Lancamento.objects.create(
            tipo="SAIDA",
            categoria=self.cat_saida,
            conta=self.conta,
            descricao="Saida",
            valor=Decimal("40.30"),
            data=date.today(),
            data_vencimento=date.today(),
            situacao="PAGO",
        )
        self.assertEqual(self.conta.saldo_atual, Decimal("60.20"))


class GeracaoRecorrenteTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_pessoa="PF",
            nome="Cliente Recorrente",
            documento="12312312312",
        )
        self.banco = Banco.objects.create(nome="Banco Y")
        self.conta = ContaBancaria.objects.create(banco=self.banco, nome="Conta Y")
        self.cat_entrada = Categoria.objects.create(nome="Receita", tipo="ENTRADA")
        self.contrato = Contrato.objects.create(
            cliente=self.cliente,
            data_inicio=date(2025, 1, 1),
            dia_vencimento=15,
        )
        self.servico = Servico.objects.create(nome="Servico R")
        self.item = ItemContrato.objects.create(
            contrato=self.contrato,
            servico=self.servico,
            tipo="RECORRENTE",
            valor_acordado=Decimal("200.00"),
        )

    def test_gera_lancamento_por_competencia_sem_duplicar(self):
        referencia = date(2025, 2, 20)
        criados = gerar_lancamentos_recorrentes(
            categoria_padrao=self.cat_entrada,
            conta_padrao=self.conta,
            data_referencia=referencia,
        )
        self.assertEqual(len(criados), 1)
        lanc = criados[0]
        self.assertEqual(lanc.item_contrato, self.item)
        self.assertEqual(lanc.competencia, date(2025, 2, 1))
        self.assertEqual(lanc.data_vencimento, date(2025, 2, 15))
        # Segunda chamada não deve criar novamente
        criados2 = gerar_lancamentos_recorrentes(
            categoria_padrao=self.cat_entrada,
            conta_padrao=self.conta,
            data_referencia=referencia,
        )
        self.assertEqual(len(criados2), 0)
