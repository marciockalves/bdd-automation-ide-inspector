import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QScrollArea, QWidget, QFrame)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Projeto")
        self.setMinimumWidth(500)
        self.layout = QVBoxLayout(self)

        # Host Principal
        self.layout.addWidget(QLabel("<b>URL Base / Host Principal:</b>"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("ex: https://meusistema.com.br")
        self.layout.addWidget(self.host_input)

        self.layout.addSpacing(15)
        self.layout.addWidget(QLabel("<b>Variáveis de Ambiente (.env):</b>"))
        
        # Área de Variáveis com Scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.vars_layout = QVBoxLayout(self.container)
        self.vars_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

        # Botões de Ação
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("+ Nova Variável")
        self.btn_add.clicked.connect(lambda: self.add_var_row())
        
        self.btn_save = QPushButton("SALVAR E APLICAR")
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; height: 35px;")
        self.btn_save.clicked.connect(self.save_and_close)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_save)
        self.layout.addLayout(btn_layout)

        self.load_current_env()

    def add_var_row(self, key="", value=""):
        row_widget = QFrame()
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 2, 0, 2)
        
        k_in = QLineEdit(key)
        k_in.setPlaceholderText("CHAVE")
        v_in = QLineEdit(value)
        v_in.setPlaceholderText("VALOR")
        
        btn_del = QPushButton("X")
        btn_del.setFixedWidth(30)
        btn_del.clicked.connect(lambda: row_widget.deleteLater())
        
        row.addWidget(k_in)
        row.addWidget(v_in)
        row.addWidget(btn_del)
        self.vars_layout.addWidget(row_widget)

    def load_current_env(self):
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        if k == "BASE_HOST":
                            self.host_input.setText(v)
                        else:
                            self.add_var_row(k, v)

    def save_and_close(self):
        with open(".env", "w") as f:
            f.write(f"BASE_HOST={self.host_input.text()}\n")
            for i in range(self.vars_layout.count()):
                widget = self.vars_layout.itemAt(i).widget()
                if widget:
                    inputs = widget.findChildren(QLineEdit)
                    if len(inputs) >= 2 and inputs[0].text():
                        f.write(f"{inputs[0].text()}={inputs[1].text()}\n")
        self.accept()