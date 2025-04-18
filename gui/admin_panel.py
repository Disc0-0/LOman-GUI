import os
import json
import logging
import time
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QGroupBox, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTextEdit, QComboBox,
    QListWidget, QListWidgetItem, QSplitter
)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QBrush, QFont

# Import admin writer functionality
import admin_writer

logger = logging.getLogger('LOManagerGUI.AdminPanel')

class AdminPanel(QWidget):
    """Panel for sending and managing admin messages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = {}
        self.message_history = []
        self.initUI()
        
    def initUI(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout()
        
        # Create message composer section
        composer_group = QGroupBox("Message Composer")
        composer_layout = QVBoxLayout()
        
        # Text area for message input
        self.messageEdit = QTextEdit()
        self.messageEdit.setPlaceholderText("Enter your admin message here...")
        self.messageEdit.setMaximumHeight(150)
        composer_layout.addWidget(QLabel("Message:"))
        composer_layout.addWidget(self.messageEdit)
        
        # Controls for sending message
        controls_layout = QHBoxLayout()
        
        # Target selection
        target_layout = QVBoxLayout()
        target_layout.addWidget(QLabel("Send to:"))
        self.targetCombo = QComboBox()
        self.targetCombo.addItem("All Tiles", -1)  # -1 means all tiles
        # Individual tiles will be added when config is loaded
        target_layout.addWidget(self.targetCombo)
        controls_layout.addLayout(target_layout)
        
        # Send button
        self.sendButton = QPushButton("Send Message")
        self.sendButton.clicked.connect(self.onSendClicked)
        controls_layout.addWidget(self.sendButton)
        
        # Clear button
        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.onClearClicked)
        controls_layout.addWidget(self.clearButton)
        
        composer_layout.addLayout(controls_layout)
        composer_group.setLayout(composer_layout)
        main_layout.addWidget(composer_group)
        
        # Create quick messages section
        quick_group = QGroupBox("Quick Messages")
        quick_layout = QGridLayout()
        
        # Define common admin messages
        quick_messages = [
            "Server restart in 5 minutes",
            "Server restart in 1 minute",
            "Server maintenance starting soon",
            "Thanks for playing!",
            "Please report bugs on Discord",
            "Welcome to the server!"
        ]
        
        # Create buttons in a grid (3 columns)
        cols = 3
        for i, message in enumerate(quick_messages):
            btn = QPushButton(message)
            # Using a lambda with default arg to avoid late binding issue
            btn.clicked.connect(lambda checked, msg=message: self.setQuickMessage(msg))
            row, col = i // cols, i % cols
            quick_layout.addWidget(btn, row, col)
        
        quick_group.setLayout(quick_layout)
        main_layout.addWidget(quick_group)
        
        # Message history section
        history_group = QGroupBox("Message History")
        history_layout = QVBoxLayout()
        
        self.historyList = QListWidget()
        self.historyList.setAlternatingRowColors(True)
        history_layout.addWidget(self.historyList)
        
        # Clear history button
        self.clearHistoryButton = QPushButton("Clear History")
        self.clearHistoryButton.clicked.connect(self.onClearHistoryClicked)
        history_layout.addWidget(self.clearHistoryButton)
        
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
        
        self.setLayout(main_layout)
    
    def setConfig(self, config):
        """Set configuration and update UI accordingly"""
        self.config = config
        
        # Clear existing tile options (except "All Tiles")
        while self.targetCombo.count() > 1:
            self.targetCombo.removeItem(1)
        
        # Add tiles based on config
        if 'tile_num' in config:
            tile_num = config['tile_num']
            for i in range(tile_num):
                self.targetCombo.addItem(f"Tile {i}", i)
    
    def onSendClicked(self):
        """Handle send button click"""
        message = self.messageEdit.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Empty Message", "Please enter a message to send.")
            return
        
        target_index = self.targetCombo.currentIndex()
        target_id = self.targetCombo.itemData(target_index)
        
        # Confirm before sending
        target_text = "all tiles" if target_id == -1 else f"Tile {target_id}"
        confirm = QMessageBox.question(
            self, 'Confirm Send',
            f"Send this message to {target_text}?\n\n{message}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.sendMessage(message, target_id)
    
    def sendMessage(self, message, target_id):
        """Send the admin message"""
        try:
            # Create a thread to avoid UI freezing during the sleep in admin_writer
            threading.Thread(
                target=self._send_message_thread,
                args=(message, target_id),
                daemon=True
            ).start()
            
            # Add to history immediately for UI responsiveness
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            target_text = "All Tiles" if target_id == -1 else f"Tile {target_id}"
            history_text = f"{timestamp} - {target_text}: {message}"
            
            self.message_history.append(history_text)
            self.updateHistoryList()
            
            # Clear the message input
            self.messageEdit.clear()
            
        except Exception as e:
            logger.error(f"Error sending admin message: {e}")
            QMessageBox.critical(
                self, 
                "Error Sending Message", 
                f"Failed to send admin message: {str(e)}"
            )
    
    def _send_message_thread(self, message, target_id):
        """Thread function to send the message without blocking UI"""
        try:
            folder_path = self.config.get('folder_path', '')
            if not folder_path:
                raise ValueError("Server folder path not configured")
            
            if target_id == -1:
                # Send to all tiles
                tile_num = self.config.get('tile_num', 1)
                for i in range(tile_num):
                    admin_writer.write(message, folder_path, i)
                    logger.info(f"Admin message sent to tile {i}: {message}")
            else:
                # Send to specific tile
                admin_writer.write(message, folder_path, target_id)
                logger.info(f"Admin message sent to tile {target_id}: {message}")
                
        except Exception as e:
            logger.error(f"Error in message thread: {e}")
            # We can't directly call QMessageBox from a non-GUI thread
            # In a more complete implementation, we would use signals to show errors
    
    def onClearClicked(self):
        """Clear the message input field"""
        self.messageEdit.clear()
    
    def setQuickMessage(self, message):
        """Set a quick message in the text edit"""
        self.messageEdit.setText(message)
        # Focus the text edit to allow for easy editing
        self.messageEdit.setFocus()
    
    def updateHistoryList(self):
        """Update the message history list"""
        self.historyList.clear()
        # Add items in reverse order (newest first)
        for message in reversed(self.message_history):
            self.historyList.addItem(message)
    
    def onClearHistoryClicked(self):
        """Clear the message history"""
        confirm = QMessageBox.question(
            self, 'Clear History',
            "Are you sure you want to clear the message history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.message_history.clear()
            self.historyList.clear()

