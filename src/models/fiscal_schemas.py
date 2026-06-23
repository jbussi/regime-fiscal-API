from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- SCHEMA DE ENTRADA (Mantenha o que já consolidamos) ---
class CenarioSimulacaoInput(BaseModel):
    tipo_atividade: str = Field(default="SERVICOS_GERAIS", description="Atividade RFB: COMERCIO, INDUSTRIALIZACAO, SERVICOS_GERAIS, SERVICOS_REGULAMENTADOS, TRANSPORTE_CARGAS", example="SERVICOS_GERAIS")
    faturamento_servicos: float = Field(default=0.0, description="Faturamento mensal com serviços", example=50000.00)
    faturamento_comercio: float = Field(default=0.0, description="Faturamento mensal com comércio", example=0.0)
    faturamento_acumulado_ano: float = Field(default=0.0, description="Faturamento bruto acumulado no ano", example=100000.00)
    aliquota_iss_local: float = Field(default=0.05, description="Alíquota de ISS local (0.02 a 0.05)", example=0.05)
    anexo_escolhido: str = Field(default="ANEXO_I", description="ANEXO_I, ANEXO_II, ANEXO_III, ANEXO_IV, ANEXO_V", example="ANEXO_III")
    rbt12: float = Field(..., description="Faturamento bruto acumulado de 12 meses", example=600000.00)
    folha_acumulada_12m: float = Field(..., description="Folha acumulada de 12 meses", example=180000.00)
    folha_mensal_atual: float = Field(default=0.0, description="Folha de salários do mês atual", example=15000.00)
    opex_dedutivel: float = Field(default=0.0, description="Despesas operacionais dedutíveis", example=15000.00)
    custos_com_direito_a_credito: float = Field(default=0.0, description="Custos geradores de crédito PIS/COFINS", example=5000.00)
    compras_capex_computadores: float = Field(default=0.0, description="Investimento em hardware no mês", example=0.0)

# --- SCHEMAS DE RETORNO (Para documentação técnica) ---
class VencedorResumo(BaseModel):
    regime: str = Field(..., example="Simples Nacional")
    imposto_total: float = Field(..., example=3650.00)
    aliquota_efetiva: float = Field(..., example=7.30)

class ComparativoRapido(BaseModel):
    simples_nacional: float = Field(..., example=3650.00)
    lucro_presumido: float = Field(..., example=6850.00)
    lucro_real: float = Field(..., example=8200.00)

class BestResponse(BaseModel):
    faturamento_analisado: float = Field(..., example=50000.00)
    vencedor: VencedorResumo
    comparativo_rapido: ComparativoRapido
    insight_planejamento: str = Field(..., example="O regime Simples Nacional apresenta a menor carga...")


class HTTPErrorModel(BaseModel):
    detail: str = Field(..., description="Mensagem descritiva do erro encontrado.")

class ValidationErrorDetail(BaseModel):
    loc: List[Any] = Field(..., description="Onde o erro ocorreu (ex: ['body', 'aliquota_iss_local'])")
    msg: str = Field(..., description="Mensagem de erro gerada pelo validador.")
    type: str = Field(..., description="Tipo do erro de validação.")

class HTTPValidationErrorModel(BaseModel):
    detail: List[ValidationErrorDetail] = Field(..., description="Lista com os detalhes de cada campo inválido.")