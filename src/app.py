# src/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Importando os motores que programamos
from src.engines.simples_nacional import calcular_imposto_simples
from src.engines.lucro_presumido import calcular_imposto_presumido
from src.engines.lucro_real import calcular_imposto_real

app = FastAPI(
    title="Lhama Fiscal API",
    description="API de simulação e planejamento tributário estratégico entre Simples, Presumido e Real.",
    version="1.0.0"
)

# Configuração de CORS: Permite que sites, dashboards e aplicações front-end consumam esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, defina os domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE ENTRADA (Validação Pydantic) ---

class CenarioSimulacaoInput(BaseModel):
    faturamento_servicos: float = Field(..., description="Faturamento mensal com serviços", example=50000.00)
    faturamento_comercio: float = Field(default=0.0, description="Faturamento mensal com comércio", example=0.0)
    
    # Dados para o Simples Nacional (Fator R)
    rbt12: float = Field(..., description="Faturamento acumulado dos últimos 12 meses", example=600000.00)
    folha_acumulada_12m: float = Field(..., description="Folha de pagamento acumulada dos últimos 12 meses", example=180000.00)
    eh_tecnologia_intelectual: bool = Field(default=True, description="Define se o serviço entra na regra do Fator R")
    
    # Dados para o Lucro Real
    opex_dedutivel: float = Field(default=0.0, description="Despesas operacionais dedutíveis (Marketing, Software, RH)", example=15000.00)
    custos_com_direito_a_credito: float = Field(default=0.0, description="Custos que geram créditos de PIS/COFINS (Cloud, Aluguel)", example=5000.00)
    compras_capex_computadores: float = Field(default=0.0, description="Investimento em maquinário/computadores no mês", example=10000.00)


# --- ROTAS DA API ---

@app.get("/")
def read_root():
    return {"status": "online", "projeto": "Lhama Fiscal API", "ano": 2026}


@app.post("/api/simular/confronto")
def simular_confronto_regimes(cenario: CenarioSimulacaoInput):
    """
    Endpoint principal. Recebe os dados financeiros do mês e processa
    o cálculo nos 3 regimes simultaneamente, devolvendo o panorama para gráficos.
    """
    faturamento_total_mes = cenario.faturamento_servicos + cenario.faturamento_comercio
    
    # 1. Executa Motor do Simples Nacional
    res_simples = calcular_imposto_simples(
        faturamento_mes=faturamento_total_mes,
        rbt12=cenario.rbt12,
        folha_acumulada_12m=cenario.folha_acumulada_12m,
        eh_tecnologia_intelectual=cenario.eh_tecnologia_intelectual
    )
    
    # 2. Executa Motor do Lucro Presumido
    res_presumido = calcular_imposto_presumido(
        faturamento_servicos=cenario.faturamento_servicos,
        faturamento_comercio=cenario.faturamento_comercio
    )
    
    # 3. Executa Motor do Lucro Real
    res_real = calcular_imposto_real(
        faturamento_bruto=faturamento_total_mes,
        opex_dedutivel=cenario.opex_dedutivel,
        custos_com_direito_a_credito=cenario.custos_com_direito_a_credito,
        compras_capex_computadores=cenario.compras_capex_computadores
    )
    
    # 4. Estrutura o payload de resposta focado em visualização (Dashboards)
    return {
        "metadata": {
            "faturamento_total": faturamento_total_mes,
            "rbt12": cenario.rbt12
        },
        "confronto_grafico": {
            "labels": ["Simples Nacional", "Lucro Presumido", "Lucro Real"],
            "valores_imposto": [
                res_simples.get("imposto_final", 0.0),
                res_presumido.get("imposto_total_mes", 0.0),
                res_real.get("imposto_total_mes", 0.0)
            ],
            "aliquotas_efetivas": [
                res_simples.get("aliquota_efetiva_calculada", 0.0),
                res_presumido.get("aliquota_efetiva_global", 0.0),
                res_real.get("aliquota_efetiva_global", 0.0)
            ]
        },
        "detalhes_regimes": {
            "simples_nacional": res_simples,
            "lucro_presumido": res_presumido,
            "lucro_real": res_real
        }
    }