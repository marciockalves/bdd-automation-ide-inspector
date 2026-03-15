import os
import sys

if sys.platform == "linux":
    # Força a renderização em software se a GPU estiver causando Segfault
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox --disable-dev-shm-usage"

from PySide6.QtWidgets import QHBoxLayout, QListWidget, QToolBar, QStackedWidget, QApplication, QMainWindow, QSplitter
from PySide6.QtCore import QSize, QThread, Qt
from src.settings import SettingsDialog
import qtawesome as qta

# Importe suas classes recém-criadas
from src.editor import ScenarioEditor
from src.generator import CodeGenerator
from src.inspector import WebInspector
from src.ai_engine import BDDTranslator, SemanticScanner, AIInterpreter
from src.workers import AIWorker

from src.crawler import SimpleCrawler
from dotenv import load_dotenv

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        load_dotenv() # Carrega as variáveis do seu novo arquivo .env
        self.simple_crawler = SimpleCrawler()
        
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
        self.active_threads = []
        self.setup_ui_elements()
        self.setup_toolbar()

    def setup_ui_elements(self):
            # O centro agora é um StackedWidget para trocar as visões
            self.central_stack = QStackedWidget()
            
            # Lado Esquerdo: Editor (Sempre visível)
            self.editor = ScenarioEditor()
            
            # Lado Direito: Alternância entre Browser e Monitor de Elementos
            self.inspector = WebInspector() # Seu Webview manual
            self.ia_monitor = QListWidget() # Lista de elementos abstraídos pelo crawler
            self.ia_monitor.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; font-family: 'Courier New';")

            self.central_stack.addWidget(self.inspector) # Index 0
            self.central_stack.addWidget(self.ia_monitor) # Index 1

            layout_principal = QHBoxLayout()
            splitter = QSplitter(Qt.Horizontal)
            splitter.addWidget(self.editor)
            splitter.addWidget(self.central_stack)
            self.setCentralWidget(splitter)
    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Ações da Toolbar
        act_manual = toolbar.addAction(qta.icon("fa5s.search"), " Novo Cenário (Inspetor Manual)")
        act_manual.triggered.connect(self.mode_manual)

        act_ia = toolbar.addAction(qta.icon("fa5s.magic"), " Novo Cenário (Assistente IA)")
        act_ia.triggered.connect(self.mode_ia)

        toolbar.addSeparator()

        act_settings = toolbar.addAction(qta.icon("fa5s.cog"), " Configurações (.env)")
        act_settings.triggered.connect(self.open_settings)

    def mode_manual(self):
        self.central_stack.setCurrentIndex(0)
        self.editor.set_mode("manual")
        self.statusBar().showMessage("Modo Inspetor Manual Ativo.")

    def mode_ia(self):
        self.central_stack.setCurrentIndex(1)
        self.editor.set_mode("ia")
        self.statusBar().showMessage("Modo Assistente de IA Ativo (Crawler Mode).")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.statusBar().showMessage("Configurações atualizadas!", 3000)

    def run_ai_mapping(self):
        current_item = self.editor.list_steps.currentItem()
        if not current_item:
            return

        self.set_ai_loading_state(True)
        
        # Pega o host configurado no formulário de Settings
        host = os.getenv("BASE_HOST")
        if not host:
            self.statusBar().showMessage("❌ Erro: Configure o HOST nas configurações!")
            self.set_ai_loading_state(False)
            return

        if self.active_mode == "ia":
            self.ia_monitor.clear()
            self.ia_monitor.addItem(f"🌐 Acessando Host: {host}...")
            
            # 1. O Crawler baixa o HTML (Síncrono aqui por simplicidade, mas o UI não trava)
            html = self.simple_crawler.fetch_html(host)
            
            if html:
                self.ia_monitor.addItem("📄 HTML Capturado com sucesso.")
                # 2. Chama a thread da IA (que já criamos) passando o HTML bruto
                self.start_ai_worker_thread(html)
            else:
                self.handle_ai_error("Não foi possível acessar o site via Crawler.")
        else:
            # Modo manual continua usando o Webview (Seletivo)
            self.inspector.browser.page().toHtml(self.start_ai_worker_thread)
   
    def handle_manual_capture(self, selector):
        """Caso o usuário prefira clicar manualmente no elemento"""
        self.editor.mark_step_as_mapped(selector)

    def start_ai_worker_thread(self, html_content):
        # Aqui fica toda aquela lógica de QThread que já tínhamos, 
        # mas agora ela aceita QUALQUER HTML que você enviar para ela.
        elements = self.scanner.get_simplified_dom(html_content)
        thread = QThread()
        worker = AIWorker(self.ai, ..., elements)
        # ... conexões de sinais ...
        thread.start()    

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

    def set_ai_loading_state(self, is_loading: bool):
        """Ativa ou desativa o estado de 'carregamento' da interface"""
        if is_loading:
            self.editor.btn_ai.setEnabled(False)
            self.editor.btn_ai.setText("⌛ IA a pensar...")
            self.editor.btn_ai.setStyleSheet("background-color: #555; color: white;")
            # Se tiver uma barra de progresso no editor:
            self.editor.progress_bar.setVisible(True)
        else:
            self.editor.btn_ai.setEnabled(True)
            self.editor.btn_ai.setText("🪄 Mapear com IA")
            self.editor.btn_ai.setStyleSheet("") # Volta ao estilo padrão do sistema
            self.editor.progress_bar.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())