from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QTextEdit, QScrollArea,
                               QFrame, QLineEdit, QSplitter, QListWidget,
                               QListWidgetItem, QSizePolicy, QMenu, QToolButton,
                               QTabWidget, QGridLayout, QDialog, QAbstractItemView)
from PySide6.QtCore import Qt, QTimer, QDateTime, QEvent, QSize, QPoint
from PySide6.QtGui import QColor, QTextCursor, QIcon, QAction
import emoji
from PySide6.QtWidgets import QApplication
import datetime
from datetime import datetime

class EmojiPickerWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(350, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #2c2c2c;
                color: #cccccc;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #363636;
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QPushButton {
                background: transparent;
                border: none;
                padding: 5px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #363636;
                border-radius: 4px;
            }
            QScrollArea {
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Search bar (optional for future implementation)
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search emoji...")
        search_input.setStyleSheet("""
            QLineEdit {
                background-color: #363636;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(search_input)
        
        # Tab widget for categories
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Emoji categories
        self.emoji_categories = {
            "😊 Smileys": [
                "😀", "😃", "😄", "😁", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍",
                "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎",
                "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩"
            ],
            "❤️ Herzen": [
                "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❤️‍🔥", "❤️‍🩹",
                "💖", "💗", "💓", "💞", "💕", "💟", "❣️", "💝", "💘", "💌"
            ],
            "👍 Gesten": [
                "👍", "👎", "👌", "🤌", "🤏", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "👇",
                "☝️", "👋", "🤚", "🖐️", "✋", "🖖", "👏", "🙌", "👐", "🤲", "🤝", "🙏"
            ],
            "🎮 Gaming": [
                "🎮", "🕹️", "🎲", "🎯", "🎳", "🎪", "🎨", "🎭", "🎪", "🎟️", "🎫", "🎖️", "🏆", "🏅",
                "🥇", "🥈", "🥉", "⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🎱"
            ],
            "💻 Technik": [
                "💻", "🖥️", "💽", "💾", "💿", "📀", "🎥", "📹", "📼", "📱", "☎️", "📞", "📟", "📠",
                "📺", "📻", "🎙️", "🎚️", "🎛️", "🧭", "⌚", "⏰", "⏱️", "⏲️", "🕰️", "📡"
            ],
            "🚀 Objekte": [
                "🚀", "✨", "💡", "🔋", "🔌", "📎", "📏", "📐", "✂️", "🗑️", "🔒", "🔓", "🔑", "🔨",
                "🪛", "🔧", "🪜", "🧰", "🎁", "📦", "📫", "💰", "💳", "💎", "⚡", "🔥"
            ]
        }
        
        # Create tabs for each category
        for category, emojis in self.emoji_categories.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            content = QWidget()
            grid = QGridLayout(content)
            grid.setSpacing(2)
            
            # Add emojis to grid
            for i, emoji_char in enumerate(emojis):
                button = QPushButton(emoji_char)
                button.setFixedSize(QSize(40, 40))
                button.clicked.connect(lambda checked, e=emoji_char: self.on_emoji_selected(e))
                grid.addWidget(button, i // 6, i % 6)  # 6 emojis per row
            
            scroll.setWidget(content)
            tab_layout.addWidget(scroll)
            tab_widget.addTab(tab, category.split()[1])  # Use category name without emoji
            
    def on_emoji_selected(self, emoji_char):
        if hasattr(self.parent, 'insert_emoji'):
            self.parent.insert_emoji(emoji_char)
            self.hide()

class QuickReactionMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent_bubble = parent
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #233138;
                border-radius: 12px;
                border: 1px solid #36474f;
            }
            QPushButton {
                background: transparent;
                border: none;
                padding: 8px;
                font-size: 22px;
                min-width: 45px;
                min-height: 45px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #36474f;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        reactions = ["👍", "❤️", "😂", "😮", "😢"]
        for reaction in reactions:
            btn = QPushButton(reaction)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, r=reaction: self.select_reaction(r))
            layout.addWidget(btn)
        
        # Add more emoji button
        more_btn = QPushButton("+")
        more_btn.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                font-weight: bold;
                color: #aebac1;
            }
        """)
        more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        more_btn.clicked.connect(self.show_full_picker)
        layout.addWidget(more_btn)
        
        self.adjustSize()
    
    def select_reaction(self, reaction):
        if self.parent_bubble:
            self.parent_bubble.add_reaction(reaction)
            self.close()
    
    def show_full_picker(self):
        if self.parent_bubble:
            self.parent_bubble.show_full_emoji_picker()
            self.close()
    
    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)

class MessageBubble(QFrame):
    def __init__(self, message_data, chat_widget, parent=None):
        super().__init__(parent)
        self.message_data = message_data
        self.chat_widget = chat_widget
        self.reaction_menu = None
        self.reaction_button = None
        self.setup_ui()

    def setup_ui(self):
        is_own_message = self.message_data['user_id'] == self.chat_widget.user_data['id']
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 4, 16, 4)
        main_layout.setSpacing(0)
        
        if is_own_message:
            main_layout.addStretch()
        
        # Message container
        container = QFrame()
        container.setObjectName("messageContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)
        
        # Message bubble
        bubble_frame = QFrame()
        bubble_frame.setObjectName("messageBubble")
        bubble_frame.setStyleSheet(f"""
            #messageBubble {{
                background-color: {('#0078d4' if is_own_message else '#2d2d2d')};
                border-radius: 12px;
                border: 1px solid {('#0078d4' if is_own_message else '#3d3d3d')};
            }}
            QLabel {{
                color: {'#ffffff' if is_own_message else '#e9edef'};
                background: transparent;
            }}
        """)
        
        bubble_layout = QVBoxLayout(bubble_frame)
        bubble_layout.setSpacing(2)
        bubble_layout.setContentsMargins(12, 8, 12, 8)
        
        # Message content
        content = QLabel(emoji.emojize(self.message_data['message'], language='alias'))
        content.setWordWrap(True)
        content.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        content.setTextFormat(Qt.TextFormat.RichText)
        content.setStyleSheet("font-size: 14px;")
        bubble_layout.addWidget(content)
        
        # Time and status
        time_layout = QHBoxLayout()
        time_layout.setSpacing(4)
        time_layout.addStretch()
        
        timestamp = QLabel(self.message_data['timestamp'].strftime("%H:%M"))
        timestamp.setStyleSheet("""
            color: #808080;
            font-size: 11px;
            margin-right: 2px;
        """)
        timestamp.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        time_layout.addWidget(timestamp)
        
        bubble_layout.addLayout(time_layout)
        
        # Bottom row with reactions
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 2, 0, 0)
        bottom_row.setSpacing(4)
        
        # Reactions display
        if self.message_data.get('reactions'):
            reactions_frame = QFrame()
            reactions_frame.setStyleSheet("""
                QFrame {
                    background-color: #252525;
                    border-radius: 12px;
                    border: 1px solid #3d3d3d;
                }
                QLabel {
                    padding: 0px 4px;
                }
            """)
            reactions_layout = QHBoxLayout(reactions_frame)
            reactions_layout.setContentsMargins(8, 4, 8, 4)
            reactions_layout.setSpacing(4)
            
            reaction_counts = {}
            for reaction in self.message_data['reactions'].values():
                if reaction in reaction_counts:
                    reaction_counts[reaction] += 1
                else:
                    reaction_counts[reaction] = 1
            
            for reaction, count in reaction_counts.items():
                reaction_label = QLabel(f"{reaction} {count}" if count > 1 else reaction)
                reaction_label.setStyleSheet("font-size: 13px;")
                reactions_layout.addWidget(reaction_label)
            
            bottom_row.addWidget(reactions_frame)
        
        bottom_row.addStretch()
        
        # Reaction button (only for messages from others)
        if not is_own_message:
            user_reaction = None
            if self.message_data.get('reactions'):
                user_reaction = self.message_data['reactions'].get(str(self.chat_widget.user_data['id']))
            
            self.reaction_button = QPushButton(user_reaction + " +" if user_reaction else "😊")
            self.reaction_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 4px;
                    color: #808080;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #2d2d2d;
                    border-radius: 6px;
                }
            """)
            self.reaction_button.setFixedSize(28, 28)
            self.reaction_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.reaction_button.clicked.connect(self.show_reaction_menu)
            bottom_row.addWidget(self.reaction_button)
        
        container_layout.addWidget(bubble_frame)
        container_layout.addLayout(bottom_row)
        
        main_layout.addWidget(container)
        
        if not is_own_message:
            main_layout.addStretch()

    def add_reaction(self, reaction):
        # Remove existing reaction if any
        self.chat_widget.db_manager.remove_message_reaction(
            str(self.message_data['_id']),
            str(self.chat_widget.user_data['id'])
        )
        
        # Add new reaction
        self.chat_widget.db_manager.add_message_reaction(
            str(self.message_data['_id']),
            str(self.chat_widget.user_data['id']),
            reaction
        )
        
        # Update the message data
        self.message_data = self.chat_widget.db_manager.get_message(str(self.message_data['_id']))
        
        # Update the UI
        self.chat_widget.update_messages()
    
    def show_reaction_menu(self):
        if not self.reaction_menu:
            self.reaction_menu = QuickReactionMenu(self)
        
        # Position the menu above the reaction button
        button_pos = self.reaction_button.mapToGlobal(self.reaction_button.rect().topLeft())
        menu_x = button_pos.x() - self.reaction_menu.width()//2 + self.reaction_button.width()//2
        menu_y = button_pos.y() - self.reaction_menu.height() - 5  # 5px gap
        
        # Ensure menu stays within screen bounds
        screen = QApplication.primaryScreen().geometry()
        menu_x = max(screen.left(), min(menu_x, screen.right() - self.reaction_menu.width()))
        menu_y = max(screen.top(), min(menu_y, screen.bottom() - self.reaction_menu.height()))
        
        self.reaction_menu.move(menu_x, menu_y)
        self.reaction_menu.show()
        self.reaction_menu.activateWindow()
    
    def show_full_emoji_picker(self):
        if not hasattr(self.chat_widget, 'emoji_picker'):
            self.chat_widget.emoji_picker = EmojiPickerWindow(self)
        
        picker = self.chat_widget.emoji_picker
        picker.on_emoji_selected = lambda emoji: self.add_reaction(emoji)
        
        # Position picker above the message
        pos = self.mapToGlobal(QPoint(0, -picker.height()))
        picker.move(pos)
        picker.show()

class UserSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_user = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Neuen Chat starten")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #36393f;
                color: #ffffff;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #202225;
                border-radius: 4px;
                background-color: #40444b;
                color: #ffffff;
                margin-bottom: 10px;
            }
            QListWidget {
                background-color: #40444b;
                border: 1px solid #202225;
                border-radius: 4px;
                color: #ffffff;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #32353b;
            }
            QListWidget::item:selected {
                background-color: #7289da;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #7289da;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #677bc4;
            }
            QPushButton:pressed {
                background-color: #5b6eae;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                margin-bottom: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Suchfeld
        search_layout = QVBoxLayout()
        search_label = QLabel("Benutzer suchen:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Benutzernamen eingeben...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Benutzerliste
        self.user_list = QListWidget()
        self.user_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.user_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.user_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.user_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Chat starten")
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #747f8d;
            }
            QPushButton:hover {
                background-color: #68727f;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)

        # Verbindungen
        self.search_input.textChanged.connect(self.filter_users)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.user_list.itemDoubleClicked.connect(self.accept)
        self.user_list.currentItemChanged.connect(self.update_ok_button)

        # Initial state
        self.ok_button.setEnabled(False)

    def set_users(self, users, current_user_id):
        self.all_users = [u for u in users if u['id'] != current_user_id]
        self.update_user_list()

    def update_user_list(self):
        self.user_list.clear()
        for user in self.all_users:
            item = QListWidgetItem()
            item.setText(f"{user['username']}")
            item.setData(Qt.UserRole, user)
            self.user_list.addItem(item)

    def filter_users(self, search_text):
        search_text = search_text.lower()
        for i in range(self.user_list.count()):
            item = self.user_list.item(i)
            user = item.data(Qt.UserRole)
            item.setHidden(search_text not in user['username'].lower())

    def update_ok_button(self, current, previous):
        self.ok_button.setEnabled(current is not None)

    def get_selected_user(self):
        if self.result() == QDialog.Accepted and self.user_list.currentItem():
            return self.user_list.currentItem().data(Qt.UserRole)
        return None

class ChatWidget(QWidget):
    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_recipient = None
        self.emoji_picker = None
        self.last_message_id = 0  # Track the last message ID
        self.setup_ui()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_messages)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel (contacts and search)
        self.left_panel = QWidget()
        self.left_panel.setStyleSheet("""
            QWidget {
                background-color: #1a1d24;
            }
        """)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Chat title
        chat_title = QLabel("Chats")
        chat_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                padding: 20px 16px 10px 16px;
            }
        """)
        
        # Add header container for title and new chat button
        header_container = QHBoxLayout()
        header_container.addWidget(chat_title)
        
        # Add New Chat button
        self.new_chat_btn = QPushButton("➕")  # Make it an instance variable
        self.new_chat_btn.setObjectName("newChatButton")  # Add object name for debugging
        self.new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Add cursor
        self.new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-size: 20px;
                padding: 20px 16px 10px 16px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover {
                color: #dcddde;
            }
        """)
        self.new_chat_btn.clicked.connect(self.start_new_chat)
        header_container.addWidget(self.new_chat_btn)
        header_container.addStretch()
        
        left_layout.addLayout(header_container)
        
        # Search bar
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background-color: #1a1d24;
                padding: 8px 16px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search messages or users")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #1a1d24;
                border: none;
                border-radius: 4px;
                color: #8e9297;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #1a1d24;
            }
        """)
        search_layout.addWidget(self.search_bar)
        left_layout.addWidget(search_container)
        
        # Recent label
        recent_label = QLabel("Recent")
        recent_label.setStyleSheet("""
            QLabel {
                color: #8e9297;
                font-size: 13px;
                padding: 16px 16px 8px 16px;
            }
        """)
        left_layout.addWidget(recent_label)
        
        # Contacts list
        self.contacts_list = QListWidget()
        self.contacts_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1d24;
                border: none;
            }
            QListWidget::item {
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px 8px;
            }
            QListWidget::item:selected {
                background-color: #36393f;
            }
            QListWidget::item:hover {
                background-color: #2f3136;
            }
        """)
        left_layout.addWidget(self.contacts_list)
        
        # Right panel (chat area)
        self.right_panel = QWidget()
        self.right_panel.setStyleSheet("""
            QWidget {
                background-color: #36393f;
            }
        """)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Chat header
        self.header = QFrame()
        self.header.setStyleSheet("""
            QFrame {
                background-color: #36393f;
                border-bottom: 1px solid #2f3136;
            }
        """)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        # User info in header
        user_info_layout = QHBoxLayout()
        user_info_layout.setSpacing(12)
        
        # Avatar placeholder (you can replace with actual avatar)
        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #2f3136;
                border-radius: 15px;
                padding: 5px;
                min-width: 30px;
                min-height: 30px;
            }
        """)
        user_info_layout.addWidget(avatar_label)
        
        # User name and status
        user_details = QVBoxLayout()
        user_details.setSpacing(2)
        
        self.chat_title = QLabel("Select a conversation")
        self.chat_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        user_details.addWidget(self.chat_title)
        
        status_label = QLabel("Active")
        status_label.setStyleSheet("color: #8e9297; font-size: 12px;")
        user_details.addWidget(status_label)
        
        user_info_layout.addLayout(user_details)
        user_info_layout.addStretch()
        
        header_layout.addLayout(user_info_layout)
        
        # Header buttons
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                color: #b9bbbe;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2f3136;
                color: #ffffff;
            }
        """
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setStyleSheet(button_style)
        header_layout.addWidget(self.search_btn)
        
        self.video_call_btn = QPushButton("📹")
        self.video_call_btn.setStyleSheet(button_style)
        header_layout.addWidget(self.video_call_btn)
        
        self.voice_call_btn = QPushButton("📞")
        self.voice_call_btn.setStyleSheet(button_style)
        header_layout.addWidget(self.voice_call_btn)
        
        right_layout.addWidget(self.header)
        
        # Messages area
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.messages_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #36393f;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2f3136;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #202225;
                min-height: 24px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(0, 16, 0, 16)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()
        
        self.messages_scroll.setWidget(self.messages_container)
        right_layout.addWidget(self.messages_scroll)
        
        # Message input area
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: #36393f;
                border-top: 1px solid #2f3136;
                padding: 0px 16px 16px 16px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(16, 12, 16, 12)
        input_layout.setSpacing(8)
        
        # Message input
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #40444b;
                border-radius: 8px;
            }
        """)
        input_frame_layout = QHBoxLayout(input_frame)
        input_frame_layout.setContentsMargins(12, 0, 12, 0)
        input_frame_layout.setSpacing(8)
        
        # Attachment button
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                color: #b9bbbe;
                font-size: 20px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        input_frame_layout.addWidget(self.attach_btn)
        
        # Text input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter Message...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #dcddde;
                padding: 8px 0;
                font-size: 14px;
            }
        """)
        self.message_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.setMinimumHeight(40)
        self.message_input.setMaximumHeight(120)
        input_frame_layout.addWidget(self.message_input)
        
        # Additional input buttons
        for icon in ["😊", "📎", "🖼️"]:
            btn = QPushButton(icon)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 8px;
                    color: #b9bbbe;
                    font-size: 16px;
                }
                QPushButton:hover {
                    color: #ffffff;
                }
            """)
            input_frame_layout.addWidget(btn)
        
        input_layout.addWidget(input_frame)
        
        # Send button
        self.send_btn = QPushButton("➤")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865f2;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)
        input_layout.addWidget(self.send_btn)
        
        right_layout.addWidget(input_container)
        
        # Add panels to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        
        # Set initial splitter sizes (30% left, 70% right)
        self.splitter.setSizes([300, 700])
        
        main_layout.addWidget(self.splitter)
        
        # Connect signals
        self.message_input.textChanged.connect(self.adjust_input_height)
        self.send_btn.clicked.connect(self.send_message)
        self.search_bar.textChanged.connect(self.filter_contacts)
        
        # Load initial data
        self.load_contacts()
        self.load_messages()
        
    def update_users_list(self):
        self.contacts_list.clear()
        users = self.db_manager.get_chat_users(self.user_data['id'])
        self.all_contacts = []  # Store all contacts for filtering
        
        for user_id in users:
            contact_data = {
                'id': user_id,
                'name': f"User {user_id}",
                'status': 'Active',
                'last_message': 'Click to start chatting'
            }
            self.all_contacts.append(contact_data)
            self._add_contact_item(contact_data)

    def _add_contact_item(self, contact_data):
        item = QListWidgetItem()
        
        # Create widget for contact item
        contact_widget = QWidget()
        layout = QHBoxLayout(contact_widget)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Avatar
        avatar = QLabel("👤")
        avatar.setStyleSheet("""
            QLabel {
                background-color: #2f3136;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
                qproperty-alignment: AlignCenter;
            }
        """)
        layout.addWidget(avatar)
        
        # Contact info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name = QLabel(contact_data['name'])
        name.setStyleSheet("color: #ffffff; font-weight: bold;")
        info_layout.addWidget(name)
        
        status = QLabel(contact_data['last_message'])
        status.setStyleSheet("color: #8e9297; font-size: 12px;")
        info_layout.addWidget(status)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Time if available
        if 'last_time' in contact_data:
            time = QLabel(contact_data['last_time'])
            time.setStyleSheet("color: #8e9297; font-size: 12px;")
            layout.addWidget(time)
        
        item.setSizeHint(contact_widget.sizeHint())
        self.contacts_list.addItem(item)
        self.contacts_list.setItemWidget(item, contact_widget)
        item.setData(Qt.UserRole, contact_data['id'])

    def filter_contacts(self, search_text):
        search_text = search_text.lower()
        self.contacts_list.clear()
        
        for contact in self.all_contacts:
            if search_text in contact['name'].lower():
                self._add_contact_item(contact)

    def load_contacts(self):
        """Load all available users except the current user"""
        try:
            # Get all users
            users = self.db_manager.get_users()
            self.all_contacts = []
            
            # Filter out current user and create contact data
            for user in users:
                if str(user['id']) != str(self.user_data['id']):
                    contact_data = {
                        'id': user['id'],
                        'name': user['username'],
                        'status': 'Active',
                        'last_message': ''
                    }
                    
                    # Get last message with this user
                    messages = self.db_manager.get_chat_messages(
                        self.user_data['id'],
                        user['id'],
                        limit=1
                    )
                    
                    if messages:
                        last_msg = messages[0]
                        contact_data['last_message'] = last_msg['message'][:30] + '...' if len(last_msg['message']) > 30 else last_msg['message']
                        contact_data['last_time'] = last_msg['timestamp'].strftime("%H:%M")
                    else:
                        contact_data['last_message'] = 'Click to start chatting'
                    
                    self.all_contacts.append(contact_data)
            
            # Display contacts
            self.contacts_list.clear()
            for contact in self.all_contacts:
                self._add_contact_item(contact)
                
        except Exception as e:
            print(f"Error loading contacts: {e}")

    def send_message(self):
        if not hasattr(self, 'current_recipient') or not self.message_input.toPlainText().strip():
            return
            
        message_text = self.message_input.toPlainText().strip()
        self.message_input.clear()
        
        try:
            # Save message to database
            message_id = self.db_manager.save_chat_message(
                self.user_data['id'],
                self.current_recipient,
                message_text
            )
            
            if message_id:
                # Add message to UI
                message_data = {
                    'id': message_id,
                    'message': message_text,
                    'timestamp': datetime.now(),
                    'user_id': self.user_data['id'],
                    'recipient_id': self.current_recipient,
                    'reactions': {},
                    'sender_name': self.user_data['username']
                }
                self.add_message(message_data)
                
                # Scroll to bottom
                self.scroll_to_bottom()
                
                # Update contacts list to show latest message
                self.load_contacts()
            else:
                print("Failed to save message to database")
                
        except Exception as e:
            print(f"Error sending message: {e}")

    def load_messages(self):
        # Clear existing messages
        while self.messages_layout.count() > 1:  # Keep the stretch at the end
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not hasattr(self, 'current_recipient'):
            return
            
        try:
            # Get messages from database
            messages = self.db_manager.get_chat_messages(
                self.user_data['id'],
                self.current_recipient
            )
            
            if not messages:
                # Add welcome message
                welcome_msg = {
                    'message': 'No messages yet. Start the conversation!',
                    'timestamp': datetime.now(),
                    'user_id': None,
                    'reactions': {}
                }
                self.add_message(welcome_msg)
                return
            
            # Add messages to the layout (reverse order since they come newest first)
            for msg in reversed(messages):
                self.add_message(msg)
            
            # Scroll to bottom
            QTimer.singleShot(100, self.scroll_to_bottom)
            
        except Exception as e:
            print(f"Error loading messages: {e}")

    def add_reaction(self, message_id, reaction_emoji):
        try:
            success = self.db_manager.add_message_reaction(
                message_id,
                self.user_data['id'],
                reaction_emoji
            )
            if success:
                self.load_messages()  # Reload to show new reaction
        except Exception as e:
            print(f"Error adding reaction: {e}")

    def remove_reaction(self, message_id):
        try:
            success = self.db_manager.remove_message_reaction(
                message_id,
                self.user_data['id']
            )
            if success:
                self.load_messages()  # Reload to show removed reaction
        except Exception as e:
            print(f"Error removing reaction: {e}")

    def on_user_selected(self, item):
        self.current_recipient = item.data(Qt.UserRole)
        self.chat_title.setText(f"Chat with User {self.current_recipient}")
        self.send_btn.setEnabled(True)
        self.update_messages()

    def start_new_chat(self):
        """Show dialog to select a new chat recipient"""
        try:
            print("\nStarte neuen Chat Dialog...")
            print(f"Aktueller Benutzer: {self.user_data['username']} (ID: {self.user_data['id']})")
            
            # Get all available users
            users = self.db_manager.get_users()
            if not users:
                print("Keine Benutzer in der Datenbank gefunden!")
                return
                
            print(f"Gefundene Benutzer: {len(users)}")
            
            # Create and show user selection dialog
            dialog = UserSelectionDialog(self)
            dialog.set_users(users, self.user_data['id'])
            
            # Center dialog on screen
            screen = QApplication.primaryScreen().geometry()
            dialog_size = dialog.sizeHint()
            x = (screen.width() - dialog_size.width()) // 2
            y = (screen.height() - dialog_size.height()) // 2
            dialog.move(x, y)
            
            print("Zeige Benutzerauswahl-Dialog...")
            dialog.exec_()
            
            # Connect dialog close event
            def on_dialog_closed():
                if dialog is not None:
                    selected_user = dialog.get_selected_user()
                    if selected_user:
                        print(f"Benutzer ausgewählt: {selected_user['username']} (ID: {selected_user['id']})")
                        self.current_recipient = selected_user['id']
                        self.chat_title.setText(f"Chat mit {selected_user['username']}")
                        self.load_messages()
                        self.load_contacts()
                    else:
                        print("Kein Benutzer ausgewählt")

            dialog.finished.connect(on_dialog_closed)
            
        except Exception as e:
            print(f"Fehler beim Starten eines neuen Chats: {e}")
            import traceback
            traceback.print_exc()

    def scroll_to_bottom(self):
        self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()
        )

    def update_messages(self):
        self.load_messages()

    def send_message(self):
        if not hasattr(self, 'current_recipient') or not self.message_input.toPlainText().strip():
            return
            
        message_text = self.message_input.toPlainText().strip()
        self.message_input.clear()
        
        try:
            # Save message to database
            message_id = self.db_manager.save_chat_message(
                self.user_data['id'],
                self.current_recipient,
                message_text
            )
            
            if message_id:
                # Add message to UI
                message_data = {
                    'id': message_id,
                    'message': message_text,
                    'timestamp': datetime.now(),
                    'user_id': self.user_data['id'],
                    'recipient_id': self.current_recipient,
                    'reactions': {},
                    'sender_name': self.user_data['username']
                }
                self.add_message(message_data)
                
                # Scroll to bottom
                self.scroll_to_bottom()
                
                # Update contacts list to show latest message
                self.load_contacts()
            else:
                print("Failed to save message to database")
                
        except Exception as e:
            print(f"Error sending message: {e}")

    def add_message(self, message_data):
        """Add a message to the chat display"""
        try:
            sender_name = message_data['sender_name']
            message_text = message_data['message']
            timestamp = message_data['timestamp']
            is_own_message = message_data['user_id'] == self.user_data['id']
            
            # Format timestamp
            if isinstance(timestamp, str):
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            
            # Create message widget
            message_widget = QWidget()
            message_layout = QHBoxLayout()
            message_layout.setContentsMargins(10, 5, 10, 5)
            
            # Message content
            content_widget = QWidget()
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(10, 5, 10, 5)
            
            # Sender name
            name_label = QLabel(sender_name)
            name_label.setStyleSheet("color: #888888; font-size: 10px;")
            content_layout.addWidget(name_label)
            
            # Message text
            text_label = QLabel(message_text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("background-color: #2b2b2b; padding: 8px; border-radius: 4px;")
            content_layout.addWidget(text_label)
            
            # Timestamp
            time_label = QLabel(timestamp.strftime("%H:%M"))
            time_label.setStyleSheet("color: #888888; font-size: 10px;")
            content_layout.addWidget(time_label)
            
            content_widget.setLayout(content_layout)
            
            # Add spacing and widgets to main layout
            if is_own_message:
                message_layout.addStretch()
                message_layout.addWidget(content_widget)
                message_widget.setStyleSheet("background-color: #1e1e1e;")
            else:
                message_layout.addWidget(content_widget)
                message_layout.addStretch()
                message_widget.setStyleSheet("background-color: #252525;")
            
            message_widget.setLayout(message_layout)
            
            # Add to chat display
            self.messages_layout.insertWidget(
                self.messages_layout.count() - 1,
                message_widget
            )
            
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Nachricht: {e}")

    def refresh_messages(self):
        """Periodically check for and load new messages"""
        if self.current_recipient:
            try:
                # Get new messages since last_message_id
                messages = self.db_manager.get_chat_messages(
                    self.user_data['id'],
                    self.current_recipient['id'],
                    since_id=self.last_message_id
                )

                if messages:
                    for message in messages:
                        self.add_message(message)
                        self.last_message_id = max(self.last_message_id, message['id'])
                    
                    # Scroll to bottom when new messages arrive
                    self.scroll_to_bottom()
                    
            except Exception as e:
                print(f"Fehler beim Aktualisieren der Nachrichten: {e}")

    def create_message_widget(self, message):
        return MessageBubble(message, self)
    
    def show_emoji_menu(self):
        if not hasattr(self, 'emoji_picker'):
            self.emoji_picker = EmojiPickerWindow(self)
        
        # Position the picker to the right of the emoji button
        button_pos = self.emoji_button.mapToGlobal(self.emoji_button.rect().topRight())
        self.emoji_picker.move(button_pos.x(), 
                             button_pos.y() - self.emoji_picker.height())
        self.emoji_picker.show()

    def insert_emoji(self, emoji_char):
        self.message_input.insertPlainText(emoji_char)

    def adjust_input_height(self):
        # Calculate the height of the text content
        document_size = self.message_input.document().size()
        text_height = document_size.height()
        
        # Add padding to the text height
        padding = 20  # Adjust this value based on your padding/margins
        new_height = text_height + padding
        
        # Clamp the height between minimum and maximum values
        new_height = max(40, min(new_height, 120))
        
        # Set the new height
        self.message_input.setFixedHeight(int(new_height))
