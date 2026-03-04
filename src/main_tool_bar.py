from PySide6.QtWidgets import QToolBar, QStyle
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt

class MainToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Barra de Ferramentas Principal", parent)
        
        # Configurações estéticas
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly) # Mostra apenas ícones na barra
        
        # Obter ícones do sistema (Standard Icons do Qt)
        style = self.style()
        
        # --- BOTAO: NOVO CENÁRIO ---
        self.action_novo = QAction(
            style.standardIcon(QStyle.SP_FileIcon), 
            "Novo Cenário", 
            self
        )
        self.action_novo.setToolTip("Criar um novo cenário BDD (Ctrl+N)")
        
        # --- BOTAO: ABRIR CENÁRIO ---
        self.action_abrir = QAction(
            style.standardIcon(QStyle.SP_DialogOpenButton), 
            "Abrir Cenário", 
            self
        )
        self.action_abrir.setToolTip("Abrir um cenário existente (Ctrl+O)")
        
        # --- BOTAO: LISTAR CENÁRIOS ---
        self.action_listar = QAction(
            style.standardIcon(QStyle.SP_FileDialogContentsView), 
            "Listar Cenários", 
            self
        )
        self.action_listar.setToolTip("Visualizar todos os cenários do projeto")
        
        # --- BOTAO: CONFIGURAÇÕES ---
        self.action_config = QAction(
            style.standardIcon(QStyle.SP_ComputerIcon), 
            "Configurações", 
            self
        )
        self.action_config.setToolTip("Configurar ambiente, caminhos e drivers")

        # Adicionar ações à barra
        self.addAction(self.action_novo)
        self.addAction(self.action_abrir)
        self.addSeparator() # Linha vertical separadora
        self.addAction(self.action_listar)
        self.addSeparator()
        self.addAction(self.action_config)