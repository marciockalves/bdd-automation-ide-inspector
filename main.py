import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QListWidget, QListWidgetItem, 
                             QPushButton, QLineEdit, QSplitter, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineScript

# Otimização para Linux (KDE/Fedora/Kubuntu)
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --ignore-gpu-blocklist"

class BDDGeneratorIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BDR - Automation Factory (v2.0)")
        self.resize(1500, 900)
        self.mapeamentos = {}
        self.seletor_atual = ""

        # Layout Principal
        main_layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # --- PAINEL ESQUERDO: EDITOR BDD ---
        self.painel_edit = QWidget()
        layout_left = QVBoxLayout(self.painel_edit)
        
        layout_left.addWidget(QLabel("<b>1. Adicionar Step:</b>"))
        self.input_step = QLineEdit()
        self.input_step.setPlaceholderText("Ex: When eu clico no botao login")
        self.input_step.returnPressed.connect(self.adicionar_step)
        layout_left.addWidget(self.input_step)
        
        self.lista_steps = QListWidget()
        layout_left.addWidget(self.lista_steps)

        # Painel de Inspeção
        inspecao_frame = QFrame()
        inspecao_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        layout_inspecao = QVBoxLayout(inspecao_frame)
        self.label_seletor = QLabel("Seletor: <i>Nenhum</i>")
        layout_inspecao.addWidget(self.label_seletor)
        self.btn_vincular = QPushButton("Vincular ao Step Selecionado")
        self.btn_vincular.setStyleSheet("background-color: #3498db; color: white; height: 30px;")
        self.btn_vincular.clicked.connect(self.vincular_seletor)
        layout_inspecao.addWidget(self.btn_vincular)
        layout_left.addWidget(inspecao_frame)
        
        self.btn_save = QPushButton("Gerar Projeto Behave")
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 40px;")
        self.btn_save.clicked.connect(self.exportar_projeto)
        layout_left.addWidget(self.btn_save)

        # --- PAINEL DIREITO: NAVEGADOR COM BARRA DE ENDEREÇO ---
        self.painel_nav = QWidget()
        layout_right = QVBoxLayout(self.painel_nav)

        # Barra de Endereços
        nav_bar = QHBoxLayout()
        self.btn_back = QPushButton("<")
        self.btn_forward = QPushButton(">")
        self.btn_reload = QPushButton("↻")
        self.url_bar = QLineEdit("https://www.saucedemo.com")
        
        nav_bar.addWidget(self.btn_back)
        nav_bar.addWidget(self.btn_forward)
        nav_bar.addWidget(self.btn_reload)
        nav_bar.addWidget(self.url_bar)
        layout_right.addLayout(nav_bar)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.url_bar.text()))
        layout_right.addWidget(self.browser)

        # Conectar ações da barra
        self.url_bar.returnPressed.connect(self.navegar)
        self.btn_back.clicked.connect(self.browser.back)
        self.btn_forward.clicked.connect(self.browser.forward)
        self.btn_reload.clicked.connect(self.browser.reload)
        self.browser.urlChanged.connect(self.atualizar_url_bar)

        self.splitter.addWidget(self.painel_edit)
        self.splitter.addWidget(self.painel_nav)
        self.splitter.setStretchFactor(1, 2)

        self.setup_inspector()

    def navegar(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.browser.setUrl(QUrl(url))

    def atualizar_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())

    def adicionar_step(self):
        txt = self.input_step.text().strip()
        if txt:
            item = QListWidgetItem(txt)
            self.lista_steps.addItem(item)
            self.mapeamentos[txt] = None
            self.input_step.clear()

    def setup_inspector(self):
        script_js = """
        (function() {
            let lastEl = null;
            const highlight = document.createElement('div');
            highlight.style.position = 'absolute';
            highlight.style.border = '2px dashed #e74c3c';
            highlight.style.backgroundColor = 'rgba(231, 76, 60, 0.2)';
            highlight.style.pointerEvents = 'none';
            highlight.style.zIndex = '1000000';
            document.body.appendChild(highlight);

            document.addEventListener('mousemove', function(e) {
                let el = e.target;
                if(el === highlight || el === lastEl) return;
                lastEl = el;
                let rect = el.getBoundingClientRect();
                highlight.style.width = rect.width + 'px';
                highlight.style.height = rect.height + 'px';
                highlight.style.top = (rect.top + window.scrollY) + 'px';
                highlight.style.left = (rect.left + window.scrollX) + 'px';
                
                let sel = el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + el.className.split(' ').join('.');
                console.log("HOVER:" + sel);
            });

            document.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                let el = e.target;
                let sel = el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + el.className.split(' ').join('.');
                console.log("SELECT:" + sel);
            }, true);
        })();
        """
        script = QWebEngineScript()
        script.setSourceCode(script_js)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        self.browser.page().scripts().insert(script)
        self.browser.page().javaScriptConsoleMessage = self.on_console_msg

    def on_console_msg(self, level, msg, line, sourceid):
        if "HOVER:" in msg:
            self.seletor_atual = msg.replace("HOVER:", "")
            self.label_seletor.setText(f"Inspecionando: <b>{self.seletor_atual}</b>")
        if "SELECT:" in msg:
            self.seletor_atual = msg.replace("SELECT:", "")
            self.label_seletor.setText(f"Selecionado: <b style='color: #2980b9;'>{self.seletor_atual}</b>")

    def vincular_seletor(self):
        item = self.lista_steps.currentItem()
        if item and self.seletor_atual:
            original_text = item.data(Qt.UserRole) or item.text()
            item.setData(Qt.UserRole, original_text)
            self.mapeamentos[original_text] = self.seletor_atual
            item.setBackground(Qt.green)
            item.setText(f"{original_text} ✔")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um Step e clique em um elemento no navegador!")

    def exportar_projeto(self):
        try:
            os.makedirs("features/steps", exist_ok=True)
            
            # 1. Feature
            with open("features/automacao.feature", "w", encoding="utf-8") as f:
                f.write("Feature: Fluxo Gerado\n\n  Scenario: Execucao de Teste\n")
                for step in self.mapeamentos.keys():
                    f.write(f"    {step}\n")

            # 2. Steps
            with open("features/steps/steps.py", "w", encoding="utf-8") as f:
                f.write("from behave import step\nfrom playwright.sync_api import expect\n\n")
                for step_txt, sel in self.mapeamentos.items():
                    if sel:
                        clean = step_txt.split(" ", 1)[1] if " " in step_txt else step_txt
                        acao = "fill('DADO')" if "preencho" in step_txt.lower() else "click()"
                        f.write(f"@step('{clean}')\ndef step_impl(context):\n    context.page.locator('{sel}').{acao}\n\n")

            # 3. Environment
            with open("features/environment.py", "w", encoding="utf-8") as f:
                f.write("from playwright.sync_api import sync_playwright\n\ndef before_all(context):\n    context.p = sync_playwright().start()\n    context.browser = context.p.chromium.launch(headless=False)\n\ndef before_scenario(context, scenario):\n    context.page = context.browser.new_page()\n\ndef after_all(context):\n    context.browser.close()\n    context.p.stop()\n")

            QMessageBox.information(self, "Sucesso", "Projeto completo gerado em /features!\nExecute: uv run behave")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BDDGeneratorIDE()
    window.show()
    sys.exit(app.exec())