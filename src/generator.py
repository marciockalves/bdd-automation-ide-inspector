import os

class CodeGenerator:
    def __init__(self, output_dir="features"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_feature_file(self, scenario_name, steps):
        """Gera o arquivo .feature"""
        filename = f"{scenario_name.lower().replace(' ', '_')}.feature"
        path = os.path.join(self.output_dir, filename)
        
        content = f"Feature: {scenario_name}\n\n"
        content += f"  Scenario: Execução gerada pelo Feature Editor Pro\n"
        
        for step in steps:
            content += f"    {step['text']}\n"
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def save_steps_file(self, scenario_name, steps):
        """Gera o arquivo de steps Python com Playwright"""
        filename = f"test_{scenario_name.lower().replace(' ', '_')}_steps.py"
        path = os.path.join(self.output_dir, filename)
        
        content = "from behave import given, when, then\n"
        content += "from playwright.sync_api import sync_playwright\n\n"
        
        for step in steps:
            # Limpa o prefixo para a definição da função
            clean_text = step['text'].split(" ", 1)[1]
            func_name = clean_text.lower().replace(" ", "_").replace('"', '')
            selector = step['selector']
            
            # Determina a ação baseada no mapeamento da IA
            if "clico" in step['text'].lower() or "clicar" in step['text'].lower():
                action = f"page.click('{selector}')"
            elif "preencho" in step['text'].lower() or "digito" in step['text'].lower():
                action = f"page.fill('{selector}', 'valor_exemplo')"
            else:
                action = f"page.wait_for_selector('{selector}')"

            content += f"@step('{clean_text}')\ndef {func_name}(context):\n"
            content += f"    context.page.{action}\n\n"
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path