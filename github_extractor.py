#!/usr/bin/env python3
"""
GitHub Repository Extractor
A tool to extract and analyze GitHub repositories.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the GUI application
from src.ui.github_extractor_gui import main as run_gui
# Import core functionality for CLI usage
from src.core.extract_github import extract_repository

def print_usage():
    """Print usage information for CLI mode."""
    print("GitHub Repository Extractor")
    print("Usage:")
    print("  GUI Mode: github_extractor.py")
    print("  CLI Mode: github_extractor.py <repository_url> [output_directory]")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - launch the GUI
        run_gui()
    elif len(sys.argv) >= 2:
        # CLI mode
        if sys.argv[1] in ['-h', '--help']:
            print_usage()
        else:
            repo_url = sys.argv[1]
            output_dir = sys.argv[2] if len(sys.argv) > 2 else './output'
            extract_repository(repo_url, output_dir)
    else:
        print_usage()