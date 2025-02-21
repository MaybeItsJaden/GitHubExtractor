import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_executable():
    # Get the root directory of the project
    root_dir = Path(__file__).parent.parent
    src_dir = root_dir / 'src'
    
    # Build the executable
    PyInstaller.__main__.run([
        str(src_dir / 'github_extractor_gui.py'),  # main script
        '--onefile',  # create single executable
        '--windowed',  # no console window
        '--name=GitHubExtractor',
        '--clean',
        '--noconfirm',
        # Add tkinter explicitly
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        # Add your other modules
        '--hidden-import=requests',
        '--hidden-import=json',
        '--hidden-import=zipfile',
        # Add data files
        '--add-data', f'{str(src_dir / "extract_github.py")}{";" if sys.platform == "win32" else ":"}.',
        '--add-data', f'{str(src_dir / "utils.py")}{";" if sys.platform == "win32" else ":"}.',
        '--add-data', f'{str(root_dir / "requirements.txt")}{";" if sys.platform == "win32" else ":"}.',
        # Debug options
        '--debug=all',
    ])

if __name__ == "__main__":
    build_executable()