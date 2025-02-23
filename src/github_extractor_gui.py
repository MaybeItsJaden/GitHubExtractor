import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from extract_github import extract_repo
import threading
import queue
import sys
import time

class ModernStyle:
    # Color scheme
    BG_COLOR = "#F5F5F1"  # Soft off-white
    PRIMARY_COLOR = "#2C5530"  # Dark nature green
    ACCENT_COLOR = "#D4AC2B"  # Golden yellow
    TEXT_COLOR = "#2A2A2A"
    
    # Fonts
    HEADER_FONT = ("Helvetica", 24, "bold")
    MAIN_FONT = ("Helvetica", 12)
    BUTTON_FONT = ("Helvetica", 14, "bold")

class GitHubExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Repository Extractor")
        self.style = ModernStyle()
        
        # Add a flag to track if extraction is running
        self.extraction_running = False
        
        # Bind window closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set iPhone-like dimensions (iPhone 13 aspect ratio)
        self.root.geometry("390x844")  # iPhone 13 dimensions
        
        # Configure root
        self.root.configure(bg=self.style.BG_COLOR)
        
        # Create custom styles
        self.setup_styles()
        
        # Create main container
        self.main_container = ttk.Frame(self.root, style="Modern.TFrame", padding="20")
        self.main_container.pack(fill="both", expand=True)
        
        # Create UI elements
        self.create_header()
        self.create_input_section()
        self.create_log_section()
        
        # Queue for thread-safe logging
        self.log_queue = queue.Queue()
        self.check_queue()
        sys.stdout = self
        
        self.loading_animation_active = False
        # New vertical flowing animation frames
        self.loading_frames = [
            "↓\n│\n│",
            "│\n↓\n│",
            "│\n│\n↓",
            "│\n│\n○",
            "│\n○\n│",
            "○\n│\n│"
        ]
        self.loading_index = 0

    def setup_styles(self):
        style = ttk.Style()
        
        # Configure frame style
        style.configure(
            "Modern.TFrame",
            background=self.style.BG_COLOR
        )
        
        # Configure label style
        style.configure(
            "Modern.TLabel",
            background=self.style.BG_COLOR,
            foreground=self.style.TEXT_COLOR,
            font=self.style.MAIN_FONT
        )
        
        # Configure entry style
        style.configure(
            "Modern.TEntry",
            fieldbackground="white",
            font=self.style.MAIN_FONT
        )

    def create_header(self):
        header = tk.Label(
            self.main_container,
            text="GitHub\nExtractor",
            font=self.style.HEADER_FONT,
            bg=self.style.BG_COLOR,
            fg=self.style.PRIMARY_COLOR,
            justify="center"
        )
        header.pack(pady=(0, 30))

    def create_input_section(self):
        # URL input container with shadow effect
        input_container = tk.Frame(
            self.main_container,
            bg="white",
            highlightthickness=1,
            highlightbackground="#E0E0E0",
            bd=0
        )
        input_container.pack(fill="x", pady=(0, 20))
        
        # URL Entry
        self.url_entry = ttk.Entry(
            input_container,
            font=self.style.MAIN_FONT,
            style="Modern.TEntry"
        )
        self.url_entry.pack(fill="x", padx=10, pady=10)
        
        # Bind Enter key to start extraction
        self.url_entry.bind('<Return>', lambda e: self.start_extraction())
        
        # Simplified Extract Button
        self.extract_button = tk.Button(
            self.main_container,
            text="Extract",
            font=self.style.BUTTON_FONT,
            bg=self.style.PRIMARY_COLOR,
            fg="white",
            activebackground="#234429",  # Slightly darker on click
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.start_extraction,
            padx=30,
            pady=10
        )
        self.extract_button.pack(pady=20)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_container,
            variable=self.progress_var,
            maximum=100,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(20, 5))
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to extract")
        self.status_label = ttk.Label(
            self.main_container,
            textvariable=self.status_var,
            style="Modern.TLabel",
            justify="center"
        )
        self.status_label.pack()
        
        # Add loading animation label
        self.loading_var = tk.StringVar(value="")
        self.loading_label = ttk.Label(
            self.main_container,
            textvariable=self.loading_var,
            style="Modern.TLabel",
            justify="center"
        )
        self.loading_label.pack()

    def create_log_section(self):
        # Log container with shadow
        log_container = tk.Frame(
            self.main_container,
            bg="white",
            highlightthickness=1,
            highlightbackground="#E0E0E0",
            bd=0
        )
        log_container.pack(fill="both", expand=True, pady=(20, 0))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            wrap=tk.WORD,
            font=self.style.MAIN_FONT,
            bg="white",
            relief="flat"
        )
        self.log_text.pack(fill="both", expand=True, padx=2, pady=2)

    def write(self, text):
        self.log_queue.put(text)

    def flush(self):
        pass

    def check_queue(self):
        while True:
            try:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self.check_queue)

    def animate_loading(self):
        if self.loading_animation_active:
            self.loading_index = (self.loading_index + 1) % len(self.loading_frames)
            self.loading_var.set(self.loading_frames[self.loading_index])
            self.root.after(100, self.animate_loading)

    def update_status(self, message, animate=True):
        if animate:
            self.loading_animation_active = True
            self.status_var.set(message)
            self.animate_loading()
        else:
            self.loading_animation_active = False
            self.status_var.set(message)
            self.loading_var.set("")  # Clear the loading animation

    def on_closing(self):
        """Handle window closing properly"""
        self.loading_animation_active = False
        self.extraction_running = False
        self.root.quit()
        self.root.destroy()

    def start_extraction(self):
        if self.extraction_running:
            return
            
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a GitHub repository URL")
            return
            
        if not url.startswith("https://github.com/"):
            messagebox.showerror(
                "Error",
                "Invalid GitHub URL. Please enter a valid GitHub repository URL"
            )
            return
        
        self.extraction_running = True
        self.extract_button.configure(state="disabled")
        self.update_status("🚀 Initializing extraction")
        self.progress_var.set(0)
        
        def extraction_thread():
            try:
                self.update_status("📡 Connecting to GitHub")
                time.sleep(0.5)  # Give visual feedback
                
                self.update_status("📥 Downloading repository")
                extract_repo(url)
                
                self.update_status("📦 Processing files")
                time.sleep(0.5)  # Give visual feedback
                
                self.update_status("✨ Extraction complete!", animate=False)
                self.progress_var.set(100)
            except Exception as e:
                self.update_status("❌ Error during extraction", animate=False)
                messagebox.showerror("Error", str(e))
            finally:
                self.loading_animation_active = False
                self.extraction_running = False
                self.extract_button.configure(state="normal")
        
        threading.Thread(target=extraction_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = GitHubExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()