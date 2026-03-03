# features/environment.py
from playwright.sync_api import sync_playwright

def before_all(context):
    # Inicia o Playwright
    context.playwright = sync_playwright().start()
    # Abre o navegador (headless=False para você ver o teste rodando)
    context.browser = context.playwright.chromium.launch(headless=False)

def before_scenario(context, scenario):
    # Cria uma nova página para cada cenário
    context.page = context.browser.new_page()

def after_scenario(context, scenario):
    # Fecha a página após o teste
    context.page.close()

def after_all(context):
    # Encerra o navegador e o Playwright
    context.browser.close()
    context.playwright.stop()