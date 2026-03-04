import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QMessageBox
from PySide6.QtCore import Qt

# Importando seus componentes
from src.main_tool_bar import MainToolBar
from src.editor import ScenarioEditor
from src.inspector import WebInspector

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"

class BDDApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BDR IDE - Modular Architecture")
        self.resize(1400, 800)

        # 1. Barra de Ferramentas
        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        # 2. Componentes Centrais
        self.editor = ScenarioEditor()
        self.inspector = WebInspector()

        # 3. Layout com Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.inspector)
        splitter.setStretchFactor(1, 2) # Dá mais espaço ao navegador
        self.setCentralWidget(splitter)

        # 4. Orquestração (Conectar os componentes)
        self.inspector.element_selected.connect(self.on_element_captured)

    def on_element_captured(self, selector):
        step_text = self.editor.get_selected_step_text()
        if step_text:
            self.editor.mark_step_as_mapped(selector)
            print(f"Vinculado: {step_text} -> {selector}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um step na lista antes de clicar no elemento!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BDDApp()
    window.show()
    sys.exit(app.exec())