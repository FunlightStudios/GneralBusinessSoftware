import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from dotenv import load_dotenv

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from utils.config import DEBUG_MODE

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BusinessApp:
    def __init__(self):
        try:
            # Load environment variables
            if not load_dotenv():
                logger.warning("No .env file found or failed to load")

            # Initialize application
            self.app = QApplication(sys.argv)
            self.app.setStyle('Fusion')
            
            # Set dark theme
            self.setup_dark_theme()
            
            # Initialize database with error handling
            try:
                self.db = DatabaseManager()
                self.db.check_users()
            except Exception as e:
                logger.error(f"Database initialization failed: {str(e)}")
                self.show_error_and_exit("Database Error", 
                    "Failed to initialize database. Please check your configuration.")
                return
            
            # Initialize main stacked widget
            self.main_stack = QStackedWidget()
            self.main_stack.setWindowTitle("Gaming Business Software")
            
            # Initialize windows
            self.login_window = LoginWindow(self.db, self.on_login_success)
            self.main_window = None
            
            # Add login window to stack
            self.main_stack.addWidget(self.login_window)
            self.main_stack.setMinimumSize(1200, 800)
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.critical(f"Failed to initialize application: {str(e)}")
            self.show_error_and_exit("Initialization Error", 
                "Failed to start the application. Please contact support.")

    def setup_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.app.setPalette(palette)
        self.app.setStyleSheet("""
            QToolTip { 
                color: #ffffff; 
                background-color: #2a82da;
                border: 1px solid white;
            }
            QWidget {
                background-color: #1e1e1e;
            }
        """)

    def on_login_success(self, user_data):
        self.main_window = MainWindow(self.db, user_data)
        self.main_stack.addWidget(self.main_window)
        self.main_stack.setCurrentWidget(self.main_window)

    def show_error_and_exit(self, title, message):
        """Show error message box and exit application"""
        if hasattr(self, 'app'):
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle(title)
            error_box.setText(message)
            error_box.exec()
            sys.exit(1)
        else:
            print(f"Critical Error - {title}: {message}")
            sys.exit(1)

    def run(self):
        try:
            self.main_stack.show()
            self.main_stack.showMaximized()
            return self.app.exec()
        except Exception as e:
            logger.critical(f"Application crashed: {str(e)}")
            self.show_error_and_exit("Runtime Error", 
                "An unexpected error occurred. Please restart the application.")

if __name__ == "__main__":
    app = BusinessApp()
    sys.exit(app.run())
