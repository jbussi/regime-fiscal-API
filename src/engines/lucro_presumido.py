from src.database.connection import get_db_connection

def calcular_imposto_presumido(faturamento_servicos: float, faturamento_comercio: float, faturamento_acumulado_ano: float, tipo_atividade: str, aliquota_iss_local: float) -> dict:
    """
    Calcula os impostos do Lucro Presumido aplicando os percentuais de presunção oficiais
    da tabela da Receita Federal do Brasil (RFB) e calculando o Adicional do IRPJ.
    """
    faturamento_total = faturamento_servicos + faturamento_comercio
    if faturamento_total <= 0:
        return {
            "imposto_total_mes": 0.0, 
            "aliquota_efetiva_global": 0.0, 
            "detalhe": {}
        }

    # 1. Recupera as alíquotas fixas e limites do banco de dados
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT parametro_nome, valor FROM parametros_fiscais_fixos WHERE regime = 'LUCRO_PRESUMIDO'")
        parametros = dict(cursor.fetchall())

    # 2. Define os percentuais de presunção (IRPJ e CSLL) baseado no tipo de atividade
    # Fallback padrão (SERVICOS_GERAIS / PROFISSÕES REGULAMENTADAS)
    p_irpj = parametros.get('presuncao_irpj_servicos_padrao', 0.32)
    p_csll = parametros.get('presuncao_csll_servicos_padrao', 0.32)

    # Aplicação cirúrgica das regras da tabela da RFB
    if tipo_atividade == "COMERCIO" or tipo_atividade == "INDUSTRIALIZACAO":
        p_irpj = parametros.get('presuncao_irpj_comercio_industria', 0.08)
        p_csll = parametros.get('presuncao_csll_comercio_industria', 0.12)
        
    elif tipo_atividade == "TRANSPORTE_CARGAS":
        p_irpj = parametros.get('presuncao_irpj_transporte_cargas', 0.08)
        p_csll = parametros.get('presuncao_csll_transporte_cargas', 0.12)
        
    elif tipo_atividade == "SERVICOS_GERAIS":
        p_csll = parametros.get('presuncao_csll_servicos_padrao', 0.32)
        # Regra de Ouro (Item 11): Se faturamento acumulado no ano for <= R$ 120.000, IRPJ cai para 16%
        limite_120k = parametros.get('limite_anual_servicos_reduzido', 120000.00)
        if faturamento_acumulado_ano <= limite_120k:
            p_irpj = parametros.get('presuncao_irpj_servicos_reduzido', 0.16)
        else:
            p_irpj = parametros.get('presuncao_irpj_servicos_padrao', 0.32)

    # 3. Cálculo das Bases de Cálculo Estacionárias (Presunção do Lucro)
    # Separamos serviços e comércio para o caso de empresas mistas
    base_irpj = (faturamento_servicos * p_irpj) + (faturamento_comercio * parametros.get('presuncao_irpj_comercio_industria', 0.08))
    base_csll = (faturamento_servicos * p_csll) + (faturamento_comercio * parametros.get('presuncao_csll_comercio_industria', 0.12))

    # 4. Cálculo dos Impostos Federais sobre o Lucro Estimado
    irpj_base = base_irpj * parametros.get('aliquota_irpj_base', 0.15)
    csll = base_csll * parametros.get('aliquota_csll', 0.09)

    # Regra do Adicional do IRPJ: 10% sobre a parcela do lucro presumido mensal que exceder R$ 20.000,00
    limite_adicional = parametros.get('limite_mensal_adicional_irpj', 20000.00)
    irpj_adicional = 0.0
    if base_irpj > limite_adicional:
        irpj_adicional = (base_irpj - limite_adicional) * parametros.get('aliquota_irpj_adicional', 0.10)

    irpj_total = irpj_base + irpj_adicional

    # 5. Cálculo dos Impostos Mensais sobre o Faturamento Bruto (PIS/COFINS Cumulativos + ISS)
    pis = faturamento_total * parametros.get('aliquota_pis', 0.0065)
    cofins = faturamento_total * parametros.get('aliquota_cofins', 0.0300)
    iss = faturamento_servicos * aliquota_iss_local

    # 6. Consolidação dos Resultados
    imposto_total_mes = irpj_total + csll + pis + cofins + iss
    aliquota_efetiva_global = (imposto_total_mes / faturamento_total) * 100 if faturamento_total > 0 else 0.0

    return {
        "imposto_total_mes": round(imposto_total_mes, 2),
        "aliquota_efetiva_global": round(aliquota_efetiva_global, 4),
        "detalhe": {
            "irpj_base": round(irpj_base, 2),
            "irpj_adicional": round(irpj_adicional, 2),
            "irpj_total": round(irpj_total, 2),
            "csll": round(csll, 2),
            "pis_cumulativo": round(pis, 2),
            "cofins_cumulativo": round(cofins, 2),
            "iss": round(iss, 2),
            "base_calculo_presumida_irpj": round(base_irpj, 2),
            "base_calculo_presumida_csll": round(base_csll, 2),
            "percentual_presuncao_irpj_aplicado": round(p_irpj * 100, 2),
            "percentual_presuncao_csll_aplicado": round(p_csll * 100, 2)
        }
    }