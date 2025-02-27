"""
GUI for the GitHub Repository Extractor.
"""

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QFileDialog, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

from src.core.extract_github import extract_repository
from src.utils.file_utils import ensure_directory

# Path to store user settings
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".github_extractor_settings.json")

class ExtractionWorker(QThread):
    """Worker thread for repository extraction."""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    
    def __init__(self, repo_url, output_dir):
        super().__init__()
        self.repo_url = repo_url
        self.output_dir = output_dir
        
    def run(self):
        try:
            success = extract_repository(self.repo_url, self.output_dir)
            self.finished.emit(success, self.output_dir)
        except Exception as e:
            self.finished.emit(False, str(e))

class GitHubExtractorWindow(QMainWindow):
    """Main window for the GitHub Repository Extractor."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Repository Extractor")
        self.setMinimumSize(600, 400)
        
        # Try to set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "resources", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Load settings
        self.settings = self.load_settings()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Repository URL input
        url_layout = QHBoxLayout()
        url_label = QLabel("Repository URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://github.com/username/repository")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)
        
        # Output directory selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Output Directory:")
        self.dir_input = QLineEdit()
        
        # Set the output directory from saved settings or default
        default_output_dir = self.settings.get('last_output_dir', './output')
        self.dir_input.setText(default_output_dir)
        
        self.dir_input.setPlaceholderText("Select output directory")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.browse_button)
        main_layout.addLayout(dir_layout)
        
        # Extract button
        self.extract_button = QPushButton("Extract Repository")
        self.extract_button.clicked.connect(self.extract_repo)
        main_layout.addWidget(self.extract_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Log output
        log_label = QLabel("Log:")
        main_layout.addWidget(log_label)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)
        
    def browse_directory(self):
        """Open a file dialog to select output directory."""
        # Start from the last selected directory if available
        start_dir = self.dir_input.text() if os.path.exists(self.dir_input.text()) else "./"
        
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", start_dir)
        if directory:
            self.dir_input.setText(directory)
            # Save the selected directory in settings
            self.settings['last_output_dir'] = directory
            self.save_settings()
            
    def extract_repo(self):
        """Start the repository extraction process."""
        repo_url = self.url_input.text().strip()
        output_dir = self.dir_input.text().strip()
        
        if not repo_url:
            self.log_output.append("Error: Please enter a repository URL")
            return
            
        if not output_dir:
            output_dir = "./output"
            self.dir_input.setText(output_dir)
        
        # Save the output directory in settings
        self.settings['last_output_dir'] = output_dir
        self.save_settings()
            
        self.log_output.append(f"Extracting repository: {repo_url}")
        self.log_output.append(f"Output directory: {output_dir}")
        
        # Disable UI elements during extraction
        self.extract_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start extraction in a separate thread
        self.worker = ExtractionWorker(repo_url, output_dir)
        self.worker.finished.connect(self.extraction_finished)
        self.worker.progress.connect(self.update_progress)
        self.worker.start()
        
    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.setValue(value)
        
    def extraction_finished(self, success, message):
        """Handle extraction completion."""
        if success:
            self.log_output.append(f"Repository extracted successfully to: {message}")
        else:
            self.log_output.append(f"Error extracting repository: {message}")
            
        # Re-enable UI elements
        self.extract_button.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def load_settings(self):
        """Load user settings from file."""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {}
    
    def save_settings(self):
        """Save user settings to file."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

def main():
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    window = GitHubExtractorWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 