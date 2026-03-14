import json
import re
from PySide6.QtCore import QObject, Signal, Slot

class AIWorker(QObject):
    """Trabalhador que executa a IA em background para não travar a UI."""
    finished = Signal(dict)  # Sinal emitido quando a IA termina
    error = Signal(str)      # Sinal emitido em caso de falha

    def __init__(self, ai_interpreter, step_text, elements):
        super().__init__()
        self.ai = ai_interpreter
        self.step_text = step_text
        self.elements = elements

    @Slot()
    def run(self):
        try:
            # Chama o método que faz a requisição ao Ollama
            result = self.ai.find_match(self.step_text, self.elements)
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("A IA não retornou um resultado válido.")
        except Exception as e:
            self.error.emit(str(e))