#!/usr/bin/env python3
"""
GUI Updater Script for Apple Design Guidelines
This script patches your existing comparison_gui.py and visualizer_gui.py 
to use the new Apple Design Guidelines styling.
"""

import os
import re

def backup_file(filename):
    """Create a backup of the original file"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup"
        try:
            with open(filename, 'r', encoding='utf-8') as original:
                content = original.read()
            with open(backup_name, 'w', encoding='utf-8') as backup:
                backup.write(content)
            print(f"✅ Created backup: {backup_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup for {filename}: {e}")
            return False
    return False

def patch_comparison_gui():
    """Apply Apple styling patches to comparison_gui.py"""
    
    filename = 'comparison_gui.py'
    if not os.path.exists(filename):
        print(f"❌ {filename} not found - skipping")
        return False
    
    # Create backup first
    backup_file(filename)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Add Apple theme import after existing imports
        if 'from theme_manager import' not in content:
            # Find the last import statement
            import_pattern = r'(from [^\n]+ import [^\n]+\n)'
            imports = re.findall(import_pattern, content)
            if imports:
                last_import = imports[-1]
                apple_import = 'from theme_manager import apply_theme, get_color, get_semantic_color, create_title_label, create_body_label, AppleColors, Spacing\n'
                content = content.replace(last_import, last_import + apple_import)
                print("  ✓ Added Apple theme imports")
        
        # 2. Apply Apple styling in __init__ method
        if 'apply_theme(widget=self.window)' not in content:
            # Find the window geometry setting
            geometry_pattern = r'(self\.window\.geometry\("[^"]+"\))'
            if re.search(geometry_pattern, content):
                apple_patch = '''
        
        # Apply Apple Design Guidelines
        apply_theme(widget=self.window)
        self.window.configure(bg=AppleColors.WINDOW_BACKGROUND)'''
                
                content = re.sub(
                    geometry_pattern,
                    r'\1' + apple_patch,
                    content
                )
                print("  ✓ Added Apple styling initialization")
        
        # 3. Update window background color references
        content = re.sub(
            r'tk\.Toplevel\(([^)]+)\)',
            r'tk.Toplevel(\1)',
            content
        )
        
        # 4. Update header styling if found
        if 'title_label = ttk.Label(' in content and 'font=(' in content:
            content = re.sub(
                r'title_label = ttk\.Label\(\s*([^,]+),\s*text="([^"]+)",\s*font=\([^)]+\)\s*\)',
                r'title_label = create_title_label(\1, "\2", "title_2")',
                content
            )
            print("  ✓ Updated header styling")
        
        # 5. Only write if changes were made
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Successfully patched {filename}")
            return True
        else:
            print(f"ℹ️  {filename} already appears to be patched")
            return True
            
    except Exception as e:
        print(f"❌ Failed to patch {filename}: {e}")
        return False

def patch_visualizer_gui():
    """Apply Apple styling patches to visualizer_gui.py"""
    
    filename = 'visualizer_gui.py'
    if not os.path.exists(filename):
        print(f"❌ {filename} not found - skipping")
        return False
    
    # Create backup first
    backup_file(filename)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Add Apple theme import after existing imports
        if 'from theme_manager import' not in content:
            # Find the last import statement
            import_pattern = r'(from [^\n]+ import [^\n]+\n)'
            imports = re.findall(import_pattern, content)
            if imports:
                last_import = imports[-1]
                apple_import = 'from theme_manager import apply_theme, get_color, get_semantic_color, create_title_label, create_body_label, AppleColors, Spacing\n'
                content = content.replace(last_import, last_import + apple_import)
                print("  ✓ Added Apple theme imports")
        
        # 2. Apply Apple styling in __init__ method
        if 'apply_theme(widget=self.window)' not in content:
            # Find the window geometry setting
            geometry_pattern = r'(self\.window\.geometry\("[^"]+"\))'
            if re.search(geometry_pattern, content):
                apple_patch = '''
        
        # Apply Apple Design Guidelines
        apply_theme(widget=self.window)
        self.window.configure(bg=AppleColors.WINDOW_BACKGROUND)'''
                
                content = re.sub(
                    geometry_pattern,
                    r'\1' + apple_patch,
                    content
                )
                print("  ✓ Added Apple styling initialization")
        
        # 3. Update header styling
        if 'Requirements Analysis' in content and 'font=(' in content:
            content = re.sub(
                r'ttk\.Label\(\s*([^,]+),\s*text="Requirements Analysis",\s*font=\([^)]+\)\s*\)',
                r'create_title_label(\1, "Requirements Analysis", "title_2")',
                content
            )
            print("  ✓ Updated header styling")
        
        # 4. Only write if changes were made
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Successfully patched {filename}")
            return True
        else:
            print(f"ℹ️  {filename} already appears to be patched")
            return True
            
    except Exception as e:
        print(f"❌ Failed to patch {filename}: {e}")
        return False

def patch_advanced_comparison_settings():
    """Apply Apple styling to advanced_comparison_settings.py if it exists"""
    
    filename = 'advanced_comparison_settings.py'
    if not os.path.exists(filename):
        print(f"ℹ️  {filename} not found - skipping (optional)")
        return True
    
    backup_file(filename)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add Apple theme import
        if 'from theme_manager import' not in content:
            import_pattern = r'(from [^\n]+ import [^\n]+\n)'
            imports = re.findall(import_pattern, content)
            if imports:
                last_import = imports[-1]
                apple_import = 'from theme_manager import apply_theme, AppleColors\n'
                content = content.replace(last_import, last_import + apple_import)
        
        # Apply styling to window creation
        if 'self.window = tk.Toplevel(' in content and 'apply_theme' not in content:
            window_pattern = r'(self\.window\.geometry\("[^"]+"\))'
            if re.search(window_pattern, content):
                apple_patch = '''
        
        # Apply Apple Design Guidelines
        apply_theme(widget=self.window)
        self.window.configure(bg=AppleColors.WINDOW_BACKGROUND)'''
                
                content = re.sub(window_pattern, r'\1' + apple_patch, content)
        
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Successfully patched {filename}")
        else:
            print(f"ℹ️  {filename} already appears to be patched")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to patch {filename}: {e}")
        return False

def create_apple_demo():
    """Create a demo script to showcase Apple Design Guidelines"""
    
    demo_content = '''#!/usr/bin/env python3
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
'''
    
    try:
        with open('apple_demo.py', 'w', encoding='utf-8') as f:
            f.write(demo_content)
        print("✅ Created apple_demo.py - run this to see the new design")
        return True
    except Exception as e:
        print(f"❌ Failed to create demo script: {e}")
        return False

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        ('theme_manager.py', 'Required - contains Apple Design Guidelines'),
        ('main.py', 'Required - main application file')
    ]
    
    optional_files = [
        ('comparison_gui.py', 'Optional - comparison results window'),
        ('visualizer_gui.py', 'Optional - file visualization window'),
        ('advanced_comparison_settings.py', 'Optional - advanced settings window')
    ]
    
    print("📋 Checking project files...")
    
    all_required_exist = True
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename} - {description}")
        else:
            print(f"❌ {filename} - {description} - NOT FOUND")
            all_required_exist = False
    
    for filename, description in optional_files:
        if os.path.exists(filename):
            print(f"✅ {filename} - {description}")
        else:
            print(f"ℹ️  {filename} - {description} - Not found (optional)")
    
    return all_required_exist

def main():
    """Main function to apply Apple Design Guidelines"""
    
    print("🍎 Beyond ReqIF - Apple Design Guidelines Updater")
    print("=" * 55)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing required files. Please ensure theme_manager.py and main.py are in place first.")
        return False
    
    print("\n🔧 Applying Apple Design Guidelines...")
    
    success_count = 0
    total_patches = 0
    
    # Patch GUI components
    patches = [
        ("Comparison GUI", patch_comparison_gui),
        ("Visualizer GUI", patch_visualizer_gui),
        ("Advanced Settings", patch_advanced_comparison_settings),
    ]
    
    for name, patch_func in patches:
        print(f"\n📝 Patching {name}...")
        if patch_func():
            success_count += 1
        total_patches += 1
    
    # Create demo
    print(f"\n🎨 Creating demo application...")
    if create_apple_demo():
        success_count += 1
    total_patches += 1
    
    print(f"\n{'='*55}")
    print(f"🎉 Update completed: {success_count}/{total_patches} successful")
    
    if success_count == total_patches:
        print("\n✅ All updates applied successfully!")
        print("\n📋 Next steps:")
        print("1. Run 'python apple_demo.py' to see the new Apple-styled interface")
        print("2. Run 'python main.py' to use your updated ReqIF Tool Suite")
        print("3. Notice the professional, clean appearance following Apple guidelines")
        
        print("\n🎨 Key improvements:")
        print("• Professional color palette (System Blue, Green, Orange, Red)")
        print("• Consistent typography hierarchy")
        print("• Clean spacing using 8pt grid system")
        print("• Enhanced visual feedback with semantic colors")
        print("• Modern button and control styling")
        print("• Better information density and layout")
        
    else:
        print("\n⚠️  Some updates failed. Check the error messages above.")
        print("You can still run the demo with: python apple_demo.py")
    
    return success_count == total_patches

if __name__ == "__main__":
    main()