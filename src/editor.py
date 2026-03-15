from PySide6.QtWidgets import (QProgressBar, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QListWidget, QListWidgetItem, 
                             QPushButton, QFrame, QInputDialog)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta

class ScenarioEditor(QWidget):
    # Sinais para comunicação externa (Main Window / Inspector)
    request_start_inspection = Signal()
    request_confirm_capture = Signal()
    request_ai_assistant = Signal()  # Novo sinal para o Assistente de IA

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # --- ENTRADA DE DADOS ---
        layout.addWidget(QLabel("<b>Cenário BDD:</b>"))
        self.input_step = QLineEdit()
        self.input_step.setPlaceholderText("Digite o step e pressione Enter...")
        self.input_step.returnPressed.connect(self.add_step)
        layout.addWidget(self.input_step)

        # --- LISTA DE STEPS ---
        self.list_steps = QListWidget()
        self.list_steps.setSelectionMode(QListWidget.SingleSelection)
        self.list_steps.setStyleSheet("QListWidget::item { padding: 5px; border-bottom: 1px solid #eee; }")
        layout.addWidget(self.list_steps)

        # --- BARRA DE BOTÕES COMPACTA ---
        self.btn_container = QFrame()
        self.btn_container.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        bar_layout = QHBoxLayout(self.btn_container)
        bar_layout.setContentsMargins(5, 5, 5, 5)
        bar_layout.setSpacing(8)

        # 1. Mover para Cima
        self.btn_move_up = QPushButton(qta.icon('fa5s.arrow-up', color='#555'), "")
        self.btn_move_up.setToolTip("Um nível acima")
        self.btn_move_up.setFixedSize(32, 32)
        self.btn_move_up.clicked.connect(self.move_item_up)

        # 2. Mover para Baixo
        self.btn_move_down = QPushButton(qta.icon('fa5s.arrow-down', color='#555'), "")
        self.btn_move_down.setToolTip("Um nível abaixo")
        self.btn_move_down.setFixedSize(32, 32)
        self.btn_move_down.clicked.connect(self.move_item_down)

        # 3. Editar Texto
        self.btn_edit = QPushButton(qta.icon('fa5s.edit', color='#f39c12'), "")
        self.btn_edit.setToolTip("Editar texto do item selecionado")
        self.btn_edit.setFixedSize(32, 32)
        self.btn_edit.clicked.connect(self.edit_item)

        # 4. Excluir Item
        self.btn_delete = QPushButton(qta.icon('fa5s.trash-alt', color='#c0392b'), "")
        self.btn_delete.setToolTip("Excluir item selecionado da lista")
        self.btn_delete.setFixedSize(32, 32)
        self.btn_delete.clicked.connect(self.delete_item)

        # --- NOVO BOTÃO: ASSISTENTE DE IA ---
        self.btn_ai = QPushButton(qta.icon('fa5s.magic', color='#8e44ad'), "")
        self.btn_ai.setToolTip("Assistente de IA")
        self.btn_ai.setFixedSize(32, 32)
        self.btn_ai.clicked.connect(self.request_ai_assistant.emit)

        # --- BOTÕES DE INSPEÇÃO ---
        # 5. Iniciar Inspeção
        self.btn_start_inspect = QPushButton(qta.icon('fa5s.search', color='#2980b9'), "")
        self.btn_start_inspect.setToolTip("Iniciar inspeção")
        self.btn_start_inspect.setFixedSize(32, 32)
        self.btn_start_inspect.clicked.connect(self.request_start_inspection.emit)

        # 6. Capturar Elemento
        self.btn_capture = QPushButton(qta.icon('fa5s.bullseye', color='#27ae60'), "")
        self.btn_capture.setToolTip("Capturar elemento da inspeção")
        self.btn_capture.setFixedSize(32, 32)
        self.btn_capture.clicked.connect(self.request_confirm_capture.emit)

        # Montagem do Layout Horizontal
        bar_layout.addWidget(self.btn_move_up)
        bar_layout.addWidget(self.btn_move_down)
        bar_layout.addWidget(self.btn_edit)
        bar_layout.addWidget(self.btn_delete)
        
        # Botão de IA em destaque antes da inspeção
        bar_layout.addWidget(self.btn_ai)
        
        bar_layout.addStretch() # Empurra os controles de inspeção para a direita
        
        bar_layout.addWidget(self.btn_start_inspect)
        bar_layout.addWidget(self.btn_capture)

        layout.addWidget(self.btn_container)

        # --- BOTÃO DE EXPORTAÇÃO ---
        self.btn_export = QPushButton(qta.icon('fa5s.code', color='white'), " GERAR CÓDIGO")
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; 
                color: white; 
                font-weight: bold; 
                height: 35px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        layout.addWidget(self.btn_export)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Estilo 'Marquee' (fica a andar de um lado para o outro)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    # --- MÉTODOS DE LÓGICA E MOVIMENTAÇÃO ---

    def add_step(self):
        text = self.input_step.text().strip()
        if text:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, None) # Placeholder para o seletor HTML
            self.list_steps.addItem(item)
            self.input_step.clear()

    def edit_item(self):
        item = self.list_steps.currentItem()
        if item:
            # Remove temporariamente o check visual para não atrapalhar a edição
            current_text = item.text().replace(" ✔", "")
            new_text, ok = QInputDialog.getText(
                self, "Editar Step", "Altere o texto do step:", 
                QLineEdit.Normal, current_text
            )
            if ok and new_text:
                # Se o item já tinha seletor, mantemos o check visual
                suffix = " ✔" if item.data(Qt.UserRole) else ""
                item.setText(new_text + suffix)

    def delete_item(self):
        current_row = self.list_steps.currentRow()
        if current_row >= 0:
            self.list_steps.takeItem(current_row)

    def move_item_up(self):
        current_row = self.list_steps.currentRow()
        if current_row > 0:
            item = self.list_steps.takeItem(current_row)
            self.list_steps.insertItem(current_row - 1, item)
            self.list_steps.setCurrentRow(current_row - 1)

    def move_item_down(self):
        current_row = self.list_steps.currentRow()
        if current_row < self.list_steps.count() - 1 and current_row >= 0:
            item = self.list_steps.takeItem(current_row)
            self.list_steps.insertItem(current_row + 1, item)
            self.list_steps.setCurrentRow(current_row + 1)

    def mark_step_as_mapped(self, selector):
        """Método auxiliar para a Main Window marcar o item como concluído"""
        item = self.list_steps.currentItem()
        if item:
            item.setData(Qt.UserRole, selector)
            item.setBackground(Qt.green)
            if " ✔" not in item.text():
                item.setText(f"{item.text()} ✔")