-- Tabela que guarda as faixas e alíquotas brutas da lei
CREATE TABLE IF NOT EXISTS faixas_simples_nacional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anexo VARCHAR(10) NOT NULL,          -- 'ANEXO_I', 'ANEXO_III', 'ANEXO_V', etc.
    faixa_numero INTEGER NOT NULL,       -- 1, 2, 3, 4, 5 ou 6
    limite_inferior DECIMAL(12,2) NOT NULL,
    limite_superior DECIMAL(12,2) NOT NULL,
    aliquota_nominal DECIMAL(6,4) NOT NULL, -- Ex: 0.0600 para 6%
    parcela_a_deduzir DECIMAL(12,2) NOT NULL
);

-- Tabela que guarda a quebra interna de para onde vai o dinheiro em cada faixa
CREATE TABLE IF NOT EXISTS reparticao_simples_nacional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anexo VARCHAR(10) NOT NULL,
    faixa_numero INTEGER NOT NULL,
    percentual_irpj DECIMAL(5,4) NOT NULL,
    percentual_csll DECIMAL(5,4) NOT NULL,
    percentual_pis DECIMAL(5,4) NOT NULL,
    percentual_cofins DECIMAL(5,4) NOT NULL,
    percentual_cpp DECIMAL(5,4) NOT NULL,    -- INSS Patronal
    percentual_iss_icms DECIMAL(5,4) NOT NULL -- ISS se for serviço, ICMS se for comércio
);

CREATE TABLE IF NOT EXISTS parametros_fiscais_fixos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regime VARCHAR(20) NOT NULL,       -- 'LUCRO_PRESUMIDO' ou 'LUCRO_REAL'
    parametro_nome VARCHAR(50) NOT NULL, -- Ex: 'aliquota_pis', 'presuncao_irpj_servicos'
    valor DECIMAL(10,4) NOT NULL,
    descricao TEXT
);