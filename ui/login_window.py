from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QApplication)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QPixmap
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LoginWindow(QWidget):
    login_successful = Signal(dict)
    MAX_ATTEMPTS = 5  # Erhöht von 3 auf 5 Versuche
    LOCKOUT_TIME = 2  # Reduziert auf 2 Minuten
    
    def __init__(self, db_manager, on_login_success):
        super().__init__()
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        
        # Login-Versuche zurücksetzen
        self.failed_attempts = {}  # Format: {username: {'count': 0, 'locked_until': datetime}}
        
        self.load_stylesheet()
        self.setup_ui()
        
        # Timer für das Aktualisieren der Sperre
        self.lock_timer = QTimer()
        self.lock_timer.timeout.connect(self.update_lock_status)
        self.lock_timer.start(1000)  # Jede Sekunde aktualisieren
    
    def load_stylesheet(self):
        style_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())
    
    def setup_ui(self):
        # Hauptlayout für das gesamte Widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Zentrierender Container
        center_container = QFrame()
        center_container.setObjectName("centerContainer")
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # Login Container
        login_container = QFrame()
        login_container.setObjectName("loginContainer")
        login_container.setFixedWidth(500)
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(40, 40, 40, 20)
        login_layout.setSpacing(1)
        
        # Logo
        logo_label = QLabel()
        logo_label.setObjectName("logoLabel")
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_pixmap = logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(logo_label)
        
        # Title
        title = QLabel("We ❤️ Gaming")
        title.setFixedHeight(70)
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("heading", True)
        login_layout.addWidget(title)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(45)
        self.username_input.returnPressed.connect(self.handle_login)
        self.username_input.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.returnPressed.connect(self.handle_login)
        self.password_input.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(self.password_input)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setFixedHeight(40)
        self.login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(self.login_button)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(self.error_label)
        
        # Füge den Login-Container zum Center-Container hinzu
        center_layout.addStretch(1)
        center_layout.addWidget(login_container, 0, Qt.AlignCenter)
        center_layout.addStretch(1)
        
        # Füge den Center-Container zum Hauptlayout hinzu
        main_layout.addWidget(center_container)
    
    def update_lock_status(self):
        """Aktualisiert den Status der Sperrzeit und entsperrt Benutzer wenn die Zeit abgelaufen ist"""
        current_time = datetime.now()
        for username in list(self.failed_attempts.keys()):
            if (self.failed_attempts[username]['locked_until'] and 
                current_time >= self.failed_attempts[username]['locked_until']):
                self.failed_attempts[username] = {'count': 0, 'locked_until': None}
                if self.username_input.text() == username:
                    self.error_label.clear()
                    self.enable_login_fields()
    
    def enable_login_fields(self):
        """Aktiviert die Login-Felder"""
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_button.setEnabled(True)
    
    def disable_login_fields(self):
        """Deaktiviert die Login-Felder"""
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.login_button.setEnabled(False)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.error_label.setText("Bitte geben Sie Benutzername und Passwort ein")
            return
            
        # Prüfen ob der Benutzer gesperrt ist
        if username in self.failed_attempts:
            user_attempts = self.failed_attempts[username]
            if user_attempts['locked_until']:
                remaining_time = user_attempts['locked_until'] - datetime.now()
                if remaining_time.total_seconds() > 0:
                    minutes = int(remaining_time.total_seconds() // 60)
                    seconds = int(remaining_time.total_seconds() % 60)
                    self.error_label.setText(
                        f"Account temporär gesperrt.\n Bitte warten Sie noch {minutes}:{seconds:02d} Minuten"
                    )
                    self.disable_login_fields()
                    return
        
        # Login-Versuch
        user_data = self.db_manager.authenticate_user(username, password)
        
        if user_data:
            # Erfolgreicher Login - Versuche zurücksetzen
            if username in self.failed_attempts:
                self.failed_attempts[username] = {'count': 0, 'locked_until': None}
            self.error_label.clear()
            logger.info(f"Erfolgreicher Login für Benutzer: {username}")
            self.on_login_success(user_data)
        else:
            # Fehlgeschlagener Login
            if username not in self.failed_attempts:
                self.failed_attempts[username] = {'count': 0, 'locked_until': None}
            
            self.failed_attempts[username]['count'] += 1
            remaining_attempts = self.MAX_ATTEMPTS - self.failed_attempts[username]['count']
            
            if remaining_attempts <= 0:
                # Account sperren
                self.failed_attempts[username]['locked_until'] = datetime.now() + timedelta(minutes=self.LOCKOUT_TIME)
                self.error_label.setText(
                    f"Zu viele fehlgeschlagene Versuche.\n Account für {self.LOCKOUT_TIME} Minuten gesperrt."
                )
                self.disable_login_fields()
                logger.warning(f"Account gesperrt für Benutzer: {username} wegen zu vieler Fehlversuche")
            else:
                # Warnung anzeigen
                self.error_label.setText(
                    f"Ungültiger Benutzername oder Passwort.\n Noch {remaining_attempts} Versuch(e) übrig"
                )
                logger.warning(f"Fehlgeschlagener Login-Versuch für Benutzer: {username}. \n "
                             f"Noch {remaining_attempts} Versuch(e) übrig")
