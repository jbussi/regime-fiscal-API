import sqlite3
from src.database.connection import get_db_connection

def calcular_imposto_simples(faturamento_mes: float, rbt12: float, folha_acumulada_12m: float, anexo_escolhido: str) -> dict:
    """
    Calcula o imposto do Simples Nacional para qualquer um dos 5 anexos.
    Aplica a regra do Fator R caso o anexo escolhido seja o III ou o V.
    """
    if faturamento_mes <= 0:
        return {
            "imposto_final": 0.0, 
            "aliquota_efetiva_calculada": 0.0, 
            "anexo_utilizado": "NENHUM", 
            "distribuicao": {}
        }

    # 1. Definição do Anexo Real (Tratamento do Fator R para Serviços Intelectuais)
    anexo = anexo_escolhido
    fator_r = 0.0

    if anexo_escolhido in ["ANEXO_III", "ANEXO_V"]:
        fator_r = (folha_acumulada_12m / rbt12) if rbt12 > 0 else 0.0
        # Regra de Ouro: Se a folha for >= 28% do faturamento, vai para o Anexo III (mais barato)
        if fator_r >= 0.28:
            anexo = "ANEXO_III"
        else:
            anexo = "ANEXO_V"

    # 2. Busca a faixa de alíquota nominal e dedução correspondente ao RBT12 no SQLite
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT faixa_numero, aliquota_nominal, parcela_a_deduzir 
            FROM faixas_simples_nacional
            WHERE anexo = ? AND ? > limite_inferior AND ? <= limite_superior
        """, (anexo, rbt12, rbt12))
        row = cursor.fetchone()
        
        # Fallback de segurança: caso ultrapasse o limite máximo da faixa 5 (Teto do Simples)
        if not row:
            cursor.execute("""
                SELECT faixa_numero, aliquota_nominal, parcela_a_deduzir 
                FROM faixas_simples_nacional 
                WHERE anexo = ? 
                ORDER BY faixa_numero DESC LIMIT 1
            """, (anexo,))
            row = cursor.fetchone()

        faixa_numero, aliquota_nominal, parcela_a_deduzir = row

        # 3. Cálculo da Alíquota Efetiva: ((RBT12 * Alíquota Nominal) - Parcela a Deduzir) / RBT12
        if rbt12 > 0:
            aliquota_efetiva = (rbt12 * aliquota_nominal - parcela_a_deduzir) / rbt12
        else:
            # Caso a empresa seja nova no mercado e não tenha histórico de 12 meses (RBT12 = 0)
            aliquota_efetiva = aliquota_nominal

        # Evita distorções matemáticas em faturamentos muito baixos no início da faixa
        if aliquota_efetiva < 0:
            aliquota_efetiva = aliquota_nominal

        # Aplicação da alíquota sobre o faturamento do mês atual
        imposto_final = round(faturamento_mes * aliquota_efetiva, 2)

        # 4. Busca os percentuais de repartição de impostos no banco para detalhamento técnico
        cursor.execute("""
            SELECT percentual_irpj, percentual_csll, percentual_pis, percentual_cofins, percentual_cpp, percentual_iss_icms
            FROM reparticao_simples_nacional 
            WHERE anexo = ? AND faixa_numero = ?
        """, (anexo, faixa_numero))
        rep = cursor.fetchone()

    # Fallback caso a linha de partilha não seja encontrada (Ex: Sublimites da faixa 6)
    p_ir, p_cs, p_pis, p_cof, p_cpp, p_iss_icms = rep if rep else (0.35, 0.118, 0.0, 0.0, 0.532, 0.0)

    # 5. Retorno estruturado pronto para consumo de gráficos do front-end
    return {
        "imposto_final": imposto_final,
        "aliquota_efetiva_calculada": round(aliquota_efetiva * 100, 4),
        "anexo_utilizado": anexo,
        "fator_r_percentual": round(fator_r * 100, 2),
        "faixa_enquadrada": faixa_numero,
        "distribuicao": {
            "irpj": round(imposto_final * p_ir, 2),
            "csll": round(imposto_final * p_cs, 2),
            "pis": round(imposto_final * p_pis, 2),
            "cofins": round(imposto_final * p_cof, 2),
            "cpp_inss": round(imposto_final * p_cpp, 2),
            "iss_ou_icms": round(imposto_final * p_iss_icms, 2)
        }
    }