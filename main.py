import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter
from PySide6.QtCore import QThread, Qt

# Importe suas classes recém-criadas
from src.editor import ScenarioEditor
from src.inspector import WebInspector
from src.ai_engine import BDDTranslator, SemanticScanner, AIInterpreter
from src.workers import AIWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feature Editor Pro - IA Edition")
        self.resize(1200, 800)

        # Inicializa o cérebro da IA
        self.translator = BDDTranslator()
        self.scanner = SemanticScanner()
        self.ai = AIInterpreter(model_name="llama3")

        # UI Components
        self.editor = ScenarioEditor()
        self.inspector = WebInspector()

        # Layout com Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.inspector)
        splitter.setStretchFactor(1, 2)
        self.setCentralWidget(splitter)

        # --- CONEXÕES ---
        # 1. Quando clicar no botão de IA no editor
        self.editor.request_ai_assistant.connect(self.run_ai_mapping)
        
        # 2. Quando o inspetor capturar algo manualmente (seletor vindo do JS)
        self.inspector.element_selected.connect(self.handle_manual_capture)

    def run_ai_mapping(self):
        current_item = self.editor.list_steps.currentItem()
        if not current_item:
            return

        step_text = current_item.text()
        normalized_step = self.translator.translate_step(step_text)

        # Feedback visual imediato na UI
        self.statusBar().showMessage(f"🤖 IA está processando: {step_text}...")
        self.editor.setEnabled(False) # Desabilita o editor temporariamente

        def on_html_received(html_content):
            elements = self.scanner.get_simplified_dom(html_content)
            
            # --- CONFIGURAÇÃO DA THREAD ---
            self.thread = QThread()
            self.worker = AIWorker(self.ai, normalized_step, elements)
            self.worker.moveToThread(self.thread)

            # Conectar sinais
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.handle_ai_success)
            self.worker.error.connect(self.handle_ai_error)
            
            # Limpeza de memória
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

        self.inspector.browser.page().toHtml(on_html_received)
    def handle_manual_capture(self, selector):
        """Caso o usuário prefira clicar manualmente no elemento"""
        self.editor.mark_step_as_mapped(selector)

    

    def handle_ai_success(self, result):
        """Executado quando a thread da IA termina com sucesso"""
        self.editor.setEnabled(True)
        self.statusBar().showMessage("✅ Mapeamento concluído!", 3000)
        
        # Recupera os elementos novamente para gerar o seletor final
        # (Em um app real, você passaria o seletor pronto do worker)
        # Aqui vamos simplificar usando o resultado do índice
        self.inspector.browser.page().toHtml(lambda html: self.finalize_mapping(html, result))

    def finalize_mapping(self, html, result):
        elements = self.scanner.get_simplified_dom(html)
        target = elements[result['index']]
        selector = self.scanner.generate_selector(target)
        self.editor.mark_step_as_mapped(selector)

    def handle_ai_error(self, message):
        """Executado se a IA falhar"""
        self.editor.setEnabled(True)
        self.statusBar().showMessage(f"❌ Erro na IA: {message}", 5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())