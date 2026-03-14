import re
import json
import ollama
from bs4 import BeautifulSoup

class BDDTranslator:
    """Traduz e normaliza steps de PT-BR para o padrão Gherkin."""
    def __init__(self):
        self.mapping = {
            r"^(Dado que|Dado|Given) ": "Given ",
            r"^(Quando|Quando que|When) ": "When ",
            r"^(Então|Entao|Then) ": "Then ",
            r"^(E|Mas|And|But) ": "And "
        }

    def translate_step(self, step_text):
        for pattern, replacement in self.mapping.items():
            if re.match(pattern, step_text, re.IGNORECASE):
                return re.sub(pattern, replacement, step_text, flags=re.IGNORECASE)
        return step_text

class SemanticScanner:
    """Extrai elementos interativos do HTML para o mapeamento da IA."""
    def __init__(self):
        self.interactive_tags = ['button', 'input', 'a', 'select', 'textarea']

    def get_simplified_dom(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        simplified_elements = []
        for tag in self.interactive_tags:
            for el in soup.find_all(tag):
                element_data = {
                    "tag": tag,
                    "id": el.get('id', ''),
                    "name": el.get('name', ''),
                    "text": el.get_text().strip()[:50],
                    "placeholder": el.get('placeholder', ''),
                    "type": el.get('type', ''),
                    "class": ".".join(el.get('class', []))
                }
                if any([element_data['id'], element_data['name'], element_data['text'], element_data['placeholder']]):
                    simplified_elements.append(element_data)
        return simplified_elements

class AIInterpreter:
    """Realiza a ponte com o Ollama (Local ou Docker)."""
    def __init__(self, model_name="llama3"):
        self.model = model_name
        self.client = ollama.Client(host='http://localhost:11434')

    def find_match(self, step_text, simplified_elements):
        elements_context = ""
        for i, el in enumerate(simplified_elements):
            elements_context += f"ID:{i} | Tag:{el['tag']} | Text:'{el['text']}' | Placeholder:'{el['placeholder']}'\n"

        prompt = f"""
        Analise o STEP BDD: "{step_text}"
        Elementos na página:
        {elements_context}
        Qual ID (índice) melhor corresponde ao STEP e qual a ação (click, fill)?
        Responda APENAS JSON: {{"index": 0, "action": "click"}}
        """
        try:
            response = self.client.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            match = re.search(r'\{.*\}', content, re.DOTALL)
            return json.loads(match.group()) if match else None
        except Exception as e:
            print(f"Erro IA: {e}")
            return None