import pytest
from fastapi.testclient import TestClient
from src.app import app  # Importa a instância do seu FastAPI

client = TestClient(app)

def test_carregar_dashboard_raiz():
    """Garante que a página inicial (dashboard) está carregando com sucesso (200)"""
    response = client.get("/")
    assert response.status_code == 200
    assert "html" in response.text.lower()

def test_simulacao_simples_sucesso():
    """Valida se o endpoint do Simples Nacional processa o schema completo corretamente"""
    # Payload estruturado exatamente de acordo com o CenarioSimulacaoInput detectado nos logs
    dados_teste = {
        "tipo_atividade": "SERVICOS_GERAIS",
        "faturamento_servicos": 60000.0,
        "faturamento_comercio": 0.0,
        "faturamento_acumulado_ano": 360000.0,
        "aliquota_iss_local": 0.03,
        "anexo_escolhido": "ANEXO_III",
        "rbt12": 720000.0,
        "folha_acumulada_12m": 18000.0,
        "folha_mensal_atual": 1500.0,
        "opex_dedutivel": 0.0,
        "custos_com_direito_a_credito": 0.0,
        "compras_capex_computadores": 0.0
    }
    
    response = client.post("/api/simular/simples", json=dados_teste)
    
    # Agora deve passar com 200 OK!
    assert response.status_code == 200
    resultado = response.json()
    assert "detail" not in resultado
    assert isinstance(resultado, dict)

def test_simulacao_dados_invalidos():
    """Valida se a API barra requisições com dados malformados (HTTP 422)"""
    dados_corrompidos = {
        "tipo_atividade": "SERVICOS_GERAIS",
        "faturamento_servicos": "texto_invalido_onde_deveria_ser_float",
        "rbt12": 720000.0,
        "folha_acumulada_12m": 18000.0
    }
    response = client.post("/api/simular/simples", json=dados_corrompidos)
    assert response.status_code == 422