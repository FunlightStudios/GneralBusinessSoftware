from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame, QScrollArea,
                             QFileDialog, QProgressBar, QGridLayout,
                             QSizePolicy, QSpacerItem, QMenu, QMessageBox,
                             QLineEdit, QDialog, QInputDialog)
from PySide6.QtCore import Qt, Signal, QThread, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QPen
import os
import shutil
from datetime import datetime
from database.db_manager import DatabaseManager

class StorageWidget(QWidget):
    def __init__(self, used_gb, total_gb):
        super().__init__()
        self.used_gb = used_gb
        self.total_gb = total_gb
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Storage header
        header = QLabel("Storage")
        header.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # Progress bar
        progress = QProgressBar()
        progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #2c2c2c;
                height: 8px;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        percentage = (self.used_gb / self.total_gb) * 100
        progress.setValue(int(percentage))
        layout.addWidget(progress)
        
        # Storage info
        info = QLabel(f"{self.used_gb:.1f} / {self.total_gb} GB Used")
        info.setStyleSheet("color: #999999; font-size: 12px;")
        layout.addWidget(info)
        
        # Free space
        free = QLabel(f"{self.total_gb - self.used_gb:.1f} GB Free")
        free.setStyleSheet("color: #999999; font-size: 12px;")
        layout.addWidget(free)
        
        # Buy storage button
        buy_btn = QPushButton("Buy Storage")
        buy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #3498db;
                color: #3498db;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3498db22;
            }
        """)
        layout.addWidget(buy_btn)

class FileCard(QFrame):
    def __init__(self, name, type_icon, parent=None):
        super().__init__(parent)
        self.name = name
        self.type_icon = type_icon
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #363636;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(self.type_icon.pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Name
        name_label = QLabel(self.name)
        name_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

class FileUploadThread(QThread):
    upload_progress = Signal(str, int)
    upload_complete = Signal(str)
    upload_error = Signal(str, str)

    def __init__(self, file_paths, db_manager, user_id):
        super().__init__()
        self.file_paths = file_paths
        self.db_manager = db_manager
        self.user_id = user_id

    def run(self):
        for file_path in self.file_paths:
            try:
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                # Get destination path
                upload_dir = self.db_manager.get_upload_path()
                dest_path = os.path.join(upload_dir, filename)
                
                # Copy file with progress updates
                with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    copied = 0
                    while True:
                        buf = src.read(8192)
                        if not buf:
                            break
                        dst.write(buf)
                        copied += len(buf)
                        progress = int((copied / file_size) * 100)
                        self.upload_progress.emit(filename, progress)
                
                # Add file to database
                file_info = {
                    'name': filename,
                    'path': dest_path,
                    'size': file_size,
                    'type': os.path.splitext(filename)[1],
                    'uploaded_at': datetime.utcnow(),
                    'user_id': self.user_id,
                    'favorites': [],
                    'in_trash': False
                }
                self.db_manager.add_file(file_info)
                self.upload_complete.emit(filename)
                
            except Exception as e:
                self.upload_error.emit(filename, str(e))

class SidebarButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon_text
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                color: #cccccc;
                background: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2c2c2c;
                color: white;
            }
        """)

class FilesWidget(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.upload_threads = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1c1c1c;
                color: #ffffff;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1c1c1c;
                border-right: 1px solid #2c2c2c;
            }
        """)
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
        # Create New button
        create_new = QPushButton("+ Create New")
        create_new.setStyleSheet("""
            QPushButton {
                background-color: #2c2c2c;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #363636;
            }
        """)
        sidebar_layout.addWidget(create_new)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", "🏠"),
            ("My Drive", "📁"),
            ("Files", "📄"),
            ("Recent", "🕒"),
            ("Favourite", "⭐"),
            ("Trash", "🗑️"),
        ]
        
        for text, icon in nav_buttons:
            btn = SidebarButton(f"{icon} {text}")
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Storage section
        storage_label = QLabel("Storage")
        storage_label.setStyleSheet("color: #999999; font-size: 12px;")
        sidebar_layout.addWidget(storage_label)
        
        # Storage progress
        progress = QProgressBar()
        progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #2c2c2c;
                height: 8px;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        progress.setValue(85)  # 17.1/20 GB ≈ 85%
        sidebar_layout.addWidget(progress)
        
        storage_info = QLabel("17.1 / 20 GB Used")
        storage_info.setStyleSheet("color: #999999; font-size: 12px;")
        sidebar_layout.addWidget(storage_info)
        
        storage_free = QLabel("2.9 GB Free")
        storage_free.setStyleSheet("color: #999999; font-size: 12px;")
        sidebar_layout.addWidget(storage_free)
        
        buy_storage = QPushButton("Buy Storage")
        buy_storage.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #3498db;
                color: #3498db;
                padding: 5px 15px;
                border-radius: 4px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #3498db22;
            }
        """)
        sidebar_layout.addWidget(buy_storage)
        
        main_layout.addWidget(sidebar)
        
        # Main content area
        content = QFrame()
        content.setStyleSheet("""
            QFrame {
                background-color: #1c1c1c;
            }
        """)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Top bar with search
        top_bar = QHBoxLayout()
        
        # My Drive dropdown
        drive_btn = QPushButton("My Drive ▼")
        drive_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                font-size: 18px;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        top_bar.addWidget(drive_btn)
        
        # Search bar
        search = QLineEdit()
        search.setPlaceholderText("Type here to search...")
        search.setStyleSheet("""
            QLineEdit {
                background-color: #2c2c2c;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                color: white;
            }
        """)
        top_bar.addWidget(search)
        
        content_layout.addLayout(top_bar)
        
        # Documents section
        docs = QFrame()
        docs.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        docs_layout = QVBoxLayout(docs)
        
        docs_header = QHBoxLayout()
        docs_title = QLabel("Documents")
        docs_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        docs_header.addWidget(docs_title)
        
        view_all = QPushButton("View All")
        view_all.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        docs_header.addWidget(view_all)
        docs_layout.addLayout(docs_header)
        
        docs_grid = QGridLayout()
        docs_grid.setSpacing(15)
        
        # Add document items
        doc_items = [
            ("Terms.pdf", "pdf"),
            ("New-one.docx", "doc"),
            ("Woo-box.xlsx", "xls"),
            ("IOS-content.pptx", "ppt")
        ]
        
        for i, (name, type_) in enumerate(doc_items):
            card = FileCard(name, self.get_file_icon(type_))
            docs_grid.addWidget(card, i // 4, i % 4)
        
        docs_layout.addLayout(docs_grid)
        content_layout.addWidget(docs)
        
        # Upload button at the bottom
        upload_btn = QPushButton("Upload Files")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        upload_btn.clicked.connect(self.upload_files)
        content_layout.addWidget(upload_btn)
        
        content_layout.addStretch()
        main_layout.addWidget(content)
    
    def get_file_icon(self, file_type):
        """Get the appropriate icon for a file type."""
        color_map = {
            'pdf': '#FF5555',  # Red
            'doc': '#5B95FF',  # Blue
            'xls': '#4CAF50',  # Green
            'ppt': '#FF9800',  # Orange
            'folder-blue': '#5B95FF',
            'folder-pink': '#FF69B4'
        }
        
        # Create a colored rectangle with file type text
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rectangle background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color_map.get(file_type, '#999999')))
        painter.drawRoundedRect(0, 0, 48, 48, 8, 8)
        
        # Draw file type text
        painter.setPen(QColor('#FFFFFF'))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        text = file_type.upper()
        if 'folder' in file_type:
            text = ''  # For folders, we don't show text
            
        text_rect = painter.boundingRect(0, 0, 48, 48, Qt.AlignCenter, text)
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        painter.end()
        return QIcon(pixmap)
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def upload_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            
            for filename in filenames:
                try:
                    # Get file info
                    file_info = {
                        'name': os.path.basename(filename),
                        'size': os.path.getsize(filename),
                        'type': os.path.splitext(filename)[1].lower(),
                        'modified': os.path.getmtime(filename),
                        'user_id': self.user_data['id']
                    }
                    
                    # Copy file to uploads directory
                    target_path = os.path.join(self.db_manager.get_upload_path(), file_info['name'])
                    shutil.copy2(filename, target_path)
                    file_info['path'] = target_path
                    
                    # Save to database
                    self.db_manager.add_file(file_info)
                    
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error uploading file {os.path.basename(filename)}: {str(e)}")

class DatabaseManager:
    def __init__(self):
        pass

    def get_upload_path(self):
        return "uploads"

    def add_file(self, file_info):
        pass

class FileManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.current_user_id = "1"  # Debug user ID
        self.current_view = "my_drive"
        self.setup_ui()
        self.load_files()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1c1c1c;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2c2c2c;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
            QLineEdit {
                background-color: #2c2c2c;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
        """)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #2c2c2c;")
        sidebar_layout = QVBoxLayout(sidebar)

        # Create New Button
        create_new_btn = QPushButton("+ Create New")
        create_new_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        create_new_btn.clicked.connect(self.show_create_new_dialog)
        sidebar_layout.addWidget(create_new_btn)

        # Navigation buttons
        nav_buttons = [
            ("My Drive", lambda: self.change_view("my_drive")),
            ("Favorites", lambda: self.change_view("favorites")),
            ("Recent", lambda: self.change_view("recent")),
            ("Trash", lambda: self.change_view("trash"))
        ]

        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    margin: 2px 0;
                }
            """)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Storage section
        storage_widget = QWidget()
        storage_layout = QVBoxLayout(storage_widget)
        
        storage_label = QLabel("Storage")
        storage_progress = QProgressBar()
        storage_progress.setValue(65)  # Example value
        storage_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #3c3c3c;
                height: 8px;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        
        buy_storage_btn = QPushButton("Buy Storage")
        buy_storage_btn.clicked.connect(self.show_buy_storage_dialog)
        
        storage_layout.addWidget(storage_label)
        storage_layout.addWidget(storage_progress)
        storage_layout.addWidget(buy_storage_btn)
        
        sidebar_layout.addWidget(storage_widget)
        main_layout.addWidget(sidebar)

        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search files...")
        search_bar.textChanged.connect(self.search_files)
        content_layout.addWidget(search_bar)

        # Document grid
        self.document_grid = QGridLayout()
        self.document_grid.setSpacing(20)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.document_grid)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        content_layout.addWidget(scroll_area)
        main_layout.addWidget(content_widget)

    def show_create_new_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New")
        layout = QVBoxLayout(dialog)

        options = ["Upload File", "Create Folder"]
        for option in options:
            btn = QPushButton(option)
            btn.clicked.connect(lambda checked, o=option: self.handle_create_new(o, dialog))
            layout.addWidget(btn)

        dialog.exec_()

    def handle_create_new(self, option, dialog):
        if option == "Upload File":
            self.upload_file()
        elif option == "Create Folder":
            self.create_folder()
        dialog.close()

    def create_folder(self):
        name, ok = QInputDialog.getText(self, "Create Folder", "Folder name:")
        if ok and name:
            # Add folder creation logic here
            pass

    def show_buy_storage_dialog(self):
        QMessageBox.information(self, "Buy Storage", "Storage upgrade options will be available soon!")

    def change_view(self, view):
        self.current_view = view
        self.load_files()

    def load_files(self):
        # Clear existing items
        for i in reversed(range(self.document_grid.count())): 
            self.document_grid.itemAt(i).widget().setParent(None)

        # Get files based on current view
        if self.current_view == "favorites":
            files = [f for f in self.db.get_files(self.current_user_id) 
                    if self.current_user_id in f.get('favorites', [])]
        elif self.current_view == "recent":
            files = self.db.get_recent_files(self.current_user_id)
        elif self.current_view == "trash":
            files = self.db.get_trash(self.current_user_id)
        else:  # my_drive
            files = [f for f in self.db.get_files(self.current_user_id) 
                    if not f.get('in_trash', False)]

        # Display files
        row = col = 0
        max_cols = 4
        for file in files:
            card = self.create_file_card(file)
            self.document_grid.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_file_card(self, file):
        card = QWidget()
        card.setFixedSize(200, 200)
        card.setStyleSheet("""
            QWidget {
                background-color: #2c2c2c;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #3c3c3c;
            }
        """)

        layout = QVBoxLayout(card)
        
        # File icon
        icon_label = QLabel()
        icon_label.setPixmap(self.get_file_icon(file.get('type', '')))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # File name
        name_label = QLabel(file.get('name', 'Unnamed'))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        # Context menu
        card.setContextMenuPolicy(Qt.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos, f=file: self.show_context_menu(pos, f))

        return card

    def show_context_menu(self, pos, file):
        menu = QMenu(self)
        
        if self.current_view == "trash":
            restore_action = menu.addAction("Restore")
            restore_action.triggered.connect(lambda: self.restore_file(file))
            delete_action = menu.addAction("Delete Permanently")
            delete_action.triggered.connect(lambda: self.delete_permanently(file))
        else:
            if self.current_user_id in file.get('favorites', []):
                fav_action = menu.addAction("Remove from Favorites")
                fav_action.triggered.connect(lambda: self.remove_from_favorites(file))
            else:
                fav_action = menu.addAction("Add to Favorites")
                fav_action.triggered.connect(lambda: self.add_to_favorites(file))
            
            trash_action = menu.addAction("Move to Trash")
            trash_action.triggered.connect(lambda: self.move_to_trash(file))

        menu.exec_(self.sender().mapToGlobal(pos))

    def get_file_icon(self, file_type):
        # Return appropriate QPixmap based on file type
        return QPixmap("path/to/default/icon.png")  # Placeholder

    def search_files(self, query):
        if not query:
            self.load_files()
            return

        files = self.db.search_files(self.current_user_id, query)
        
        # Clear and reload grid with search results
        for i in reversed(range(self.document_grid.count())): 
            self.document_grid.itemAt(i).widget().setParent(None)

        row = col = 0
        max_cols = 4
        for file in files:
            card = self.create_file_card(file)
            self.document_grid.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def add_to_favorites(self, file):
        if self.db.add_to_favorites(file['_id'], self.current_user_id):
            self.load_files()

    def remove_from_favorites(self, file):
        if self.db.remove_from_favorites(file['_id'], self.current_user_id):
            self.load_files()

    def move_to_trash(self, file):
        if self.db.move_to_trash(file['_id'], self.current_user_id):
            self.load_files()

    def restore_file(self, file):
        if self.db.restore_from_trash(file['_id'], self.current_user_id):
            self.load_files()

    def delete_permanently(self, file):
        reply = QMessageBox.question(
            self, 
            'Delete Permanently',
            'Are you sure you want to permanently delete this file? This action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Add permanent deletion logic here
            self.load_files()
