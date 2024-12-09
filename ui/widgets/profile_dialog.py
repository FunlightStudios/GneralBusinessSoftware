from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QWidget)
from PySide6.QtCore import Qt
from .user_management import UserManagementDialog

class ProfileDialog(QDialog):
    def __init__(self, user_data, db_manager, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Profil")
        self.setObjectName("profile-dialog")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Profile header
        header = QWidget()
        header.setObjectName("profile-header")
        header_layout = QHBoxLayout(header)
        
        name_label = QLabel(self.user_data['username'])
        name_label.setObjectName("profile-name")
        role_label = QLabel(f"({self.user_data['role']})")
        role_label.setObjectName("profile-role")
        
        header_layout.addWidget(name_label)
        header_layout.addWidget(role_label)
        header_layout.addStretch()
        
        # Admin button for user management
        if self.user_data['role'] == 'admin':
            admin_button = QPushButton("Benutzer verwalten")
            admin_button.setObjectName("admin-button")
            admin_button.clicked.connect(self.show_user_management)
            header_layout.addWidget(admin_button)
        
        # User info section
        info_widget = QWidget()
        info_widget.setObjectName("profile-info")
        info_layout = QVBoxLayout(info_widget)
        
        # Add user information fields
        fields = [
            ("Email", "email"),
            ("Position", "role"),
            ("Abteilung", "department"),
            ("Standort", "location")
        ]
        
        for label_text, key in fields:
            field_container = QWidget()
            field_layout = QVBoxLayout(field_container)
            field_layout.setSpacing(5)
            
            label = QLabel(label_text)
            label.setObjectName("field-label")
            value = QLineEdit(self.user_data.get(key, ""))
            value.setReadOnly(True)
            value.setObjectName("field-value")
            
            field_layout.addWidget(label)
            field_layout.addWidget(value)
            info_layout.addWidget(field_container)
        
        # Add buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        edit_button = QPushButton("Bearbeiten")
        edit_button.setObjectName("edit-button")
        close_button = QPushButton("Schließen")
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(close_button)
        
        # Add all sections to main layout
        layout.addWidget(header)
        layout.addWidget(info_widget)
        layout.addStretch()
        layout.addWidget(button_container)
        
    def show_user_management(self):
        dialog = UserManagementDialog(self, self.db_manager)
        dialog.exec_()
