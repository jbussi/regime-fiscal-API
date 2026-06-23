from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_redoc_html

# Importando os Schemas atualizados
from src.models.fiscal_schemas import (
    CenarioSimulacaoInput, 
    BestResponse, 
    HTTPErrorModel, 
    HTTPValidationErrorModel
)
from src.engines import calcular_imposto_simples, calcular_imposto_presumido, calcular_imposto_real

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("LhamaFiscalAPI")

app = FastAPI(
    title="Regime Fiscal API",
    description="Backend de alta performance com tratamento estrito de erros e validação de regras de negócio.",
    version="0.0.0",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dicionário padrão de erros para documentar no Swagger
ERROS_DOCUMENTADOS = {
    400: {"model": HTTPErrorModel, "description": "Erro de Regra de Negócio (Dados inconsistentes)"},
    422: {"model": HTTPValidationErrorModel, "description": "Erro de Validação de Tipo/Contrato (Pydantic)"},
    500: {"model": HTTPErrorModel, "description": "Erro Interno do Servidor (Falha no banco ou processamento)"}
}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro Crítico 500 em {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocorreu uma falha inesperada no processamento fiscal. Contate o suporte."}
    )

# --- ENDPOINTS COM TRATAMENTO DE ERRO DE NEGÓCIO ---

@app.get("/", tags=["Status"], include_in_schema=False)
def redirect_to_docs():
    """Redireciona automaticamente a raiz para a documentação do Swagger."""
    return RedirectResponse(url="/docs")

@app.get("/redoc", tags=["Status"], include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,  # Ele vai buscar dinamicamente do seu app
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js", # Versão estável fixada
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.post("/api/simular/simples", tags=["Simulações Isoladas"], responses=ERROS_DOCUMENTADOS)
def get_simples(cenario: CenarioSimulacaoInput):
    """Calcula o Simples Nacional com validação de Anexo e Faturamento."""
    faturamento_total = cenario.faturamento_servicos + cenario.faturamento_comercio
    
    if faturamento_total < 0:
        raise HTTPException(status_code=400, detail="O faturamento do mês não pode ser negativo.")
        
    ANEXOS_VALIDOS = ["ANEXO_I", "ANEXO_II", "ANEXO_III", "ANEXO_IV", "ANEXO_V"]
    if cenario.anexo_escolhido not in ANEXOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Anexo inválido. Escolha entre: {', '.join(ANEXOS_VALIDOS)}")

    return calcular_imposto_simples(
        faturamento_mes=faturamento_total,
        rbt12=cenario.rbt12,
        folha_acumulada_12m=cenario.folha_acumulada_12m,
        anexo_escolhido=cenario.anexo_escolhido
    )

@app.post("/api/simular/presumido", tags=["Simulações Isoladas"], responses=ERROS_DOCUMENTADOS)
def get_presumido(cenario: CenarioSimulacaoInput):
    """Calcula o Lucro Presumido validando as travas constitucionais do ISS e Atividades."""
    if cenario.faturamento_servicos > 0 and not (0.02 <= cenario.aliquota_iss_local <= 0.05):
        raise HTTPException(status_code=400, detail="Por lei complementar (Art. 8º-A da LC 116/03), a alíquota do ISS deve estar entre 2% (0.02) e 5% (0.05).")

    ATIVIDADES_VALIDAS = ["COMERCIO", "INDUSTRIALIZACAO", "TRANSPORTE_CARGAS", "SERVICOS_GERAIS", "SERVICOS_REGULAMENTADOS"]
    if cenario.tipo_atividade not in ATIVIDADES_VALIDAS:
        raise HTTPException(status_code=400, detail=f"Tipo de atividade desconhecido. Escolha entre: {', '.join(ATIVIDADES_VALIDAS)}")

    return calcular_imposto_presumido(
        faturamento_servicos=cenario.faturamento_servicos,
        faturamento_comercio=cenario.faturamento_comercio,
        faturamento_acumulado_ano=cenario.faturamento_acumulado_ano,
        tipo_atividade=cenario.tipo_atividade,
        aliquota_iss_local=cenario.aliquota_iss_local
    )

@app.post("/api/simular/real", tags=["Simulações Isoladas"], responses=ERROS_DOCUMENTADOS)
def get_real(cenario: CenarioSimulacaoInput):
    """Calcula o Lucro Real garantindo consistência entre faturamento e custos."""
    faturamento_total = cenario.faturamento_servicos + cenario.faturamento_comercio
    
    if cenario.custos_com_direito_a_credito > faturamento_total:
        raise HTTPException(status_code=400, detail="Inconsistência: Os custos creditáveis de PIS/COFINS não podem superar o faturamento bruto.")

    return calcular_imposto_real(
        faturamento_bruto=faturamento_total,
        opex_dedutivel=cenario.opex_dedutivel,
        custos_com_direito_a_credito=cenario.custos_com_direito_a_credito,
        compras_capex_computadores=cenario.compras_capex_computadores,
        folha_mensal_atual=cenario.folha_mensal_atual
    )

@app.post("/api/simular/all", tags=["Simulações Combinadas"], responses=ERROS_DOCUMENTADOS)
def get_all(cenario: CenarioSimulacaoInput):
    """Executa a malha completa aplicando todas as validações prévias de negócio."""
    faturamento_total = cenario.faturamento_servicos + cenario.faturamento_comercio
    
    if faturamento_total <= 0:
        raise HTTPException(status_code=400, detail="Para realizar o confronto de cenários, o faturamento total deve ser maior que zero.")
    if cenario.faturamento_servicos > 0 and not (0.02 <= cenario.aliquota_iss_local <= 0.05):
        raise HTTPException(status_code=400, detail="Alíquota de ISS inválida para o motor do Presumido (deve ser entre 0.02 e 0.05).")

    return {
        "faturamento_total_mes": faturamento_total,
        "simples_nacional": calcular_imposto_simples(faturamento_total, cenario.rbt12, cenario.folha_acumulada_12m, cenario.anexo_escolhido),
        "lucro_presumido": calcular_imposto_presumido(cenario.faturamento_servicos, cenario.faturamento_comercio, cenario.faturamento_acumulado_ano, cenario.tipo_atividade, cenario.aliquota_iss_local),
        "lucro_real": calcular_imposto_real(faturamento_total, cenario.opex_dedutivel, cenario.custos_com_direito_a_credito, cenario.compras_capex_computadores, cenario.folha_mensal_atual)
    }

@app.post("/api/simular/best", tags=["Simulações Combinadas"], response_model=BestResponse, responses=ERROS_DOCUMENTADOS)
def get_best(cenario: CenarioSimulacaoInput):
    """Compara os regimes com validação estrita e retorna o melhor cenário documentado."""
    faturamento_total = cenario.faturamento_servicos + cenario.faturamento_comercio
    
    if faturamento_total <= 0:
        raise HTTPException(status_code=400, detail="O faturamento total deve ser superior a zero para gerar insights de melhor escolha.")

    res_simples = calcular_imposto_simples(faturamento_total, cenario.rbt12, cenario.folha_acumulada_12m, cenario.anexo_escolhido)
    res_presumido = calcular_imposto_presumido(cenario.faturamento_servicos, cenario.faturamento_comercio, cenario.faturamento_acumulado_ano, cenario.tipo_atividade, cenario.aliquota_iss_local)
    res_real = calcular_imposto_real(faturamento_total, cenario.opex_dedutivel, cenario.custos_com_direito_a_credito, cenario.compras_capex_computadores, cenario.folha_mensal_atual)
    
    impostos = {
        "Simples Nacional": res_simples.get("imposto_final", float('inf')),
        "Lucro Presumido": res_presumido.get("imposto_total_mes", float('inf')),
        "Lucro Real": res_real.get("imposto_total_mes", float('inf'))
    }
    
    melhor_regime = min(impostos, key=impostos.get)
    menor_imposto = impostos[melhor_regime]
    pior_regime = max(impostos, key=impostos.get)
    economia_maxima = impostos[pior_regime] - menor_imposto
    
    aliquota_efetiva = (menor_imposto / faturamento_total * 100)
    
    return {
        "faturamento_analisado": faturamento_total,
        "vencedor": {
            "regime": melhor_regime,
            "imposto_total": round(menor_imposto, 2),
            "aliquota_efetiva": round(aliquota_efetiva, 4)
        },
        "comparativo_rapido": {
            "simples_nacional": round(impostos["Simples Nacional"], 2),
            "lucro_presumido": round(impostos["Lucro Presumido"], 2),
            "lucro_real": round(impostos["Lucro Real"], 2)
        },
        "insight_planejamento": f"Cenário validado! O regime {melhor_regime} é economicamente superior para este mês, poupando R$ {round(economia_maxima, 2)} em relação ao modelo {pior_regime}."
    }