from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton
from PySide6.QtCore import Qt, Signal

class ScenarioEditor(QWidget):
    # Sinal enviado quando um step é selecionado para ser mapeado
    step_selected = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>Cenário BDD:</b>"))
        self.input_step = QLineEdit()
        self.input_step.setPlaceholderText("Ex: When clico no login")
        self.input_step.returnPressed.connect(self.add_step)
        layout.addWidget(self.input_step)

        self.list_steps = QListWidget()
        layout.addWidget(self.list_steps)
        
        self.btn_export = QPushButton("Gerar Código")
        self.btn_export.setStyleSheet("background-color: #27ae60; color: white;")
        layout.addWidget(self.btn_export)

    def add_step(self):
        text = self.input_step.text().strip()
        if text:
            item = QListWidgetItem(text)
            self.list_steps.addItem(item)
            self.input_step.clear()

    def get_selected_step_text(self):
        item = self.list_steps.currentItem()
        return item.text() if item else None

    def mark_step_as_mapped(self, selector):
        item = self.list_steps.currentItem()
        if item:
            item.setBackground(Qt.green)
            item.setText(f"{item.text()} [Mapeado: {selector}]")