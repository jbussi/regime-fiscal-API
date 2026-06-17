import sqlite3
from typing import Dict, Any

def obter_parametro_real(parametro_nome: str, db_path: str = "database.db") -> float:
    """
    Busca um parâmetro específico do Lucro Real no banco de dados.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT valor 
        FROM parametros_fiscais_fixos 
        WHERE regime = 'LUCRO_REAL' AND parametro_nome = ?
        LIMIT 1;
    """
    cursor.execute(query, (parametro_nome,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError(f"Parâmetro fiscal '{parametro_nome}' não encontrado para o Lucro Real.")
    return float(row[0])

def calcular_imposto_real(
    faturamento_bruto: float,
    opex_dedutivel: float,
    custos_com_direito_a_credito: float,
    compras_capex_computadores: float,
    db_path: str = "database.db"
) -> Dict[str, Any]:
    """
    Executa a apuração completa da DRE e dos tributos no regime do Lucro Real.
    Considera créditos não cumulativos e depreciação acumulada do mês.
    """
    if faturamento_bruto <= 0:
        return {
            "faturamento_bruto": 0.0, "lucro_liquido_tributavel": 0.0,
            "pis_liquido": 0.0, "cofins_liquido": 0.0, "csll": 0.0, "irpj_total": 0.0,
            "imposto_total_mes": 0.0, "aliquota_efetiva_global": 0.0, "mensagem": "Sem faturamento."
        }

    # 1. Buscar parâmetros da lei no banco de dados
    aliq_pis = obter_parametro_real("aliquota_pis", db_path)
    aliq_cofins = obter_parametro_real("aliquota_cofins", db_path)
    cred_pis = obter_parametro_real("credito_pis_custos", db_path)
    cred_cofins = obter_parametro_real("credito_cofins_custos", db_path)
    aliq_csll = obter_parametro_real("aliquota_csll", db_path)
    aliq_irpj_base = obter_parametro_real("aliquota_irpj_base", db_path)
    aliq_irpj_adic = obter_parametro_real("aliquota_irpj_adicional", db_path)
    limite_adicional = obter_parametro_real("limite_mensal_adicional_irpj", db_path)

    # 2. Camada A: PIS e COFINS Não Cumulativos (Débitos - Créditos)
    pis_debito = faturamento_bruto * aliq_pis
    cofins_debito = faturamento_bruto * aliq_cofins
    
    pis_credito = custos_com_direito_a_credito * cred_pis
    cofins_credito = custos_com_direito_a_credito * cred_cofins
    
    # Imposto não cumulativo não pode ser negativo (se der crédito maior, acumula para o mês seguinte)
    pis_liquido = max(0.0, pis_debito - pis_credito)
    cofins_liquido = max(0.0, cofins_debito - cofins_credito)

    # 3. Cálculo da Depreciação do CAPEX (Notebooks/TI = 20% ao ano -> 1.6667% ao mês)
    taxa_depreciacao_mensal = 0.016667
    depreciacao_mes = compras_capex_computadores * taxa_depreciacao_mensal

    # 4. Construção da DRE Contábil para achar o Lucro Líquido Real
    # O PIS e COFINS líquidos entram reduzindo o resultado operacional
    total_deducoes_operacionais = opex_dedutivel + custos_com_direito_a_credito + depreciacao_mes + pis_liquido + cofins_liquido
    lucro_antes_impostos = faturamento_bruto - total_deducoes_operacionais

    # 5. Camada B: IRPJ e CSLL (Se houver prejuízo, imposto é zero!)
    if lucro_antes_impostos <= 0:
        return {
            "faturamento_bruto": round(faturamento_bruto, 2),
            "lucro_liquido_tributavel": round(max(0.0, lucro_antes_impostos), 2),
            "depreciacao_deduzida": round(depreciacao_mes, 2),
            "impostos_detalhados": {
                "pis": round(pis_liquido, 2),
                "cofins": round(cofins_liquido, 2),
                "csll": 0.0, "irpj_base": 0.0, "irpj_adicional": 0.0, "irpj_total": 0.0
            },
            "imposto_total_mes": round(pis_liquido + cofins_liquido, 2),
            "aliquota_efetiva_global": round(((pis_liquido + cofins_liquido) / faturamento_bruto) * 100, 4),
            "mensagem": "Estratégia Eficiente: Prejuízo Contábil/Lucro Zero. Isento de IRPJ e CSLL!"
        }

    # Se gerou lucro, aplica a tributação com o teste do adicional
    csll_total = lucro_antes_impostos * aliq_csll
    irpj_base = lucro_antes_impostos * aliq_irpj_base
    
    irpj_adicional = 0.0
    excedente_lucro = lucro_antes_impostos - limite_adicional
    if excedente_lucro > 0:
        irpj_adicional = excedente_lucro * aliq_irpj_adic
        
    irpj_total = irpj_base + irpj_adicional
    imposto_total = pis_liquido + cofins_liquido + csll_total + irpj_total
    aliquota_efetiva = (imposto_total / faturamento_bruto) * 100

    return {
        "faturamento_bruto": round(faturamento_bruto, 2),
        "lucro_liquido_tributavel": round(lucro_antes_impostos, 2),
        "depreciacao_deduzida": round(depreciacao_mes, 2),
        "impostos_detalhados": {
            "pis": round(pis_liquido, 2),
            "cofins": round(cofins_liquido, 2),
            "csll": round(csll_total, 2),
            "irpj_base": round(irpj_base, 2),
            "irpj_adicional": round(irpj_adicional, 2),
            "irpj_total": round(irpj_total, 2)
        },
        "imposto_total_mes": round(imposto_total, 2),
        "aliquota_efetiva_global": round(aliquota_efetiva, 4),
        "mensagem": "Empresa gerou Lucro Real e foi tributada sobre o resultado líquido."
    }