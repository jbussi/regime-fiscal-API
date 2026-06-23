from src.database.connection import get_db_connection

def calcular_imposto_real(faturamento_bruto: float, opex_dedutivel: float, custos_com_direito_a_credito: float, compras_capex_computadores: float, folha_mensal_atual: float) -> dict:
    """
    Calcula o imposto do Lucro Real (Regime Não Cumulativo).
    Computa débitos e créditos de PIS/COFINS, encargos de folha e depreciação de ativos.
    """
    if faturamento_bruto <= 0:
        return {
            "imposto_total_mes": 0.0, 
            "aliquota_efetiva_global": 0.0, 
            "detalhe": {}
        }

    # 1. Recupera as alíquotas fixas do banco de dados
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT parametro_nome, valor FROM parametros_fiscais_fixos WHERE regime = 'LUCRO_REAL'")
        parametros = dict(cursor.fetchall())

    # 2. PIS e COFINS Não Cumulativos (Débito - Crédito)
    pis_debito = faturamento_bruto * parametros.get('aliquota_pis', 0.0165)
    cofins_debito = faturamento_bruto * parametros.get('aliquota_cofins', 0.0760)

    pis_credito = custos_com_direito_a_credito * parametros.get('credito_pis_custos', 0.0165)
    cofins_credito = custos_com_direito_a_credito * parametros.get('credito_cofins_custos', 0.0760)

    pis_final = max(0.0, pis_debito - pis_credito)
    cofins_final = max(0.0, cofins_debito - cofins_credito)

    # 3. Encargos sobre a Folha de Pagamento (INSS Patronal + RAT + Terceiros)
    aliquota_folha_cheia = parametros.get('aliquota_inss_patronal', 0.2000) + parametros.get('aliquota_rat_terceiros_estimado', 0.0580)
    inss_folha = folha_mensal_atual * aliquota_folha_cheia

    # 4. Cálculo da Depreciação Mensal (Ativos CAPEX)
    depreciacao_mes = compras_capex_computadores * parametros.get('taxa_depreciacao_mensal_computadores', 0.016667)

    # 5. Base de Cálculo do IRPJ e CSLL (Lucro Líquido Real)
    total_despesas_dedutiveis = opex_dedutivel + inss_folha + depreciacao_mes + pis_final + cofins_final
    lucro_real_periodo = faturamento_bruto - total_despesas_dedutiveis

    irpj_total = 0.0
    csll = 0.0

    # Só há incidência se houver lucro real. Se houver prejuízo, zera a base fiscal.
    if lucro_real_periodo > 0:
        irpj_base = lucro_real_periodo * parametros.get('aliquota_irpj_base', 0.1500)
        csll = lucro_real_periodo * parametros.get('aliquota_csll', 0.0900)

        # Adicional de IRPJ (10% sobre o que passar de R$ 20.000 no mês)
        limite_adicional = parametros.get('limite_mensal_adicional_irpj', 20000.00)
        irpj_adicional = 0.0
        if lucro_real_periodo > limite_adicional:
            irpj_adicional = (lucro_real_periodo - limite_adicional) * parametros.get('aliquota_irpj_adicional', 0.1000)
        
        irpj_total = irpj_base + irpj_adicional
    else:
        lucro_real_periodo = 0.0

    # 6. Consolidação da carga tributária
    imposto_total_mes = irpj_total + csll + pis_final + cofins_final + inss_folha
    aliquota_efetiva_global = (imposto_total_mes / faturamento_bruto) * 100

    return {
        "imposto_total_mes": round(imposto_total_mes, 2),
        "aliquota_efetiva_global": round(aliquota_efetiva_global, 4),
        "detalhe": {
            "lucro_real_calculado": round(lucro_real_periodo, 2),
            "irpj_total": round(irpj_total, 2),
            "csll": round(csll, 2),
            "pis_nao_cumulativo": round(pis_final, 2),
            "cofins_nao_cumulativo": round(cofins_final, 2),
            "inss_patronal_folha": round(inss_folha, 2),
            "depreciacao_deduzida": round(depreciacao_mes, 2)
        }
    }