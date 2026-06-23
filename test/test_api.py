# src/test_api.py
import json
import urllib.request
import urllib.error

API_URL = "http://127.0.0.1:8000/api/simular"

# 1. Definição dos Cenários de Teste
CENARIOS = {
    "1. Fator R (Simples Nacional Vencedor)": {
        "payload": {
            "tipo_atividade": "SERVICOS_REGULAMENTADOS",
            "faturamento_servicos": 50000.0,
            "faturamento_comercio": 0.0,
            "faturamento_acumulado_ano": 150000.0,
            "aliquota_iss_local": 0.05,
            "anexo_escolhido": "ANEXO_V",
            "rbt12": 600000.0,
            "folha_acumulada_12m": 180000.0,
            "folha_mensal_atual": 15000.0,
            "opex_dedutivel": 5000.0,
            "custos_com_direito_a_credito": 1000.0,
            "compras_capex_computadores": 0.0
        },
        "endpoint": "/best",
        "espera_erro": False
    },
    "2. Estouro do Item 11 (Presunção Cheia de 32%)": {
        "payload": {
            "tipo_atividade": "SERVICOS_GERAIS",
            "faturamento_servicos": 20000.0,
            "faturamento_comercio": 0.0,
            "faturamento_acumulado_ano": 130000.0, # Passou de 120k
            "aliquota_iss_local": 0.03,
            "anexo_escolhido": "ANEXO_III",
            "rbt12": 150000.0,
            "folha_acumulada_12m": 30000.0,
            "folha_mensal_atual": 3000.0,
            "opex_dedutivel": 2000.0,
            "custos_com_direito_a_credito": 0.0,
            "compras_capex_computadores": 0.0
        },
        "endpoint": "/presumido",
        "espera_erro": False
    },
    "3. Validação de Erro de ISS (Esperado 400)": {
        "payload": {
            "tipo_atividade": "SERVICOS_GERAIS",
            "faturamento_servicos": 10000.0,
            "aliquota_iss_local": 0.01, # ISS abaixo de 2% (Ilegal)
            "anexo_escolhido": "ANEXO_III",
            "rbt12": 100000.0,
            "folha_acumulada_12m": 20000.0
        },
        "endpoint": "/presumido",
        "espera_erro": True
    }
}

def rodar_testes():
    print("🚀 Iniciando Testes de Homologação - Lhama Fiscal API\n" + "="*55)
    
    for nome, config in CENARIOS.items():
        url = f"{API_URL}{config['endpoint']}"
        data = json.dumps(config["payload"]).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
                res_body = json.loads(response.read().decode("utf-8"))
                
                if config["espera_erro"]:
                    print(f"❌ {nome} -> FALHOU (Esperava erro, mas retornou status {status_code})")
                else:
                    print(f"✅ {nome} -> SUCESSO (Status {status_code})")
                    if "vencedor" in res_body:
                        print(f"   | Vencedor: {res_body['vencedor']['regime']} (Alíquota Efetiva: {res_body['vencedor']['aliquota_efetiva']}%)")
                    elif "percentual_presuncao_irpj_aplicado" in res_body.get("detalhe", {}):
                        print(f"   | Presunção IRPJ Aplicada: {res_body['detalhe']['percentual_presuncao_irpj_aplicado']}%")
                        
        except urllib.error.HTTPError as e:
            status_code = e.code
            error_body = json.loads(e.read().decode("utf-8"))
            
            if config["espera_erro"] and status_code == 400:
                print(f"✅ {nome} -> SUCESSO (Erro interceptado corretamente: {status_code})")
                print(f"   | Mensagem da API: '{error_body['detail']}'")
            else:
                print(f"❌ {nome} -> CRASH (Erro inesperado {status_code})")
                print(f"   | Detalhes: {error_body}")
        except Exception as ex:
            print(f"❌ {nome} -> Falha crítica de conexão: {str(ex)}")
            
        print("-" * 55)

if __name__ == "__main__":
    rodar_testes()