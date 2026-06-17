import sqlite3
from typing import Dict, Any

def calcular_fator_r(folha_acumulada_12m: float, rbt12: float) -> float:
    """
    Calcula a relação percentual entre a folha de pagamento e o faturamento dos últimos 12 meses.
    """
    if rbt12 <= 0:
        return 0.0
    return (folha_acumulada_12m / rbt12) * 100

def obter_faixa_simples(anexo: str, rbt12: float, db_path: str = "database.db") -> Dict[str, Any]:
    """
    Busca no banco de dados a alíquota nominal e a parcela a deduzir 
    correspondente à faixa de faturamento acumulado (RBT12).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query para encontrar a faixa correta com base no RBT12
    query = """
        SELECT aliquota_nominal, parcela_a_deduzir, faixa_numero
        FROM faixas_simples_nacional
        WHERE anexo = ? 
          AND ? > limite_inferior 
          AND ? <= limite_superior
        LIMIT 1;
    """
    
    cursor.execute(query, (anexo, rbt12, rbt12))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        # Caso o faturamento estoure o limite máximo do Simples (R$ 4.8 milhões)
        raise ValueError("Faturamento acumulado excede o limite máximo do Simples Nacional (R$ 4,8M).")
        
    return {
        "aliquota_nominal": row[0],
        "parcela_a_deduzir": row[1],
        "faixa": row[2]
    }

def calcular_imposto_simples(
    faturamento_mes: float, 
    rbt12: float, 
    folha_acumulada_12m: float,
    eh_tecnologia_intelectual: bool = True,
    db_path: str = "database.db"
) -> Dict[str, Any]:
    """
    Função principal que orquestra o cálculo do Simples Nacional do mês.
    """
    # 1. Se o faturamento for zero, o imposto é zero
    if faturamento_mes <= 0:
        return {"imposto_final": 0.0, "aliquota_efetiva": 0.0, "anexo_utilizado": "N/A", "faixa": 0}

    # 2. Definição do Anexo (Regra do Fator R para Serviços Intelectuais/TI)
    if eh_tecnologia_intelectual:
        fator_r = calcular_fator_r(folha_acumulada_12m, rbt12)
        anexo = "ANEXO_III" if fator_r >= 28.0 else "ANEXV"
    else:
        # Para serviços gerais que não entram no Fator R, costuma ser fixo no Anexo III
        fator_r = None
        anexo = "ANEXO_III"

    # 3. Busca os parâmetros da lei no banco de dados
    try:
        dados_faixa = obter_faixa_simples(anexo, rbt12, db_path)
    except ValueError as e:
        return {"erro": str(e), "sublimite_estourado": True}

    aliq_nominal = dados_faixa["aliquota_nominal"]
    deducao = dados_faixa["parcela_a_deduzir"]

    # 4. Cálculo da Alíquota Efetiva (Fórmula da LC 123/06)
    # Primeira faixa (RBT12 até 180k) não tem dedução, a alíquota efetiva é a própria nominal
    if dados_faixa["faixa"] == 1:
        aliquota_efetiva = aliq_nominal
    else:
        aliquota_efetiva = ((rbt12 * aliq_nominal) - deducao) / rbt12

    # 5. Cálculo do valor final a pagar
    imposto_final = faturamento_mes * aliquota_efetiva

    return {
        "faturamento_mes": round(faturamento_mes, 2),
        "rbt12": round(rbt12, 2),
        "fator_r_percentual": round(fator_r, 2) if fator_r is not None else None,
        "anexo_utilizado": anexo,
        "faixa_identificada": dados_faixa["faixa"],
        "aliquota_nominal_lei": round(aliq_nominal * 100, 2),
        "aliquota_efetiva_calculada": round(aliquota_efetiva * 100, 4),
        "imposto_final": round(imposto_final, 2)
    }