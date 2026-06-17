import sqlite3
from typing import Dict, Any

def obter_parametro_presumido(parametro_nome: str, db_path: str = "database.db") -> float:
    """
    Busca um parâmetro específico do Lucro Presumido no banco de dados.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT valor 
        FROM parametros_fiscais_fixos 
        WHERE regime = 'LUCRO_PRESUMIDO' AND parametro_nome = ?
        LIMIT 1;
    """
    cursor.execute(query, (parametro_nome,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError(f"Parâmetro fiscal '{parametro_nome}' não encontrado para o Lucro Presumido.")
    return float(row[0])

def calcular_imposto_presumido(
    faturamento_servicos: float,
    faturamento_comercio: float,
    db_path: str = "database.db"
) -> Dict[str, Any]:
    """
    Executa a apuração completa mensal dos tributos federais no regime do Lucro Presumido.
    """
    faturamento_total = faturamento_servicos + faturamento_comercio
    
    if faturamento_total <= 0:
        return {
            "faturamento_total": 0.0,
            "pis": 0.0, "cofins": 0.0, "csll": 0.0, "irpj_base": 0.0, "irpj_adicional": 0.0,
            "imposto_total": 0.0, "aliquota_efetiva_global": 0.0
        }

    # 1. Carregar alíquotas e regras do banco de dados
    p_irpj_servicos = obter_parametro_presumido("presuncao_irpj_servicos", db_path)
    p_csll_servicos = obter_parametro_presumido("presuncao_csll_servicos", db_path)
    p_irpj_comercio = obter_parametro_presumido("presuncao_irpj_comercio", db_path)
    p_csll_comercio = obter_parametro_presumido("presuncao_csll_comercio", db_path)
    
    aliq_pis = obter_parametro_presumido("aliquota_pis", db_path)
    aliq_cofins = obter_parametro_presumido("aliquota_cofins", db_path)
    aliq_csll = obter_parametro_presumido("aliquota_csll", db_path)
    aliq_irpj_base = obter_parametro_presumido("aliquota_irpj_base", db_path)
    aliq_irpj_adic = obter_parametro_presumido("aliquota_irpj_adicional", db_path)
    limite_adicional = obter_parametro_presumido("limite_mensal_adicional_irpj", db_path)

    # 2. Cálculo do PIS e COFINS (Cumulativo sobre o Faturamento Total)
    pis_total = faturamento_total * aliq_pis
    cofins_total = faturamento_total * aliq_cofins

    # 3. Cálculo das Bases de Presunção (onde a mágica da estimativa acontece)
    base_presumida_irpj = (faturamento_servicos * p_irpj_servicos) + (faturamento_comercio * p_irpj_comercio)
    base_presumida_csll = (faturamento_servicos * p_csll_servicos) + (faturamento_comercio * p_csll_comercio)

    # 4. Cálculo da CSLL (9% sobre a base presumida da CSLL)
    csll_total = base_presumida_csll * aliq_csll

    # 5. Cálculo do IRPJ Base (15% sobre a base presumida do IRPJ)
    irpj_base = base_presumida_irpj * aliq_irpj_base

    # 6. Jogo Estratégico do Adicional de IRPJ (+10% sobre o que ultrapassa R$ 20k/mês de base)
    irpj_adicional = 0.0
    excedente_adicional = base_presumida_irpj - limite_adicional
    if excedente_adicional > 0:
        irpj_adicional = excedente_adicional * aliq_irpj_adic

    irpj_total = irpj_base + irpj_adicional
    imposto_total = pis_total + cofins_total + csll_total + irpj_total
    aliquota_efetiva = (imposto_total / faturamento_total) * 100

    return {
        "faturamento_total": round(faturamento_total, 2),
        "faturamento_detalhado": {
            "servicos": round(faturamento_servicos, 2),
            "comercio": round(faturamento_comercio, 2)
        },
        "bases_presumidas": {
            "irpj": round(base_presumida_irpj, 2),
            "csll": round(base_presumida_csll, 2)
        },
        "impostos_detalhados": {
            "pis": round(pis_total, 2),
            "cofins": round(cofins_total, 2),
            "csll": round(csll_total, 2),
            "irpj_base": round(irpj_base, 2),
            "irpj_adicional": round(irpj_adicional, 2),
            "irpj_total": round(irpj_total, 2)
        },
        "imposto_total_mes": round(imposto_total, 2),
        "aliquota_efetiva_global": round(aliquota_efetiva, 4)
    }