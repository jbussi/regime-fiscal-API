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

## 🔌 Arquitetura de Rotas e Documentação da API

O ecossistema de rotas foi projetado seguindo as melhores práticas RESTful, utilizando versionamento explícito (`/api/v1`) para os endpoints analíticos e isolando as rotas de infraestrutura e interface. Todos os payloads de entrada e saída contam com validação estrita de tipos via Pydantic.

---

### 🌐 Rotas de Infraestrutura e Interface

* **`GET /` (Interface Visual da Simulação):** Renderiza o painel interativo (Frontend). É o ponto de entrada para o usuário final realizar simulações visuais completas, visualizando gráficos comparativos e relatórios de eficiência fiscal de forma amigável.
  
* **`GET /docs` (Swagger UI):**
  Documentação interativa automatizada da API. Permite testar todos os endpoints em tempo real, verificar schemas de validação e códigos de status HTTP diretamente pelo navegador.
  
* **`GET /redoc` (ReDoc):**
  Documentação técnica estática e detalhada, ideal para consulta de estruturas de dados e integrações externas.

---

### 🧠 Rotas de Processamento Core (Motores Fiscais)

#### 1. Confronto Geral (Simulação Paralela Monetária)
* **Endpoint:** `POST /api/v1/simulacao/confronto`
* **Descrição:** Orquestra a execução simultânea das três engines (`Simples Nacional`, `Lucro Presumido` e `Lucro Real`) utilizando concorrência em memória. Retorna o veredito do regime ideal e a economia real projetada.
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
* **Resposta de Sucesso (`ConfrontoResponse` - HTTP 200):**
  ```json
  {
    "melhor_opcao": "SIMPLES_NACIONAL",
    "economia_estimada": 3540.25,
    "simples_nacional": { "imposto_final": 10875.00, "aliquota_efetiva_calculada": 13.59 },
    "lucro_presumido": { "imposto_final": 14415.25, "aliquota_efetiva_calculada": 18.01 },
    "lucro_real": { "imposto_final": 16200.00, "aliquota_efetiva_calculada": 20.25 }
  }

#### 2. Isolação das Engines (Módulos de Auditoria Técnico-Fiscal)

Endpoints especializados que alimentam as abas de detalhamento técnico do sistema, permitindo auditar as memórias de cálculo de forma isolada.

* **`POST /api/v1/simulacao/simples`**
  * **Descrição:** Calcula a alíquota efetiva baseada na tabela progressiva da Receita Federal. Realiza o cruzamento do **Fator R** (Relação Folha/Faturamento) para determinar o enquadramento dinâmico entre o Anexo III e Anexo V.
  * **Retorno Técnico:** Detalha a parcela a deduzir da faixa atingida e o status de enquadramento do Fator R.

* **`POST /api/v1/simulacao/presumido`**
  * **Descrição:** Aplica os percentuais de presunção legal sobre a receita (ex: 32% para serviços). Calcula de forma isolada o **Adicional de IRPJ** (alíquota extraordinária de 10% sobre a parcela do lucro presumido que exceder R\$ 20.000,00/mês), além das alíquotas fixas de PIS, COFINS e CSLL.
  * **Retorno Técnico:** Separação granular de impostos federais acumulados e o peso do adicional de IRPJ.

* **`POST /api/v1/simulacao/real`**
  * **Descrição:** Avalia o cenário com base no lucro líquido contábil real da operação. Processa as adições e exclusões clássicas do LALUR (Livro de Apuração do Lucro Real) e computa o impacto de créditos tributários não-cumulativos de PIS e COFINS sobre insumos.
  * **Retorno Técnico:** Demonstrativo de resultado fiscal com a incidência direta sobre a margem real líquida.

---

## ⚙️ Configuração do Banco de Dados e Performance

O banco de dados SQLite aplica configurações via `PRAGMA` no momento em que a conexão é aberta pelo Context Manager (`connection.py`), elevando a concorrência ao nível de produção:

```sql
PRAGMA journal_mode = WAL;         -- Habilita o Write-Ahead Logging
PRAGMA synchronous = NORMAL;       -- Otimiza a sincronia de disco sem perder segurança
PRAGMA busy_timeout = 5000;        -- Evita travamentos de threads concorrentes aguardando escrita
```

## 🐳 Execução em Ambiente Local (Docker)

Para subir a aplicação completa localmente simulando o ambiente de produção:

```bash
# Sobe o contêiner da API mapeando a porta local de forma dinâmica
docker compose up -d --build

# Popula o banco de dados com as tabelas oficiais da RFB (Seed)
docker compose exec api python src/engines/seed_db.py

# Roda a suíte completa de testes de interface do Playwright
docker compose exec api pytest -v test/test_frontend.py
```
## 🚀 Deploy em Produção

A aplicação está totalmente configurada para **Deploy Contínuo em Nuvem baseada em Contêineres (como o Railway)**. 

O `Dockerfile` e o `docker-compose.yml` utilizam mapeamentos dinâmicos de porta através da variável `${PORT}`, permitindo que a infraestrutura gerencie a escalabilidade do serviço sem necessidade de alteração de código.
