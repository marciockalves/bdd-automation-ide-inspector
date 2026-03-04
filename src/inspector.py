from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineScript
from PySide6.QtCore import QUrl, Signal

class WebInspector(QWidget):
    # Sinal enviado quando o usuário clica em um elemento
    element_selected = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Barra de Endereço
        nav_layout = QHBoxLayout()
        self.url_bar = QLineEdit("https://www.google.com")
        self.btn_go = QPushButton("Ir")
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.btn_go)
        layout.addLayout(nav_layout)

        # Navegador
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Configurações
        self.btn_go.clicked.connect(self.navigate)
        self.url_bar.returnPressed.connect(self.navigate)
        self.setup_scripts()

    def navigate(self):
        url = self.url_bar.text()
        if not url.startswith("http"): url = "https://" + url
        self.browser.setUrl(QUrl(url))

    def setup_scripts(self):
        script_js = """
        document.addEventListener('click', function(e) {
            e.preventDefault(); e.stopPropagation();
            let el = e.target;
            let sel = el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + el.className.split(' ').join('.');
            console.log("CAPTURED_SELECTOR:" + sel);
        }, true);
        """
        script = QWebEngineScript()
        script.setSourceCode(script_js)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        self.browser.page().scripts().insert(script)
        self.browser.page().javaScriptConsoleMessage = self._on_console_message

    def _on_console_message(self, level, message, line, sourceid):
        if "CAPTURED_SELECTOR:" in message:
            selector = message.replace("CAPTURED_SELECTOR:", "")
            self.element_selected.emit(selector)