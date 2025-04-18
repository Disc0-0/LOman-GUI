import sys
import json
import os
import logging
import traceback
import warnings

# Filter out the specific sipPyTypeDict() deprecation warning
warnings.filterwarnings("ignore", message=r"sipPyTypeDict\(\) is deprecated")

# Import PyQt5 modules
from PyQt5 import sip

# Import PyQt5 modules
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
    QWidget, QMenuBar, QMenu, QAction, QMessageBox, 
    QStatusBar, QLabel
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# Import custom panels
from gui.server_panel import ServerPanel
from gui.mod_panel import ModPanel
from gui.config_panel import ConfigPanel
from gui.log_panel import LogPanel
from gui.admin_panel import AdminPanel

# Import existing functionality
import LastOasisManager
import admin_writer
from mod_checker import add_new_mod_ids, read_json, update_mods_info

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='lomangui.log',
    filemode='a'
)
logger = logging.getLogger('LOManagerGUI')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = {}
        self.initUI()
        self.loadConfig()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("Last Oasis Manager GUI")
        self.setGeometry(100, 100, 1024, 768)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add tabs for each panel
        self.server_panel = ServerPanel()
        self.mod_panel = ModPanel()
        self.config_panel = ConfigPanel()
        self.log_panel = LogPanel()
        self.admin_panel = AdminPanel()
        
        self.tabs.addTab(self.server_panel, "Server Management")
        self.tabs.addTab(self.mod_panel, "Mod Management")
        self.tabs.addTab(self.config_panel, "Configuration")
        self.tabs.addTab(self.log_panel, "Logs")
        self.tabs.addTab(self.admin_panel, "Admin Messages")
        
        layout.addWidget(self.tabs)
        
        # Create menu bar
        self.createMenus()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusMsg = QLabel("Ready")
        self.statusBar.addWidget(self.statusMsg)
        
        # Set up timer for status updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(5000)  # Update every 5 seconds
    
    def createMenus(self):
        """Create application menus"""
        # File menu
        fileMenu = self.menuBar().addMenu("&File")
        
        # Reload Config action
        reloadConfigAction = QAction("Reload &Configuration", self)
        reloadConfigAction.setShortcut("Ctrl+R")
        reloadConfigAction.triggered.connect(self.loadConfig)
        fileMenu.addAction(reloadConfigAction)
        
        # Exit action
        exitAction = QAction("E&xit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # Help menu
        helpMenu = self.menuBar().addMenu("&Help")
        
        # About action
        aboutAction = QAction("&About", self)
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)
    
    def loadConfig(self):
        """Load configuration from config.json"""
        try:
            with open("config.json", 'r') as file:
                self.config = json.load(file)
            
            # Initialize LastOasisManager with the config
            LastOasisManager.update_config()
            
            # Initialize TileTracker
            log_folder = os.path.join(self.config["folder_path"].replace("Binaries\\Win64\\", ""), "Saved\\Logs")
            LastOasisManager.tile_tracker = LastOasisManager.get_tracker(
                log_folder=log_folder,
                config_path="config.json"
            )
            
            # Pass config to panels
            self.server_panel.setConfig(self.config)
            self.mod_panel.setConfig(self.config)
            self.config_panel.setConfig(self.config)
            self.log_panel.setConfig(self.config)
            self.admin_panel.setConfig(self.config)
            
            self.statusMsg.setText("Configuration loaded successfully")
            logger.info("Configuration loaded successfully")
        except Exception as e:
            self.showError("Error loading configuration", str(e))
            logger.error(f"Error loading configuration: {e}")
    
    def updateStatus(self):
        """Update status information periodically"""
        # This will be expanded to show real-time status
        pass
    
    def showAbout(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 
            "About Last Oasis Manager GUI",
            "Last Oasis Manager GUI\n\n"
            "A graphical interface for managing Last Oasis server tiles, "
            "mods, and admin messages."
        )
    
    def showError(self, title, message):
        """Show error dialog"""
        QMessageBox.critical(self, title, message)
    
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            "Are you sure you want to exit? This will not stop any running servers.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clean up resources before exit
            event.accept()
        else:
            event.ignore()


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        logger.critical(traceback.format_exc())
        QMessageBox.critical(
            None,
            "Critical Error",
            f"An unhandled error occurred:\n\n{str(e)}\n\nSee logs for details."
        )


if __name__ == "__main__":
    main()

