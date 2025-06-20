import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Import the other modules
try:
    # Import ReqIF Visualizer
    from reqif_visualizer import ReqIFVisualizer
except ImportError:
    ReqIFVisualizer = None
    print("Warning: Could not import ReqIFVisualizer")

try:
    # Import ReqIF Comparator GUI
    from reqif_comparison_gui import ReqIFComparisonGUI
except ImportError:
    ReqIFComparisonGUI = None
    print("Warning: Could not import ReqIFComparisonGUI")


class ReqIFMainMenu:
    """Main menu application for ReqIF tools"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ReqIF Tools Suite")
        self.root.geometry("600x400")
        self.root.configure(bg='#f0f0f0')
        
        # Center the window
        self.center_window()
        
        # Setup the main menu GUI
        self.setup_gui()
        
        # Store references to opened windows
        self.visualizer_window = None
        self.comparator_window = None
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_gui(self):
        """Setup the main menu GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="ReqIF Tools Suite", 
            font=('Arial', 24, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame, 
            text="Choose a tool to get started", 
            font=('Arial', 12)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Tools frame
        tools_frame = ttk.Frame(main_frame)
        tools_frame.pack(expand=True, fill=tk.BOTH)
        
        # Configure grid
        tools_frame.columnconfigure((0, 1), weight=1)
        tools_frame.rowconfigure(0, weight=1)
        
        # ReqIF Visualizer Card
        self.create_tool_card(
            parent=tools_frame,
            row=0, column=0,
            title="ReqIF Visualizer",
            description="View and analyze ReqIF files\nin an Excel-like interface",
            icon="📊",
            command=self.open_visualizer,
            enabled=ReqIFVisualizer is not None
        )
        
        # ReqIF Comparator Card
        self.create_tool_card(
            parent=tools_frame,
            row=0, column=1,
            title="ReqIF Comparator",
            description="Compare ReqIF files and\nfind differences between versions",
            icon="🔍",
            command=self.open_comparator,
            enabled=ReqIFComparisonGUI is not None
        )
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready - Select a tool to begin",
            font=('Arial', 9)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Exit button
        exit_button = ttk.Button(
            status_frame,
            text="Exit",
            command=self.on_exit
        )
        exit_button.pack(side=tk.RIGHT)
    
    def create_tool_card(self, parent, row, column, title, description, icon, command, enabled=True):
        """Create a tool card widget"""
        # Main card frame
        card_frame = ttk.Frame(parent, relief='raised', borderwidth=2)
        card_frame.grid(row=row, column=column, padx=10, pady=10, sticky='nsew')
        
        # Configure card layout
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure((0, 1, 2, 3), weight=1)
        
        # Icon
        icon_label = ttk.Label(
            card_frame, 
            text=icon, 
            font=('Arial', 48)
        )
        icon_label.grid(row=0, column=0, pady=(20, 10))
        
        # Title
        title_label = ttk.Label(
            card_frame, 
            text=title, 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=1, column=0, pady=(0, 5))
        
        # Description
        desc_label = ttk.Label(
            card_frame, 
            text=description, 
            font=('Arial', 10),
            justify=tk.CENTER
        )
        desc_label.grid(row=2, column=0, pady=(0, 20))
        
        # Button
        if enabled:
            button = ttk.Button(
                card_frame,
                text=f"Open {title}",
                command=command,
                style='Accent.TButton'
            )
        else:
            button = ttk.Button(
                card_frame,
                text="Not Available",
                state='disabled'
            )
        
        button.grid(row=3, column=0, pady=(0, 20), padx=20, sticky='ew')
        
        # Add hover effects if enabled
        if enabled:
            self.add_hover_effect(card_frame, button)
    
    def add_hover_effect(self, card_frame, button):
        """Add hover effects to tool cards"""
        def on_enter(event):
            card_frame.configure(relief='solid', borderwidth=3)
            button.configure(style='Hover.TButton')
        
        def on_leave(event):
            card_frame.configure(relief='raised', borderwidth=2)
            button.configure(style='Accent.TButton')
        
        # Bind events to card frame and all its children
        widgets = [card_frame] + list(card_frame.winfo_children())
        for widget in widgets:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
    
    def open_visualizer(self):
        """Open the ReqIF Visualizer"""
        if ReqIFVisualizer is None:
            messagebox.showerror(
                "Error", 
                "ReqIF Visualizer is not available.\nPlease check if reqif_visualizer.py is in the same directory."
            )
            return
        
        try:
            # Check if visualizer window is already open
            if self.visualizer_window and self.visualizer_window.winfo_exists():
                self.visualizer_window.lift()
                self.visualizer_window.focus_force()
                return
            
            # Create new visualizer window
            self.visualizer_window = tk.Toplevel(self.root)
            visualizer_app = ReqIFVisualizer(self.visualizer_window)
            
            # Update status
            self.status_label.config(text="ReqIF Visualizer opened")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ReqIF Visualizer:\n{str(e)}")
    
    def open_comparator(self):
        """Open the ReqIF Comparator"""
        if ReqIFComparisonGUI is None:
            messagebox.showerror(
                "Error", 
                "ReqIF Comparator is not available.\nPlease check if reqif_comparison_gui.py and reqif_comparator.py are in the same directory."
            )
            return
        
        try:
            # Check if comparator window is already open
            if self.comparator_window and self.comparator_window.winfo_exists():
                self.comparator_window.lift()
                self.comparator_window.focus_force()
                return
            
            # Create new comparator window
            self.comparator_window = tk.Toplevel(self.root)
            comparator_app = ReqIFComparisonGUI(self.comparator_window)
            
            # Update status
            self.status_label.config(text="ReqIF Comparator opened")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ReqIF Comparator:\n{str(e)}")
    
    def on_exit(self):
        """Handle application exit"""
        # Close any open tool windows
        try:
            if self.visualizer_window and self.visualizer_window.winfo_exists():
                self.visualizer_window.destroy()
        except:
            pass
        
        try:
            if self.comparator_window and self.comparator_window.winfo_exists():
                self.comparator_window.destroy()
        except:
            pass
        
        # Close main window
        self.root.quit()
        self.root.destroy()


def setup_styles():
    """Setup custom styles for the application"""
    style = ttk.Style()
    
    # Use a modern theme if available
    try:
        style.theme_use('clam')  # or 'vista', 'xpnative' on Windows
    except:
        pass
    
    # Configure custom styles
    style.configure('Accent.TButton', 
                   foreground='white', 
                   background='#0078d4',
                   font=('Arial', 10, 'bold'))
    
    style.map('Accent.TButton',
             background=[('active', '#106ebe'),
                        ('pressed', '#005a9e')])
    
    style.configure('Hover.TButton',
                   foreground='white',
                   background='#106ebe',
                   font=('Arial', 10, 'bold'))


def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Setup styles
    setup_styles()
    
    # Create and run the main menu
    app = ReqIFMainMenu(root)
    
    # Handle window close event
    def on_closing():
        app.on_exit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()