import os
import sys

if sys.platform == "linux":
    # Força a renderização em software se a GPU estiver causando Segfault
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox --disable-dev-shm-usage"

from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter
from PySide6.QtCore import QThread, Qt

# Importe suas classes recém-criadas
from src.editor import ScenarioEditor
from src.generator import CodeGenerator
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
        
        self.generator = CodeGenerator()
        self.editor.btn_export.clicked.connect(self.export_test_files)

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
        """Executado quando a thread da IA termina"""
        self.editor.setEnabled(True)
        
        # 1. Recuperamos o item que estava selecionado
        current_item = self.editor.list_steps.currentItem()
        if not current_item or 'index' not in result:
            self.statusBar().showMessage("❌ IA não encontrou um elemento compatível.")
            return

        # 2. Em vez de re-analisar o HTML, vamos extrair o seletor 
        # do mapeamento que já temos guardado ou processar rápido:
        self.inspector.browser.page().toHtml(lambda html: self.finalize_mapping_and_save(html, result, current_item))

    def finalize_mapping_and_save(self, html, result, item):
        # Gera a lista de elementos novamente baseada no HTML do momento da resposta
        elements = self.scanner.get_simplified_dom(html)
        
        try:
            target = elements[result['index']]
            selector = self.scanner.generate_selector(target)
            
            # --- O PULO DO GATO ---
            # Gravamos o seletor no UserRole do item para o gerador de código enxergar
            item.setData(Qt.UserRole, selector)
            
            # Adiciona o check visual
            if " ✔" not in item.text():
                item.setText(f"{item.text()} ✔")
            
            item.setBackground(Qt.transparent) # Limpa cores de erro se houver
            self.statusBar().showMessage(f"✅ Step mapeado para: {selector}", 3000)
            
        except IndexError:
            self.statusBar().showMessage("❌ Erro de sincronia no mapeamento.")

    def handle_ai_error(self, message):
        """Executado se a IA falhar"""
        self.editor.setEnabled(True)
        self.statusBar().showMessage(f"❌ Erro na IA: {message}", 5000)

    def export_test_files(self):
        """Pega os dados da lista e gera os arquivos físicos"""
        steps_data = []
        for i in range(self.editor.list_steps.count()):
            item = self.editor.list_steps.item(i)
            selector = item.data(Qt.UserRole)
            
            if selector: # Apenas steps que foram mapeados pela IA ou manual
                steps_data.append({
                    "text": item.text().replace(" ✔", ""),
                    "selector": selector
                })

        if not steps_data:
            self.statusBar().showMessage("⚠️ Nenhum step mapeado para exportação!", 5000)
            return

        # Gera os arquivos
        feat_path = self.generator.save_feature_file("MeuCenarioIA", steps_data)
        step_path = self.generator.save_steps_file("MeuCenarioIA", steps_data)

        self.statusBar().showMessage(f"🚀 Arquivos gerados em: {self.generator.output_dir}", 6000)
        print(f"✅ Sucesso! Arquivos criados:\n- {feat_path}\n- {step_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())