from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QComboBox,
                             QHeaderView, QFrame, QToolButton, QMenu)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QColor

class UserManagementDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        self.setWindowTitle("Benutzerverwaltung")
        self.setObjectName("user-management")
        
        # Hauptlayout ohne Margins für maximale Ausnutzung
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header-Bereich
        header = QWidget()
        header.setObjectName("dialog-header")
        header.setFixedHeight(80)  # Feste Höhe für Header
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Titel
        title = QLabel("Benutzer verwalten")
        title.setObjectName("section-title")
        
        # Such- und Filter-Bereich
        search_container = QFrame()
        search_container.setObjectName("search-container")
        search_container.setFixedWidth(400)  # Feste Breite für Suchbereich
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 15, 0)
        
        # Suchfeld
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Benutzer suchen...")
        self.search_input.textChanged.connect(self.filter_users)
        
        # Filter-Button
        self.filter_btn = QToolButton()
        self.filter_btn.setText("Filter")
        self.filter_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.filter_btn.setPopupMode(QToolButton.InstantPopup)
        
        filter_menu = QMenu(self.filter_btn)
        self.role_filter = filter_menu.addMenu("Rolle")
        self.role_actions = {
            "Alle": self.role_filter.addAction("Alle"),
            "Admin": self.role_filter.addAction("Admin"),
            "User": self.role_filter.addAction("User")
        }
        for action in self.role_actions.values():
            action.setCheckable(True)
            action.triggered.connect(self.filter_users)
        self.role_actions["Alle"].setChecked(True)
        
        self.filter_btn.setMenu(filter_menu)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.filter_btn)
        
        # Neuer Benutzer Button
        add_user_btn = QPushButton("Neuer Benutzer")
        add_user_btn.setObjectName("add-button")
        add_user_btn.setFixedWidth(150)  # Feste Breite für Button
        add_user_btn.clicked.connect(self.show_add_user_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(search_container)
        header_layout.addWidget(add_user_btn)
        
        # Hauptbereich mit Tabelle
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(0)
        
        # Tabelle
        self.users_table = QTableWidget()
        self.users_table.setObjectName("users-table")
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            "Benutzername", "E-Mail", "Rolle", "Position", 
            "Abteilung", "Standort", "Aktionen"
        ])
        
        # Tabellenspalten konfigurieren
        header = self.users_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        
        # Spaltenbreiten festlegen
        self.users_table.setColumnWidth(0, 150)  # Benutzername
        self.users_table.setColumnWidth(2, 100)  # Rolle
        self.users_table.setColumnWidth(3, 150)  # Position
        self.users_table.setColumnWidth(4, 150)  # Abteilung
        self.users_table.setColumnWidth(5, 150)  # Standort
        self.users_table.setColumnWidth(6, 200)  # Aktionen
        
        # Tabelleneigenschaften
        self.users_table.setShowGrid(True)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setSortingEnabled(True)
        
        content_layout.addWidget(self.users_table)
        
        # Status-Leiste
        status_bar = QWidget()
        status_bar.setObjectName("status-bar")
        status_bar.setFixedHeight(30)  # Feste Höhe für Status-Leiste
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(20, 0, 20, 0)
        
        self.status_label = QLabel()
        self.status_label.setObjectName("status-label")
        status_layout.addWidget(self.status_label)
        
        # Hauptlayout zusammenbauen
        main_layout.addWidget(header)
        main_layout.addWidget(content_widget)
        main_layout.addWidget(status_bar)
        
        # Fenster maximieren
        self.showMaximized()

    def filter_users(self):
        search_text = self.search_input.text().lower()
        selected_role = next(name for name, action in self.role_actions.items() 
                           if action.isChecked())
        
        visible_rows = 0
        for row in range(self.users_table.rowCount()):
            show_row = True
            
            # Textsuche
            if search_text:
                show_row = False
                for col in range(self.users_table.columnCount() - 1):
                    item = self.users_table.item(row, col)
                    if item and search_text in item.text().lower():
                        show_row = True
                        break
            
            # Rollenfilter
            if show_row and selected_role != "Alle":
                role_item = self.users_table.item(row, 2)
                if role_item and role_item.text() != selected_role:
                    show_row = False
            
            self.users_table.setRowHidden(row, not show_row)
            if show_row:
                visible_rows += 1
        
        # Status-Update
        total_rows = self.users_table.rowCount()
        self.status_label.setText(
            f"{visible_rows} von {total_rows} Benutzern angezeigt"
        )
    
    def add_user_to_table(self, row, user):
        # Benutzerdaten hinzufügen
        columns = ['username', 'email', 'role', 'position', 'department', 'location']
        for col, field in enumerate(columns):
            item = QTableWidgetItem(user.get(field, ''))
            item.setData(Qt.UserRole, user)
            
            # Text-Ausrichtung
            if field in ['username', 'email']:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            
            self.users_table.setItem(row, col, item)
            
            # Spezielle Formatierung für Rollen
            if field == 'role':
                role_color = '#E74C3C' if user.get(field) == 'admin' else '#2ECC71'
                item.setForeground(QColor(role_color))
                
        # Aktionsbuttons mit Icons
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        actions_layout.setSpacing(5)
        
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(":/icons/edit.png"))
        edit_btn.setText("Bearbeiten")
        edit_btn.setObjectName("edit-button")
        edit_btn.clicked.connect(lambda: self.edit_user(user))
        
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(":/icons/delete.png"))
        delete_btn.setText("Löschen")
        delete_btn.setObjectName("delete-button")
        delete_btn.clicked.connect(lambda: self.delete_user(user))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addStretch()
        
        self.users_table.setCellWidget(row, 6, actions_widget)

    def load_users(self):
        users = self.db_manager.get_all_users()
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            self.add_user_to_table(row, user)
    
    def show_add_user_dialog(self):
        dialog = UserDialog(self.db_manager, parent=self)
        if dialog.exec_():
            self.load_users()
    
    def edit_user(self, user):
        dialog = UserDialog(self.db_manager, user=user, parent=self)
        if dialog.exec_():
            self.load_users()
    
    def delete_user(self, user):
        reply = QMessageBox.question(
            self,
            "Benutzer löschen",
            f"Möchten Sie den Benutzer {user['username']} wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db_manager.delete_user(user['username'])
            self.load_users()


class UserDialog(QDialog):
    def __init__(self, db_manager, user=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = user
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Benutzer " + ("bearbeiten" if self.user else "hinzufügen"))
        self.setObjectName("user-dialog")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Formularfelder erstellen
        self.fields = {}
        self.error_labels = {}  # Für Validierungsfehler
        
        field_definitions = [
            ("username", "Benutzername*", QLineEdit, {"required": True, "pattern": r"^[a-zA-Z0-9_]{3,20}$"}),
            ("email", "E-Mail*", QLineEdit, {"required": True, "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}),
            ("role", "Rolle*", QComboBox, {"required": True, "items": ["user", "admin"]}),
            ("position", "Position", QLineEdit),
            ("department", "Abteilung", QLineEdit),
            ("location", "Standort", QLineEdit),
            ("password", "Passwort" + ("" if self.user else "*"), QLineEdit, 
             {"required": not bool(self.user), "password": True, "pattern": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"})
        ]
        
        for field_id, label_text, widget_class, *options in field_definitions:
            container = QWidget()
            container.setObjectName("field-container")
            container_layout = QVBoxLayout(container)
            container_layout.setSpacing(5)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            # Label
            label = QLabel(label_text)
            label.setObjectName("field-label")
            
            # Widget
            if widget_class == QComboBox:
                widget = QComboBox()
                widget.addItems(options[0].get("items", []))
            else:
                widget = widget_class()
                if options and options[0].get("password"):
                    widget.setEchoMode(QLineEdit.Password)
                    
                # Platzhaltertext
                placeholders = {
                    "username": "z.B. max.mustermann",
                    "email": "name@firma.de",
                    "position": "z.B. Entwickler",
                    "department": "z.B. IT",
                    "location": "z.B. Berlin",
                    "password": "Mind. 8 Zeichen, Buchstaben und Zahlen"
                }
                if field_id in placeholders:
                    widget.setPlaceholderText(placeholders[field_id])
            
            widget.setObjectName("field-input")
            
            # Existierende Werte setzen
            if self.user and field_id in self.user and field_id != "password":
                if widget_class == QComboBox:
                    widget.setCurrentText(self.user[field_id])
                else:
                    widget.setText(self.user[field_id])
            
            # Fehlerlabel
            error_label = QLabel()
            error_label.setObjectName("error-label")
            error_label.setStyleSheet("color: #E74C3C; font-size: 11px;")
            error_label.hide()
            
            self.fields[field_id] = widget
            self.error_labels[field_id] = error_label
            
            container_layout.addWidget(label)
            container_layout.addWidget(widget)
            container_layout.addWidget(error_label)
            
            layout.addWidget(container)
        
        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        save_button = QPushButton("Speichern")
        save_button.setObjectName("save-button")
        save_button.clicked.connect(self.save_user)
        
        cancel_button = QPushButton("Abbrechen")
        cancel_button.setObjectName("cancel-button")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addStretch()
        layout.addWidget(button_container)
    
    def validate_field(self, field_id, value, options):
        if not options:
            return True
            
        if options.get("required") and not value:
            self.error_labels[field_id].setText("Dieses Feld ist erforderlich")
            self.error_labels[field_id].show()
            return False
            
        pattern = options.get("pattern")
        if pattern and value:
            import re
            if not re.match(pattern, value):
                error_messages = {
                    "username": "Benutzername muss 3-20 Zeichen lang sein und darf nur Buchstaben, Zahlen und Unterstriche enthalten",
                    "email": "Bitte geben Sie eine gültige E-Mail-Adresse ein",
                    "password": "Passwort muss mindestens 8 Zeichen lang sein und Buchstaben sowie Zahlen enthalten"
                }
                self.error_labels[field_id].setText(error_messages.get(field_id, "Ungültiges Format"))
                self.error_labels[field_id].show()
                return False
                
        self.error_labels[field_id].hide()
        return True
    
    def save_user(self):
        # Alle Fehler zurücksetzen
        for error_label in self.error_labels.values():
            error_label.hide()
        
        # Daten sammeln und validieren
        user_data = {}
        is_valid = True
        
        field_definitions = [
            ("username", {"required": True, "pattern": r"^[a-zA-Z0-9_]{3,20}$"}),
            ("email", {"required": True, "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}),
            ("role", {"required": True}),
            ("position", {}),
            ("department", {}),
            ("location", {}),
            ("password", {"required": not bool(self.user), "pattern": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"})
        ]
        
        for field_id, options in field_definitions:
            widget = self.fields[field_id]
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            else:
                value = widget.text().strip()
                
            if not self.validate_field(field_id, value, options):
                is_valid = False
            else:
                user_data[field_id] = value
        
        if not is_valid:
            return
        
        # Benutzer speichern oder aktualisieren
        try:
            if self.user:
                success = self.db_manager.update_user(self.user['username'], user_data)
            else:
                success = self.db_manager.create_user(user_data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Fehler",
                    "Beim Speichern ist ein Fehler aufgetreten."
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}"
            )
