import sqlite3
import os

# Define caminhos absolutos precisos usando a raiz do projeto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "src/database/schema.sql")

def inicializar_tabelas():
    """Lê o arquivo schema.sql e cria a estrutura das tabelas caso não existam."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Arquivo schema.sql não foi encontrado em: {SCHEMA_PATH}")
        
    print("🏗️ Inicializando estrutura do banco de dados através do schema.sql...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("✅ Estrutura de tabelas verificada/criada com sucesso!")

def popular_dados_simples():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM faixas_simples_nacional;")
    cursor.execute("DELETE FROM reparticao_simples_nacional;")
    
    faixas = [
        # --- ANEXO I (Comércio) ---
        ('ANEXO_I', 1, 0.00, 180000.00, 0.0400, 0.00),
        ('ANEXO_I', 2, 180000.00, 360000.00, 0.0730, 5940.00),
        ('ANEXO_I', 3, 360000.00, 720000.00, 0.0950, 13860.00),
        ('ANEXO_I', 4, 720000.00, 1800000.00, 0.1070, 22500.00),
        ('ANEXO_I', 5, 1800000.00, 3600000.00, 0.1430, 87300.00),
        ('ANEXO_I', 6, 3600000.00, 4800000.00, 0.1900, 378000.00),

        # --- ANEXO II (Indústria) ---
        ('ANEXO_II', 1, 0.00, 180000.00, 0.0450, 0.00),
        ('ANEXO_II', 2, 180000.00, 360000.00, 0.0780, 5940.00),
        ('ANEXO_II', 3, 360000.00, 720000.00, 0.1000, 13860.00),
        ('ANEXO_II', 4, 720000.00, 1800000.00, 0.1120, 22500.00),
        ('ANEXO_II', 5, 1800000.00, 3600000.00, 0.1470, 85500.00),
        ('ANEXO_II', 6, 3600000.00, 4800000.00, 0.3000, 720000.00),

        # --- ANEXO III (Serviços Gerais / TI com Fator R) ---
        ('ANEXO_III', 1, 0.00, 180000.00, 0.0600, 0.00),
        ('ANEXO_III', 2, 180000.00, 360000.00, 0.1120, 9360.00),
        ('ANEXO_III', 3, 360000.00, 720000.00, 0.1350, 17640.00),
        ('ANEXO_III', 4, 720000.00, 1800000.00, 0.1600, 35640.00),
        ('ANEXO_III', 5, 1800000.00, 3600000.00, 0.2100, 125640.00),
        ('ANEXO_III', 6, 3600000.00, 4800000.00, 0.3300, 648000.00),

        # --- ANEXO IV (Serviços c/ Retenção de INSS) ---
        ('ANEXO_IV', 1, 0.00, 180000.00, 0.0450, 0.00),
        ('ANEXO_IV', 2, 180000.00, 360000.00, 0.0900, 8100.00),
        ('ANEXO_IV', 3, 360000.00, 720000.00, 0.1020, 12420.00),
        ('ANEXO_IV', 4, 720000.00, 1800000.00, 0.1400, 39780.00),
        ('ANEXO_IV', 5, 1800000.00, 3600000.00, 0.2200, 183780.00),
        ('ANEXO_IV', 6, 3600000.00, 4800000.00, 0.3300, 828000.00),

        # --- ANEXO V (Serviços Intelectuais) ---
        ('ANEXO_V', 1, 0.00, 180000.00, 0.1550, 0.00),
        ('ANEXO_V', 2, 180000.00, 360000.00, 0.1800, 4500.00),
        ('ANEXO_V', 3, 360000.00, 720000.00, 0.1950, 9900.00),
        ('ANEXO_V', 4, 720000.00, 1800000.00, 0.2050, 17100.00),
        ('ANEXO_V', 5, 1800000.00, 3600000.00, 0.2300, 62100.00),
        ('ANEXO_V', 6, 3600000.00, 4800000.00, 0.3050, 540000.00)
    ]
    
    reparticoes = [
        # --- ANEXO I ---
        ('ANEXO_I', 1, 0.0550, 0.0350, 0.0276, 0.1274, 0.4150, 0.3400),
        ('ANEXO_I', 2, 0.0550, 0.0350, 0.0276, 0.1274, 0.4150, 0.3400),
        ('ANEXO_I', 3, 0.0550, 0.0350, 0.0276, 0.1274, 0.4200, 0.3350),
        ('ANEXO_I', 4, 0.0550, 0.0350, 0.0276, 0.1274, 0.4200, 0.3350),
        ('ANEXO_I', 5, 0.0550, 0.0350, 0.0276, 0.1274, 0.4200, 0.3350),
        ('ANEXO_I', 6, 0.1350, 0.1000, 0.0613, 0.2827, 0.4210, 0.0000),

        # --- ANEXO II ---
        ('ANEXO_II', 1, 0.0550, 0.0350, 0.0249, 0.1151, 0.3750, 0.3200),
        ('ANEXO_II', 2, 0.0550, 0.0350, 0.0249, 0.1151, 0.3750, 0.3200),
        ('ANEXO_II', 3, 0.0550, 0.0350, 0.0249, 0.1151, 0.3750, 0.3200),
        ('ANEXO_II', 4, 0.0550, 0.0350, 0.0249, 0.1151, 0.3750, 0.3200),
        ('ANEXO_II', 5, 0.0550, 0.0350, 0.0249, 0.1151, 0.3750, 0.3200),
        ('ANEXO_II', 6, 0.0850, 0.0750, 0.0454, 0.2096, 0.2350, 0.0000),

        # --- ANEXO III ---
        ('ANEXO_III', 1, 0.0400, 0.0350, 0.0278, 0.1282, 0.4340, 0.3350),
        ('ANEXO_III', 2, 0.0400, 0.0350, 0.0305, 0.1405, 0.4340, 0.3200),
        ('ANEXO_III', 3, 0.0400, 0.0350, 0.0296, 0.1364, 0.4340, 0.3250),
        ('ANEXO_III', 4, 0.0400, 0.0350, 0.0296, 0.1364, 0.4340, 0.3250),
        ('ANEXO_III', 5, 0.0400, 0.0350, 0.0278, 0.1282, 0.4340, 0.3350),
        ('ANEXO_III', 6, 0.3500, 0.1500, 0.0347, 0.1603, 0.3050, 0.0000),

        # --- ANEXO IV ---
        ('ANEXO_IV', 1, 0.1880, 0.1520, 0.0383, 0.1767, 0.0000, 0.4450),
        ('ANEXO_IV', 2, 0.1980, 0.1520, 0.0445, 0.2055, 0.0000, 0.4000),
        ('ANEXO_IV', 3, 0.2080, 0.1520, 0.0427, 0.1973, 0.0000, 0.4000),
        ('ANEXO_IV', 4, 0.1780, 0.1920, 0.0410, 0.1890, 0.0000, 0.4000),
        ('ANEXO_IV', 5, 0.1880, 0.1920, 0.0392, 0.1808, 0.0000, 0.4000),
        ('ANEXO_IV', 6, 0.5350, 0.2150, 0.0445, 0.2055, 0.0000, 0.0000),

        # --- ANEXO V ---
        ('ANEXO_V', 1, 0.2500, 0.1500, 0.0305, 0.1410, 0.2885, 0.1400),
        ('ANEXO_V', 2, 0.2300, 0.1500, 0.0305, 0.1410, 0.2785, 0.1700),
        ('ANEXO_V', 3, 0.2400, 0.1500, 0.0323, 0.1492, 0.2385, 0.1900),
        ('ANEXO_V', 4, 0.2100, 0.1500, 0.0341, 0.1574, 0.2385, 0.2100),
        ('ANEXO_V', 5, 0.2300, 0.1250, 0.0305, 0.1410, 0.2385, 0.2350),
        ('ANEXO_V', 6, 0.3500, 0.1550, 0.0356, 0.1644, 0.2950, 0.0000)
    ]

    cursor.executemany("""
        INSERT INTO faixas_simples_nacional (anexo, faixa_numero, limite_inferior, limite_superior, aliquota_nominal, parcela_a_deduzir)
        VALUES (?, ?, ?, ?, ?, ?);
    """, faixas)
    
    cursor.executemany("""
        INSERT INTO reparticao_simples_nacional (anexo, faixa_numero, percentual_irpj, percentual_csll, percentual_pis, percentual_cofins, percentual_cpp, percentual_iss_icms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, reparticoes)

    conn.commit()
    conn.close()
    print("✨ Massa de dados (Seed) de todos os 5 anexos do Simples Nacional carregada com sucesso!")


def popular_dados_presumido():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM parametros_fiscais_fixos WHERE regime = 'LUCRO_PRESUMIDO';")
    
    parametros = [
        ('LUCRO_PRESUMIDO', 'presuncao_irpj_comercio_industria', 0.0800, 'Alíquota IRPJ para Comércio, Indústria e Construção'),
        ('LUCRO_PRESUMIDO', 'presuncao_csll_comercio_industria', 0.1200, 'Alíquota CSLL para Comércio, Indústria e Construção'),
        ('LUCRO_PRESUMIDO', 'presuncao_irpj_combustiveis', 0.0160, 'Alíquota IRPJ para Revenda de Combustíveis'),
        ('LUCRO_PRESUMIDO', 'presuncao_csll_combustiveis', 0.1200, 'Alíquota CSLL para Revenda de Combustíveis'),
        ('LUCRO_PRESUMIDO', 'presuncao_irpj_transporte_cargas', 0.0800, 'Alíquota IRPJ para Transporte de Cargas'),
        ('LUCRO_PRESUMIDO', 'presuncao_csll_transporte_cargas', 0.1200, 'Alíquota CSLL para Transporte de Cargas'),
        ('LUCRO_PRESUMIDO', 'presuncao_irpj_transporte_geral', 0.1600, 'Alíquota IRPJ para Transporte Geral'),
        ('LUCRO_PRESUMIDO', 'presuncao_csll_transporte_geral', 0.1200, 'Alíquota CSLL para Transporte Geral'),
        ('LUCRO_PRESUMIDO', 'presuncao_irpj_servicos_padrao', 0.3200, 'Alíquota IRPJ Padrão para Serviços'),
        ('LUCRO_PRESUMIDO', 'presuncao_csll_servicos_padrao', 0.3200, 'Alíquota CSLL Padrão para Serviços'),
        ('LUCRO_PRESUMIDO', 'presuncao_irpj_servicos_reduzido', 0.1600, 'Alíquota IRPJ Reduzida para Serviços Gerais (Até 120k/ano)'),
        ('LUCRO_PRESUMIDO', 'limite_anual_servicos_reduzido', 120000.00, 'Limite anual para utilizar presunção de 16%'),
        ('LUCRO_PRESUMIDO', 'aliquota_pis', 0.0065, 'PIS Cumulativo'),
        ('LUCRO_PRESUMIDO', 'aliquota_cofins', 0.0300, 'COFINS Cumulativo'),
        ('LUCRO_PRESUMIDO', 'aliquota_csll', 0.0900, 'Alíquota de CSLL sobre a base'),
        ('LUCRO_PRESUMIDO', 'aliquota_irpj_base', 0.1500, 'Alíquota base de IRPJ sobre a base'),
        ('LUCRO_PRESUMIDO', 'aliquota_irpj_adicional', 0.1000, 'Adicional de IRPJ'),
        ('LUCRO_PRESUMIDO', 'limite_mensal_adicional_irpj', 20000.00, 'Isenção mensal do adicional')
    ]
    
    cursor.executemany("""
        INSERT INTO parametros_fiscais_fixos (regime, parametro_nome, valor, descricao)
        VALUES (?, ?, ?, ?);
    """, parametros)
    
    conn.commit()
    conn.close()
    print("✨ Massa de dados do Lucro Presumido carregada com sucesso!")


def popular_dados_lucro_real():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM parametros_fiscais_fixos WHERE regime = 'LUCRO_REAL';")
    
    parametros = [
        ('LUCRO_REAL', 'aliquota_pis', 0.0165, 'Alíquota mensal de PIS não cumulativo (1.65%)'),
        ('LUCRO_REAL', 'aliquota_cofins', 0.0760, 'Alíquota mensal de COFINS não cumulativo (7.60%)'),
        ('LUCRO_REAL', 'credito_pis_custos', 0.0165, 'Direito de crédito de PIS sobre insumos (1.65%)'),
        ('LUCRO_REAL', 'credito_cofins_custos', 0.0760, 'Direito de crédito de COFINS sobre insumos (7.60%)'),
        ('LUCRO_REAL', 'aliquota_csll', 0.0900, 'Alíquota padrão de CSLL (9%)'),
        ('LUCRO_REAL', 'aliquota_irpj_base', 0.1500, 'Alíquota base de IRPJ (15%)'),
        ('LUCRO_REAL', 'aliquota_irpj_adicional', 0.1000, 'Alíquota do Adicional de IRPJ (10%)'),
        ('LUCRO_REAL', 'limite_mensal_adicional_irpj', 20000.00, 'Limite mensal de isenção do adicional'),
        ('LUCRO_REAL', 'taxa_depreciacao_mensal_computadores', 0.016667, 'Taxa mensal de depreciação de computadores (20%/ano)'), # <-- Corrigido (Vírgula adicionada)
        ('LUCRO_REAL', 'aliquota_inss_patronal', 0.2000, 'INSS Patronal sobre a folha (20%)'),
        ('LUCRO_REAL', 'aliquota_rat_terceiros_estimado', 0.0580, 'Estimativa média de RAT + Terceiros (5.8%)')
    ]
    
    cursor.executemany("""
        INSERT INTO parametros_fiscais_fixos (regime, parametro_nome, valor, descricao)
        VALUES (?, ?, ?, ?);
    """, parametros)
    
    conn.commit()
    conn.close()
    print("✨ Massa de dados (Seed) do Lucro Real carregada com sucesso!")


if __name__ == "__main__":
    # Garante a criação da estrutura primeiro
    inicializar_tabelas()
    
    # Popula os dados
    popular_dados_simples()
    popular_dados_presumido()
    popular_dados_lucro_real()
    print("\n🚀 Banco de dados totalmente povoado e pronto para uso!")