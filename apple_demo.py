#!/usr/bin/env python3
"""
Apple Design Guidelines Demo for Beyond ReqIF
Shows the new Apple-inspired UI styling
"""

import tkinter as tk
from tkinter import ttk
from theme_manager import (
    configure_main_window, create_title_label, create_body_label, 
    create_primary_button, create_secondary_button, get_semantic_color,
    Spacing, AppleColors, AppleFonts
)

def create_demo():
    """Create demo window showing Apple Design Guidelines"""
    
    root = tk.Tk()
    root.title("Beyond ReqIF - Apple Design Guidelines Demo")
    root.geometry("900x700")
    
    # Apply Apple Design Guidelines
    configure_main_window(root)
    
    # Main container
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header
    header = create_title_label(main_frame, "Apple Design Guidelines", "title_1")
    header.pack(pady=(0, Spacing.S))
    
    subtitle = create_body_label(main_frame, "Professional UI for Beyond ReqIF", secondary=True)
    subtitle.pack(pady=(0, Spacing.XL))
    
    # Create notebook to show different sections
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.L))
    
    # Colors tab
    colors_frame = ttk.Frame(notebook, padding="20")
    notebook.add(colors_frame, text="Colors")
    
    create_title_label(colors_frame, "Color Palette", "headline").pack(anchor=tk.W, pady=(0, Spacing.M))
    
    color_row = ttk.Frame(colors_frame)
    color_row.pack(fill=tk.X, pady=(0, Spacing.L))
    
    colors = [
        ("Primary", AppleColors.SYSTEM_BLUE),
        ("Success", AppleColors.SYSTEM_GREEN),
        ("Warning", AppleColors.SYSTEM_ORANGE),
        ("Error", AppleColors.SYSTEM_RED)
    ]
    
    for name, color in colors:
        color_frame = ttk.Frame(color_row)
        color_frame.pack(side=tk.LEFT, padx=(0, Spacing.L))
        
        swatch = tk.Label(color_frame, text="    ", bg=color, width=6, height=3, relief='solid', borderwidth=1)
        swatch.pack()
        
        label = create_body_label(color_frame, name, secondary=True)
        label.pack(pady=(4, 0))
    
    # Typography tab
    typo_frame = ttk.Frame(notebook, padding="20")
    notebook.add(typo_frame, text="Typography")
    
    create_title_label(typo_frame, "Typography Scale", "headline").pack(anchor=tk.W, pady=(0, Spacing.M))
    
    typo_examples = [
        ("Large Title", "large_title"),
        ("Title 1", "title_1"),
        ("Title 2", "title_2"),
        ("Headline", "headline"),
        ("Body", "body"),
        ("Callout", "callout")
    ]
    
    for text, level in typo_examples:
        if level in ["body", "callout"]:
            create_body_label(typo_frame, f"{text} - Clean and readable typography").pack(anchor=tk.W, pady=(4, 0))
        else:
            create_title_label(typo_frame, f"{text} - Professional headers", level).pack(anchor=tk.W, pady=(4, 0))
    
    # Controls tab
    controls_frame = ttk.Frame(notebook, padding="20")
    notebook.add(controls_frame, text="Controls")
    
    create_title_label(controls_frame, "Interface Controls", "headline").pack(anchor=tk.W, pady=(0, Spacing.M))
    
    # Buttons
    button_row = ttk.Frame(controls_frame)
    button_row.pack(fill=tk.X, pady=(0, Spacing.L))
    
    primary_btn = create_primary_button(button_row, "Primary Action")
    primary_btn.pack(side=tk.LEFT, padx=(0, Spacing.S))
    
    secondary_btn = create_secondary_button(button_row, "Secondary Action")
    secondary_btn.pack(side=tk.LEFT)
    
    # Entry
    create_body_label(controls_frame, "Text Input:").pack(anchor=tk.W, pady=(0, 4))
    entry = ttk.Entry(controls_frame, width=50, font=AppleFonts.get("body"))
    entry.pack(anchor=tk.W, pady=(0, Spacing.L))
    entry.insert(0, "Sample text with Apple styling")
    
    # Status indicators
    create_body_label(controls_frame, "Status Indicators:").pack(anchor=tk.W, pady=(0, 4))
    status_row = ttk.Frame(controls_frame)
    status_row.pack(fill=tk.X, pady=(0, Spacing.L))
    
    statuses = [
        ("✓ Success", "success"),
        ("⚠ Warning", "warning"), 
        ("✗ Error", "error"),
        ("ℹ Info", "info")
    ]
    
    for text, status in statuses:
        status_label = ttk.Label(status_row, text=text, 
                               foreground=get_semantic_color(status),
                               font=AppleFonts.get("callout"))
        status_label.pack(side=tk.LEFT, padx=(0, Spacing.L))
    
    # Sample data table
    create_body_label(controls_frame, "Data Table:").pack(anchor=tk.W, pady=(Spacing.M, 4))
    
    tree_frame = ttk.Frame(controls_frame)
    tree_frame.pack(fill=tk.X, pady=(0, Spacing.L))
    
    tree = ttk.Treeview(tree_frame, columns=('status', 'type'), show='tree headings', height=6)
    tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.heading('#0', text='Requirement ID', anchor=tk.W)
    tree.heading('status', text='Status', anchor=tk.W)
    tree.heading('type', text='Type', anchor=tk.W)
    
    # Sample data
    sample_data = [
        ('REQ-001', 'Approved', 'Functional'),
        ('REQ-002', 'Draft', 'Interface'),
        ('REQ-003', 'Rejected', 'Performance'),
        ('REQ-004', 'Approved', 'Security'),
        ('REQ-005', 'Pending', 'Usability')
    ]
    
    for req_id, status, req_type in sample_data:
        tree.insert('', 'end', text=req_id, values=(status, req_type))
    
    # Footer
    footer_frame = ttk.Frame(main_frame)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(Spacing.L, 0))
    
    footer_text = create_body_label(footer_frame, 
                                   "🍎 Beyond ReqIF now follows Apple Human Interface Guidelines for a professional, clean appearance.", 
                                   secondary=True)
    footer_text.pack()
    
    # Status bar
    status_frame = ttk.Frame(footer_frame)
    status_frame.pack(fill=tk.X, pady=(Spacing.S, 0))
    
    ttk.Separator(status_frame, orient='horizontal').pack(fill=tk.X, pady=(0, Spacing.S))
    
    status_content = ttk.Frame(status_frame)
    status_content.pack(fill=tk.X)
    
    create_body_label(status_content, "Demo ready", secondary=True).pack(side=tk.LEFT)
    create_body_label(status_content, "Apple Design Guidelines v1.0", secondary=True).pack(side=tk.RIGHT)
    
    root.mainloop()

if __name__ == "__main__":
    create_demo()
