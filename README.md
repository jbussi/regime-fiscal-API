# Regime Fiscal API

O **Regime Fiscal API** é um motor assíncrono de alta performance construído para simulação analítica e planejamento tributário estratégico corporativo. A aplicação realiza o confronto simultâneo e em tempo real entre os três principais regimes tributários brasileiros (**Simples Nacional**, **Lucro Presumido** e **Lucro Real**), aplicando regras estritas da Receita Federal (RFB).

O sistema foi desenhado sob os pilares de consistência matemática fiscal, isolamento de escopo por engines dedicadas e alta concorrência.

---

## 🚀 Diferenciais Técnicos e Funcionalidades

* **Motor de Confronto Simultâneo:** Processamento paralelo de múltiplos cenários fiscais para determinar o regime tributário mais favorável (maior eficiência fiscal).
* **Cálculo Dinâmico do Fator R:** Monitoramento da relação entre a folha de salários e a receita bruta acumulada para enquadramento automático entre o Anexo III (alíquotas reduzidas) e o Anexo V do Simples Nacional.
* **Persistência Otimizada (SQLite em Modo WAL):** Utilização do banco de dados SQLite operando em modo **Write-Ahead Logging (WAL)**, permitindo leituras concorrentes ultrarrápidas sem locks de escrita durante as simulações.
* **Auditoria de Payloads:** Geração de logs estruturados e retornos granulares detalhando a distribuição interna de impostos (**IRPJ, CSLL, PIS, COFINS, CPP/INSS, ISS/ICMS**).

---

## 📂 Estrutura do Projeto

```text
meu_projeto/
│
├── database.db               # Banco SQLite (Gerado automaticamente pelo seed)
├── requirements.txt          # Dependências do ecossistema Python (FastAPI, Pydantic, etc.)
├── docker-compose.yml        # Arquivo para servidor Docker
├── Dockerfile                # Arquivo para servidor Docker
│
├── src/
│   ├── __init__.py           # Inicializador do pacote raiz
│   ├── app.py                # Ponto de entrada, rotas FastAPI e middlewares de CORS/Erros
│   │
│   ├── database/
│   │   ├── __init__.py       # Exporta o pool/gerenciador de conexões
│   │   ├── connection.py     # Context Manager do SQLite (Configuração do Modo WAL e PRAGMAs)
│   │   └── schema.sql        # DDL das tabelas fiscais (alíquotas, faixas e anexos)
│   │
│   ├── engines/
│   │   ├── __init__.py       # Fachada unificada das engines de cálculo
│   │   ├── seed_db.py        # Script de carga inicial e tabelas de referência da RFB
│   │   ├── simples_nacional.py # Regras de cálculo progressivo e dedução de faixas
│   │   ├── lucro_presumido.py  # Presunção por atividade (Serviços/Comércio) e Adicional de IRPJ
│   │   └── lucro_real.py       # Lucro líquido contábil e adições/exclusões do LALUR
│   │
│   └── models/
│       ├── __init__.py       # Exporta os schemas de validação
│       └── fiscal_schemas.py # Modelos de dados Pydantic para validação estrita (Request/Response)
├── test
    ├── test_api.py
    ├── test_app.py
    └── test_frontend.py  # Testes para confirmar funcionamento do projeto
```

## 🔌 Documentação da API (Endpoints Principais)

Todos os payloads de entrada passam por validação estrita de tipo e limites via Pydantic.

### 1. Confronto Geral (Simulação Completa)
* **Endpoint:** `POST /api/v1/simulacao/confronto`
* **Descrição:** Executa as três engines em paralelo e retorna o comparativo financeiro consolidado.
* **Payload de Entrada (`SimulationRequest`):**
    ```json
    {
      "faturamento_servicos": 80000.00,
      "folha_mensal_atual": 24000.00,
      "rbt12": 960000.00,
      "folha_acumulada_12m": 288000.00,
      "aliquota_iss_local": 3.5,
      "anexo_escolhido": "ANEXO_V"
    }
    ```
* **Resposta de Sucesso (`ConfrontoResponse` - HTTP 200):**
    ```json
    {
      "melhor_opcao": "SIMPLES_NACIONAL",
      "economia_estimada": 3540.25,
      "simples_nacional": { "imposto_final": 10875.00, "aliquota_efetiva_calculada": 13.59 },
      "lucro_presumido": { "imposto_final": 14415.25, "aliquota_efetiva_calculada": 18.01 },
      "lucro_real": { "imposto_final": 16200.00, "aliquota_efetiva_calculada": 20.25 }
    }
    ```

### 2. Isolação das Engines (Auditoria Técnica)
Caso precise auditar um cálculo isoladamente, o sistema expõe as rotas de backend que alimentam a aba técnica:

* `POST /api/v1/simulacao/simples` -> Retorna a alíquota efetiva deduzida da tabela progressiva e o estado do Fator R.
* `POST /api/v1/simulacao/presumido` -> Aplica a presunção (ex: 32% para serviços), calcula o adicional de 10% do IRPJ se ultrapassar R\$ 20 mil/mês e as alíquotas fixas de PIS/COFINS.
* `POST /api/v1/simulacao/real` -> Deduz o imposto com base no lucro líquido real e analisa créditos tributários informados.