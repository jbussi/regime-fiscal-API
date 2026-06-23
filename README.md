# Regime Fiscal API

O **Regime Fiscal API** é um motor de alta performance para simulação analítica e planejamento tributário estratégico. A aplicação realiza o confronto simultâneo entre os três principais regimes tributários brasileiros (**Simples Nacional**, **Lucro Presumido** e **Lucro Real**), aplicando regras estritas da Receita Federal, como o Fator R, o limite de presunção reduzida e créditos não cumulativos.

O sistema utiliza um banco de dados **SQLite** otimizado em modo **WAL (Write-Ahead Logging)** para garantir leituras concorrentes ultrarrápidas sem concorrência de escrita.

---

## 📂 Estrutura do Projeto

```text
meu_projeto/
│
├── database.db               # Banco SQLite (Gerado automaticamente pelo seed)
├── requirements.txt          # Dependências do ecossistema Python
│
└── src/
    ├── __init__.py           # Inicializador do pacote raiz (vazio)
    ├── app.py                # Rotas da API FastAPI e Handlers de Erro
    │
    ├── database/
    │   ├── __init__.py       # Exporta o gerenciador de conexões
    │   ├── connection.py     # Context Manager do SQLite (Modo WAL)
    │   └── schema.sql        # Estrutura das tabelas fiscais
    │
    ├── engines/
    │   ├── __init__.py       # Exporta as funções principais de cálculo
    │   ├── seed_db.py        # Script de carga inicial das tabelas da RFB
    │   ├── simples_nacional.py
    │   ├── lucro_presumido.py
    │   └── lucro_real.py
    │
    └── models/
        ├── __init__.py       # Exporta os schemas de dados
        └── fiscal_schemas.py # Modelos Pydantic (Request/Response)