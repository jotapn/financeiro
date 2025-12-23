from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import List, Optional

from django.db import transaction
from django.utils import timezone

from contratos.models import ItemContrato
from .models import Categoria, ContaBancaria, Lancamento


def _data_vencimento_para_mes(dia_vencimento: int, referencia: date) -> date:
    ultimo_dia = calendar.monthrange(referencia.year, referencia.month)[1]
    dia = min(dia_vencimento, ultimo_dia)
    return date(referencia.year, referencia.month, dia)


@transaction.atomic
def gerar_lancamentos_recorrentes(
    categoria_padrao: Categoria,
    conta_padrao: ContaBancaria,
    centro_custo_padrao: Optional[int] = None,
    data_referencia: Optional[date] = None,
) -> List[Lancamento]:
    """
    Gera lançamentos de ENTRADA para todos os ItemContrato recorrentes, uma vez por competência.
    - categoria_padrao/conta_padrao são obrigatórios para preencher os lançamentos gerados.
    - data_referencia define o mês de competência (default = hoje).
    """
    if not categoria_padrao or not conta_padrao:
        raise ValueError("categoria_padrao e conta_padrao são obrigatórios para gerar recorrências.")

    hoje = timezone.now().date()
    referencia = data_referencia or hoje
    competencia = date(referencia.year, referencia.month, 1)

    criados: List[Lancamento] = []

    itens = (
        ItemContrato.objects.select_related("contrato", "contrato__cliente", "servico")
        .filter(tipo="RECORRENTE", contrato__ativo=True)
        .exclude(contrato__dia_vencimento__isnull=True)
    )

    for item in itens:
        contrato = item.contrato
        vencimento = _data_vencimento_para_mes(contrato.dia_vencimento, referencia)

        ja_existe = Lancamento.objects.filter(
            item_contrato=item,
            competencia=competencia,
            tipo="ENTRADA",
        ).exists()
        if ja_existe:
            continue

        lancamento = Lancamento(
            tipo="ENTRADA",
            cliente=contrato.cliente,
            contrato=contrato,
            item_contrato=item,
            categoria=categoria_padrao,
            centro_custo_id=centro_custo_padrao,
            conta=conta_padrao,
            descricao=f"{item.servico.nome} - {competencia:%m/%Y}",
            valor=item.valor_acordado,
            competencia=competencia,
            data=competencia,
            data_vencimento=vencimento,
            situacao="PENDENTE",
            nota_fiscal_emitida=False,
            eh_extra=False,
        )
        lancamento.full_clean()
        lancamento.save()
        criados.append(lancamento)

    return criados
