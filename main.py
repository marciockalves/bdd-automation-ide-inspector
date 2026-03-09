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

        self.editor.request_start_inspection.connect(lambda: self.inspector.toggle_inspection(True))

        self.inspector.element_selected.connect(self.on_element_captured)


    def on_element_captured(self, selector):
        item = self.editor.list_steps.currentItem()
        if item:
            # 2. Marca no editor (fica verde e ganha o check)
            self.editor.mark_step_as_mapped(selector)
            # 3. Desliga a inspeção para dar feedback de "Tarefa Concluída"
            self.inspector.toggle_inspection(False)
        else:
            # Se não houver step selecionado, avise o usuário
            QMessageBox.warning(self, "Atenção", "Selecione um Step na lista antes de capturar!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BDDApp()
    window.show()
    sys.exit(app.exec())