import sys
import os
import threading
import queue
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QProgressBar, QTextEdit,
    QFrame, QFileDialog, QMessageBox, QStatusBar, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QFont

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from core module
from src.extract_github import extract_repo


class LogRedirector:
    """Redirects stdout to a queue for thread-safe logging in the GUI."""
    
    def __init__(self, queue):
        self.queue = queue
        
    def write(self, text):
        self.queue.put(text)
        
    def flush(self):
        pass


class ExtractorMainWindow(QMainWindow):
    """Main window for the GitHub Repository Extractor application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Repository Extractor")
        self.setMinimumSize(800, 600)
        
        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create the main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Init UI components
        self.extraction_running = False
        self.setup_ui()
        
        # Set up logging
        self.log_queue = queue.Queue()
        self.original_stdout = sys.stdout
        sys.stdout = LogRedirector(self.log_queue)
        
        # Timer to check the log queue
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.check_log_queue)
        self.log_timer.start(100)
        
        # Set up the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Apply styles
        self.apply_styles()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Header section
        self.setup_header()
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Extractor tab
        self.extractor_tab = QWidget()
        self.tab_widget.addTab(self.extractor_tab, "Repository Extractor")
        
        # Settings tab (for future expansion)
        self.settings_tab = QWidget()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Set up extractor tab UI
        self.setup_extractor_tab()
        
        # Set up settings tab UI (basic for now)
        self.setup_settings_tab()
    
    def setup_header(self):
        """Set up the header section with logo and title."""
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        # You can add a logo here if you have one
        # logo_label = QLabel()
        # logo_pixmap = QPixmap("resources/logo.png").scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
        # logo_label.setPixmap(logo_pixmap)
        # header_layout.addWidget(logo_label)
        
        # Title and subtitle
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("GitHub Repository Extractor")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("Extract and analyze GitHub repositories with ease")
        subtitle_label.setObjectName("subtitleLabel")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        self.main_layout.addWidget(header_container)
    
    def setup_extractor_tab(self):
        """Set up the UI for the repository extractor tab."""
        layout = QVBoxLayout(self.extractor_tab)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        # Repository URL input section
        input_section = QFrame()
        input_section.setObjectName("inputSection")
        input_layout = QVBoxLayout(input_section)
        
        url_label = QLabel("GitHub Repository URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter GitHub repository URL (e.g., https://github.com/username/repo)")
        self.url_input.returnPressed.connect(self.start_extraction)
        
        input_layout.addWidget(url_label)
        input_layout.addWidget(self.url_input)
        
        # Buttons section
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.extract_button = QPushButton("Extract Repository")
        self.extract_button.setObjectName("primaryButton")
        self.extract_button.clicked.connect(self.start_extraction)
        
        self.open_folder_button = QPushButton("Open Output Folder")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        
        button_layout.addWidget(self.extract_button)
        button_layout.addWidget(self.open_folder_button)
        
        # Progress section
        progress_section = QFrame()
        progress_section.setObjectName("progressSection")
        progress_layout = QVBoxLayout(progress_section)
        
        progress_header = QLabel("Extraction Progress")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        progress_layout.addWidget(progress_header)
        progress_layout.addWidget(self.progress_bar)
        
        # Log section
        log_section = QFrame()
        log_section.setObjectName("logSection")
        log_layout = QVBoxLayout(log_section)
        
        log_header = QLabel("Activity Log")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        
        log_layout.addWidget(log_header)
        log_layout.addWidget(self.log_text)
        
        # Add all sections to the main layout
        layout.addWidget(input_section)
        layout.addWidget(button_container)
        layout.addWidget(progress_section)
        layout.addWidget(log_section)
        layout.addStretch()
    
    def setup_settings_tab(self):
        """Set up the UI for the settings tab."""
        layout = QVBoxLayout(self.settings_tab)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        # Output folder setting
        output_section = QFrame()
        output_section.setObjectName("settingsSection")
        output_layout = QVBoxLayout(output_section)
        
        output_header = QLabel("Output Settings")
        output_header.setObjectName("settingsSectionHeader")
        
        output_folder_container = QWidget()
        output_folder_layout = QHBoxLayout(output_folder_container)
        output_folder_layout.setContentsMargins(0, 0, 0, 0)
        
        output_label = QLabel("Output Folder:")
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText(str(Path("extracted_repos").absolute()))
        self.output_folder_input.setReadOnly(True)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output_folder)
        
        output_folder_layout.addWidget(output_label)
        output_folder_layout.addWidget(self.output_folder_input, 1)
        output_folder_layout.addWidget(browse_button)
        
        output_layout.addWidget(output_header)
        output_layout.addWidget(output_folder_container)
        
        # Add sections to layout
        layout.addWidget(output_section)
        layout.addStretch()
    
    def apply_styles(self):
        """Apply CSS styling to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F7FA;
            }
            
            QTabWidget::pane {
                border: 1px solid #E1E5EB;
                border-radius: 5px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #E1E5EB;
                color: #333;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #E1E5EB;
                border-bottom: none;
            }
            
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C5530;
            }
            
            QLabel#subtitleLabel {
                font-size: 14px;
                color: #666;
            }
            
            QLabel#settingsSectionHeader {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            
            QPushButton {
                padding: 8px 15px;
                background-color: #E1E5EB;
                border: none;
                border-radius: 4px;
                color: #333;
            }
            
            QPushButton:hover {
                background-color: #D0D4DA;
            }
            
            QPushButton#primaryButton {
                background-color: #2C5530;
                color: white;
                font-weight: bold;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #234429;
            }
            
            QLineEdit {
                padding: 8px;
                border: 1px solid #E1E5EB;
                border-radius: 4px;
                background-color: white;
            }
            
            QProgressBar {
                border: 1px solid #E1E5EB;
                border-radius: 4px;
                background-color: white;
                text-align: center;
                height: 20px;
            }
            
            QProgressBar::chunk {
                background-color: #2C5530;
                border-radius: 3px;
            }
            
            QTextEdit {
                border: 1px solid #E1E5EB;
                border-radius: 4px;
                background-color: white;
                font-family: monospace;
            }
            
            QFrame#inputSection, QFrame#progressSection, QFrame#logSection, QFrame#settingsSection {
                background-color: white;
                border: 1px solid #E1E5EB;
                border-radius: 5px;
                padding: 15px;
            }
        """)
    
    def start_extraction(self):
        """Start the repository extraction process."""
        if self.extraction_running:
            return
            
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a GitHub repository URL")
            return
            
        if not url.startswith("https://github.com/"):
            QMessageBox.warning(
                self,
                "Invalid URL", 
                "Invalid GitHub URL. Please enter a valid GitHub repository URL"
            )
            return
        
        # Clear previous log and reset progress
        self.log_text.clear()
        self.progress_bar.setValue(0)
        
        # Update UI state
        self.extraction_running = True
        self.extract_button.setEnabled(False)
        self.status_bar.showMessage("Extraction in progress...")
        
        # Start extraction in a separate thread
        threading.Thread(
            target=self._extraction_thread,
            args=(url,),
            daemon=True
        ).start()
    
    def _extraction_thread(self, url):
        """Thread function to handle repository extraction."""
        try:
            # Call the extraction function
            extract_repo(url)
            
            # Update UI from the main thread
            self.progress_bar.setValue(100)
            self.status_bar.showMessage("Extraction completed successfully")
            QMessageBox.information(
                self, 
                "Success", 
                "Repository extraction completed successfully!"
            )
        except Exception as e:
            # Handle exceptions
            error_message = str(e)
            self.log_text.append(f"\n❌ Error: {error_message}")
            self.status_bar.showMessage("Extraction failed")
            QMessageBox.critical(
                self, 
                "Extraction Error", 
                f"An error occurred during extraction:\n\n{error_message}"
            )
        finally:
            # Reset UI state
            self.extraction_running = False
            self.extract_button.setEnabled(True)
    
    def check_log_queue(self):
        """Check the log queue and update the log text area."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                
                # Update progress bar based on message content
                if "Downloading:" in message and "%" in message:
                    try:
                        # Extract percentage from message
                        percentage = float(message.split("Downloading:")[1].split("%")[0].strip())
                        self.progress_bar.setValue(int(percentage))
                    except (ValueError, IndexError):
                        pass
                
                # Add message to log
                self.log_text.append(message)
                self.log_text.ensureCursorVisible()
                
                # Handle queue properly
                self.log_queue.task_done()
        except queue.Empty:
            pass
    
    def browse_output_folder(self):
        """Open dialog to select output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_folder_input.text()
        )
        
        if folder:
            self.output_folder_input.setText(folder)
            
            # TODO: Update the actual output folder in the extractor
            # This would require modifying the extract_repo function
            # to accept an output directory parameter
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        output_folder = Path(self.output_folder_input.text())
        
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)
        
        # Open the folder in file explorer
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_folder)))
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Restore original stdout
        sys.stdout = self.original_stdout
        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    
    # Enable DPI scaling for high-DPI displays
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = ExtractorMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()