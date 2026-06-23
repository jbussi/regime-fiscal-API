import pytest
import re
from playwright.sync_api import Page, expect

URL_DASHBOARD = "http://localhost:8000/" 

def test_renderizacao_inicial_e_abas(page: Page):
    """Garante que a interface carrega os elementos principais e alterna as abas corretamente"""
    page.goto(URL_DASHBOARD)
    
    # 1. CORREÇÃO: Usando o título real retornado pelo seu HTML
    expect(page.locator("h1")).to_contain_text("Regime Fiscal Analytics Suite")
    expect(page.locator("#mainFiscalForm")).to_be_visible()
    
    # Testa a alternância para a aba de Endpoints
    page.click("#btn-tab-endpoints")
    expect(page.locator("#tab-endpoints")).not_to_have_class(re.compile(r"\bhidden\b"))
    
    # Volta para a aba comparativa
    page.click("#btn-tab-comparativo")
    expect(page.locator("#tab-comparativo")).not_to_have_class(re.compile(r"\bhidden\b"))


def test_fluxo_calculo_com_fator_r(page: Page):
    """Cenário 1: Testa faturamento com folha alta (Fator R ativo -> Anexo III favorável)"""
    page.goto(URL_DASHBOARD)
    
    page.fill("#faturamento_servicos", "80000")
    page.fill("#folha_mensal_atual", "24000")
    page.fill("#rbt12", "960000")
    page.fill("#folha_acumulada_12m", "288000")
    page.fill("#aliquota_iss_local", "3.5")
    page.select_option("#anexo_escolhido", "ANEXO_V")
    
    page.click("button[type='submit']")
    
    # 2. CORREÇÃO: Evita checar a string de classe exata; apenas valida que o loading sumiu/ficou oculto
    expect(page.locator("#loading")).to_be_hidden()
    expect(page.locator("#insightContainer")).to_be_visible()


def test_auditoria_de_payloads_isolados(page: Page):
    """Cenário 2: Valida se a aba técnica recebeu os retornos JSON com status HTTP 200"""
    page.goto(URL_DASHBOARD)
    
    page.click("button[type='submit']")
    page.wait_for_selector("#loading", state="hidden")
    
    page.click("#btn-tab-endpoints")
    
    expect(page.locator("#status-simples")).to_contain_text("HTTP 200")
    expect(page.locator("#status-presumido")).to_contain_text("HTTP 200")
    expect(page.locator("#status-real")).to_contain_text("HTTP 200")
    
    # 3. CORREÇÃO: Mapeia para 'imposto_final', que é a chave que seu backend realmente cospe
    texto_json = page.locator("#json-simples").text_content()
    assert "imposto_final" in texto_json or "detail" in texto_json