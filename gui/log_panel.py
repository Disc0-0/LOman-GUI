import os
import re
import time
import threading
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, 
    QTextEdit, QCheckBox, QLineEdit,
    QGroupBox, QFileDialog, QMessageBox,
    QSplitter, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QBrush

logger = logging.getLogger('LOManagerGUI.LogPanel')

class LogWatcher(QThread):
    """Watches log files for changes and emits signal when new content is available"""
    
    log_updated = pyqtSignal(str, str)  # filename, new content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_files = {}  # filename -> last position
        self.running = True
        self.mutex = threading.Lock()
    
    def add_log_file(self, filename):
        """Add a log file to watch"""
        with self.mutex:
            if filename not in self.log_files:
                if os.path.exists(filename):
                    self.log_files[filename] = os.path.getsize(filename)
                else:
                    self.log_files[filename] = 0
    
    def remove_log_file(self, filename):
        """Remove a log file from the watch list"""
        with self.mutex:
            if filename in self.log_files:
                del self.log_files[filename]
    
    def run(self):
        """Thread main loop"""
        while self.running:
            with self.mutex:
                for filename in list(self.log_files.keys()):
                    if os.path.exists(filename):
                        current_size = os.path.getsize(filename)
                        last_size = self.log_files[filename]
                        
                        if current_size > last_size:
                            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                                f.seek(last_size)
                                new_content = f.read()
                                if new_content:
                                    self.log_updated.emit(filename, new_content)
                            
                            self.log_files[filename] = current_size
            
            time.sleep(0.5)  # Check every 500ms
    
    def stop(self):
        """Stop the watcher thread"""
        self.running = False

class LogPanel(QWidget):
    """Panel for log viewing and filtering"""
    
    LOG_LEVELS = {
        "ALL": -1,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = {}
        self.log_files = []
        self.current_log = None
        self.filter_text = ""
        self.log_level = "ALL"
        self.auto_scroll = True
        self.initUI()
        
        # Start log watcher
        self.log_watcher = LogWatcher()
        self.log_watcher.log_updated.connect(self.onLogUpdated)
        self.log_watcher.start()
    
    def initUI(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Log file selector
        self.log_selector = QComboBox()
        self.log_selector.currentIndexChanged.connect(self.onLogFileChanged)
        controls_layout.addWidget(QLabel("Log File:"))
        controls_layout.addWidget(self.log_selector)
        
        # Refresh button
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.refreshLogs)
        controls_layout.addWidget(self.refreshButton)
        
        # Browse button
        self.browseButton = QPushButton("Browse...")
        self.browseButton.clicked.connect(self.browseLogFile)
        controls_layout.addWidget(self.browseButton)
        
        main_layout.addLayout(controls_layout)
        
        # Filtering and options
        filter_layout = QHBoxLayout()
        
        # Text filter
        filter_layout.addWidget(QLabel("Filter:"))
        self.filterEdit = QLineEdit()
        self.filterEdit.setPlaceholderText("Enter text to filter...")
        self.filterEdit.textChanged.connect(self.onFilterTextChanged)
        filter_layout.addWidget(self.filterEdit)
        
        # Log level filter
        filter_layout.addWidget(QLabel("Level:"))
        self.levelCombo = QComboBox()
        for level in self.LOG_LEVELS.keys():
            self.levelCombo.addItem(level)
        self.levelCombo.currentTextChanged.connect(self.onLogLevelChanged)
        filter_layout.addWidget(self.levelCombo)
        
        # Auto-scroll checkbox
        self.autoScrollCheck = QCheckBox("Auto-scroll")
        self.autoScrollCheck.setChecked(True)
        self.autoScrollCheck.stateChanged.connect(self.onAutoScrollChanged)
        filter_layout.addWidget(self.autoScrollCheck)
        
        # Clear button
        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.clearLog)
        filter_layout.addWidget(self.clearButton)
        
        # Copy button
        self.copyButton = QPushButton("Copy to Clipboard")
        self.copyButton.clicked.connect(self.copyToClipboard)
        filter_layout.addWidget(self.copyButton)
        
        main_layout.addLayout(filter_layout)
        
        # Log text display
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        self.logText.setLineWrapMode(QTextEdit.NoWrap)
        self.logText.setFont(QApplication.font("Monospace"))
        main_layout.addWidget(self.logText)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.statusLabel = QLabel("No log file loaded")
        status_layout.addWidget(self.statusLabel)
        main_layout.addLayout(status_layout)
        
        self.setLayout(main_layout)
        
        # Set up timer for periodic log refresh
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkLogUpdates)
        self.timer.start(1000)  # Check every second
    
    def setConfig(self, config):
        """Set configuration and update UI accordingly"""
        self.config = config
        self.findLogFiles()
    
    def findLogFiles(self):
        """Find available log files based on configuration"""
        self.log_files = []
        
        # Default logs in the current directory
        if os.path.exists("loman.log"):
            self.log_files.append(os.path.abspath("loman.log"))
        
        if os.path.exists("lomangui.log"):
            self.log_files.append(os.path.abspath("lomangui.log"))
        
        # Game logs in configured directory
        if 'folder_path' in self.config:
            log_dir = self.config['folder_path'].replace("Binaries\\Win64\\", "Saved\\Logs")
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.lower().endswith('.log'):
                        self.log_files.append(os.path.join(log_dir, file))
        
        # Update log selector
        self.log_selector.clear()
        for log_file in self.log_files:
            self.log_selector.addItem(os.path.basename(log_file), log_file)
        
        # Select first log file if available
        if self.log_files:
            self.current_log = self.log_files[0]
            self.loadLogFile(self.current_log)
            self.log_watcher.add_log_file(self.current_log)
    
    def loadLogFile(self, filename):
        """Load a log file into the display"""
        if not os.path.exists(filename):
            self.logText.clear()
            self.statusLabel.setText(f"Log file not found: {os.path.basename(filename)}")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            self.logText.clear()
            self.applyContentFilter(content)
            
            file_size = os.path.getsize(filename)
            modified_time = datetime.fromtimestamp(os.path.getmtime(filename))
            self.statusLabel.setText(
                f"Log: {os.path.basename(filename)} | Size: {file_size / 1024:.1f} KB | "
                f"Last modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # Update watcher
            self.log_watcher.add_log_file(filename)
            self.current_log = filename
            
        except Exception as e:
            logger.error(f"Error loading log file: {e}")
            self.logText.clear()
            self.statusLabel.setText(f"Error loading log file: {str(e)}")
    
    def applyContentFilter(self, content):
        """Apply filtering to log content and update display"""
        if not content:
            return
        
        # Split into lines for filtering
        lines = content.splitlines()
        filtered_lines = []
        
        for line in lines:
            # Apply text filter
            if self.filter_text and self.filter_text.lower() not in line.lower():
                continue
            
            # Apply log level filter
            if self.log_level != "ALL":
                level_match = False
                for level_name in self.LOG_LEVELS.keys():
                    if level_name != "ALL" and level_name in line:
                        level_val = self.LOG_LEVELS[level_name]
                        filter_val = self.LOG_LEVELS[self.log_level]
                        if level_val >= filter_val:
                            level_match = True
                            break
                if not level_match:
                    continue
            
            filtered_lines.append(line)
        
        # Format and add to text edit
        self.formatAndAddLines(filtered_lines)
    
    def formatAndAddLines(self, lines):
        """Format log lines with colors and add to text edit"""
        cursor = self.logText.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        for line in lines:
            fmt = QTextCharFormat()
            
            # Apply colors based on log level
            if "ERROR" in line or "CRITICAL" in line:
                fmt.setForeground(QBrush(QColor("red")))
            elif "WARNING" in line:
                fmt.setForeground(QBrush(QColor("orange")))
            elif "INFO" in line:
                fmt.setForeground(QBrush(QColor("blue")))
            elif "DEBUG" in line:
                fmt.setForeground(QBrush(QColor("gray")))
            
            # Apply highlight for filtered text
            if self.filter_text and self.filter_text.lower() in line.lower():
                fmt.setBackground(QBrush(QColor(255, 255, 0, 50)))  # Light yellow
            
            cursor.insertText(line + "\n", fmt)
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            self.logText.setTextCursor(cursor)
            self.logText.ensureCursorVisible()
    
    def onLogFileChanged(self, index):
        """Handle log file selection change"""
        if index >= 0 and index < len(self.log_files):
            self.loadLogFile(self.log_files[index])
    
    def onFilterTextChanged(self, text):
        """Handle filter text change"""
        self.filter_text = text
        self.refreshLogs()
    
    def onLogLevelChanged(self, level):
        """Handle log level filter change"""
        self.log_level = level
        self.refreshLogs()
    
    def onAutoScrollChanged(self, state):
        """Handle auto-scroll checkbox change"""
        self.auto_scroll = (state == Qt.Checked)
    
    def refreshLogs(self):
        """Refresh log display"""
        if self.current_log:
            self.loadLogFile(self.current_log)
    
    def clearLog(self):
        """Clear log display"""
        self.logText.clear()
    
    def copyToClipboard(self):
        """Copy log content to clipboard"""
        self.logText.selectAll()
        self.logText.copy()
        self.logText.moveCursor(QTextCursor.Start)
        
        QMessageBox.information(
            self,
            "Copied to Clipboard",
            "Log content has been copied to clipboard."
        )
    
    def browseLogFile(self):
        """Browse for a log file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Log File",
            "",
            "Log Files (*.log);;All Files (*.*)"
        )
        
        if file_path:
            # Add to log files list if not already there
            if file_path not in self.log_files:
                self.log_files.append(file_path)
                self.log_selector.addItem(os.path.basename(file_path), file_path)
            
            # Select the file
            index = self.log_selector.findData(file_path)
            if index >= 0:
                self.log_selector.setCurrentIndex(index)
    
    def checkLogUpdates(self):
        """Periodic check for log updates"""
        # This is handled by the LogWatcher class
        pass
    
    def onLogUpdated(self, filename, new_content):
        """Handle new log content"""
        if filename == self.current_log:
            self.applyContentFilter(new_content)
            
            # Update status
            file_size = os.path.getsize(filename)
            modified_time = datetime.fromtimestamp(os.path.getmtime(filename))
            self.statusLabel.setText(
                f"Log: {os.path.basename(filename)} | Size: {file_size / 1024:.1f} KB | "
                f"Last modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
