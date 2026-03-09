from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineScript, QWebEnginePage
from PySide6.QtCore import QUrl, Signal

class WebInspector(QWidget):
    element_selected = Signal(str)
    preview_selector = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Barra de Navegação
        nav_layout = QHBoxLayout()
        self.url_bar = QLineEdit("https://www.saucedemo.com")
        self.btn_go = QPushButton("Ir")
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.btn_go)
        layout.addLayout(nav_layout)

        # Navegador
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Conexões
        self.btn_go.clicked.connect(self.navigate)
        self.url_bar.returnPressed.connect(self.navigate)
        
        # GARANTIA: Reinjetar o script sempre que a página carregar 100%
        self.browser.loadFinished.connect(self.setup_scripts)
        
        # Substituir o console original por um manipulador robusto
        self.browser.page().javaScriptConsoleMessage = self._on_console_message

    def navigate(self):
        url = self.url_bar.text()
        if not url.startswith("http"): url = "https://" + url
        self.browser.setUrl(QUrl(url))

    def setup_scripts(self):
        # Script injetado com verificação de existência para evitar duplicidade
        script_js = """
        (function() {
            if (window.bddInspectorInitialized) return;
            
            console.log("LOG: Sistema de Inspeção Inicializado");
            
            const highlight = document.createElement('div');
            highlight.id = 'bdd-highlighter';
            highlight.style.cssText = "position:absolute; border:2px solid #e74c3c; background:rgba(231,76,60,0.1); pointer-events:none; z-index:1000000; display:none; transition: all 0.05s ease;";
            document.body.appendChild(highlight);

            window.isInspecting = false;

            window.setInspectionMode = function(active) {
                window.isInspecting = active;
                highlight.style.display = active ? 'block' : 'none';
                highlight.style.borderColor = '#e74c3c';
            };

            document.addEventListener('mousemove', function(e) {
                if(!window.isInspecting) return;
                let el = e.target;
                if(el.id === 'bdd-highlighter') return;
                
                let rect = el.getBoundingClientRect();
                highlight.style.width = rect.width + 'px';
                highlight.style.height = rect.height + 'px';
                highlight.style.top = (rect.top + window.scrollY) + 'px';
                highlight.style.left = (rect.left + window.scrollX) + 'px';
                
                let sel = el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ').join('.') : '');
                console.log("HOVER_SELECTOR:" + sel);
            });

            document.addEventListener('click', function(e) {
                if(!window.isInspecting) return;
                e.preventDefault(); e.stopPropagation();
                
                highlight.style.borderColor = '#27ae60';
                highlight.style.backgroundColor = 'rgba(39, 174, 96, 0.4)';
                
                let el = e.target;
                let sel = el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ').join('.') : '');
                
                console.log("CAPTURED_SELECTOR:" + sel);
                
                setTimeout(() => { window.setInspectionMode(false); }, 300);
            }, true);

            window.bddInspectorInitialized = true;
        })();
        """
        self.browser.page().runJavaScript(script_js)

    def _on_console_message(self, level, message, line, sourceid):
        # Debug para você ver no terminal se o JS está "falando"
        if "LOG:" in message:
            print(f"Browser Info: {message}")
            
        if "CAPTURED_SELECTOR:" in message:
            selector = message.replace("CAPTURED_SELECTOR:", "")
            print(f"Capturado com sucesso: {selector}") # Confirmação no terminal
            self.element_selected.emit(selector)
            return True # Indica que a mensagem foi tratada
            
        if "HOVER_SELECTOR:" in message:
            selector = message.replace("HOVER_SELECTOR:", "")
            self.preview_selector.emit(selector)
            return True
        return False

    def toggle_inspection(self, active):
        val = "true" if active else "false"
        self.browser.page().runJavaScript(f"window.setInspectionMode({val});")