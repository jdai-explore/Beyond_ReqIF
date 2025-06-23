#!/usr/bin/env python3
"""
Theme Diagnostic Test - Find Root Cause of Color Application Issue
"""

import tkinter as tk
from tkinter import ttk

# Test 1: Basic TTK Style Application
def test_basic_styling():
    print("=== TEST 1: Basic TTK Style Application ===")
    
    root = tk.Tk()
    root.title("Basic Style Test")
    root.geometry("400x300")
    
    # Create style BEFORE any widgets
    style = ttk.Style()
    print(f"Available themes: {style.theme_names()}")
    print(f"Current theme: {style.theme_use()}")
    
    # Configure a simple style
    style.configure('TButton', 
                   background='#007AFF',  # Blue
                   foreground='white',
                   font=('Helvetica', 12))
    
    style.configure('TFrame',
                   background='#F8F9FA')  # Light gray
    
    style.configure('TLabel',
                   background='#F8F9FA',
                   foreground='#1D1D1F')
    
    # Create widgets AFTER configuring styles
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Style Test", font=('Helvetica', 16, 'bold')).pack(pady=10)
    ttk.Button(main_frame, text="Styled Button").pack(pady=10)
    ttk.Label(main_frame, text="This should have styled colors").pack(pady=10)
    
    def close_test():
        root.destroy()
    
    ttk.Button(main_frame, text="Close Test", command=close_test).pack(pady=20)
    
    root.mainloop()


# Test 2: Style Application Order
def test_style_order():
    print("\n=== TEST 2: Style Application Order ===")
    
    root = tk.Tk()
    root.title("Style Order Test")
    root.geometry("500x400")
    
    # Test different orders
    style = ttk.Style()
    
    # Method 1: Configure styles first, create widgets after
    print("Configuring styles...")
    style.configure('Test1.TButton', background='red', foreground='white')
    style.configure('Test2.TButton', background='green', foreground='white')
    style.configure('Test3.TButton', background='blue', foreground='white')
    
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Style Order Test", font=('Helvetica', 16, 'bold')).pack(pady=10)
    
    # Create buttons with custom styles
    ttk.Button(main_frame, text="Red Button", style='Test1.TButton').pack(pady=5)
    ttk.Button(main_frame, text="Green Button", style='Test2.TButton').pack(pady=5)
    ttk.Button(main_frame, text="Blue Button", style='Test3.TButton').pack(pady=5)
    
    # Test default style modification
    style.configure('TButton', background='orange', foreground='black')
    ttk.Button(main_frame, text="Default Orange Button").pack(pady=5)
    
    def close_test():
        root.destroy()
    
    ttk.Button(main_frame, text="Close Test", command=close_test).pack(pady=20)
    
    root.mainloop()


# Test 3: Theme Manager Integration Test
def test_theme_manager_integration():
    print("\n=== TEST 3: Theme Manager Integration Test ===")
    
    # Import our theme manager
    try:
        from theme_manager import (
            apply_theme, get_color, get_semantic_color,
            create_primary_button, create_secondary_button,
            configure_main_window
        )
        print("✅ Theme manager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import theme manager: {e}")
        return
    
    root = tk.Tk()
    root.title("Theme Manager Integration Test")
    root.geometry("600x500")
    
    # Apply our custom theme configuration
    print("Applying theme manager configuration...")
    configure_main_window(root)
    
    # Force apply theme
    apply_theme(widget=root)
    
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Test color functions
    print(f"Primary color: {get_color('primary')}")
    print(f"Background color: {get_color('bg')}")
    print(f"Success color: {get_semantic_color('success')}")
    
    # Create test widgets
    ttk.Label(main_frame, text="Theme Manager Test", 
             font=('Helvetica', 16, 'bold')).pack(pady=10)
    
    # Test our custom button creators
    primary_btn = create_primary_button(main_frame, "Primary Button (10% Accent)")
    primary_btn.pack(pady=5)
    
    secondary_btn = create_secondary_button(main_frame, "Secondary Button (30% Secondary)")
    secondary_btn.pack(pady=5)
    
    # Test manual color application
    test_label = ttk.Label(main_frame, text="Manual Color Test")
    test_label.pack(pady=5)
    test_label.configure(foreground=get_semantic_color('success'))
    
    def close_test():
        root.destroy()
    
    ttk.Button(main_frame, text="Close Test", command=close_test).pack(pady=20)
    
    root.mainloop()


# Test 4: Step-by-step debugging
def test_step_by_step():
    print("\n=== TEST 4: Step-by-step Debugging ===")
    
    root = tk.Tk()
    root.title("Step-by-step Debug")
    root.geometry("500x600")
    
    # Step 1: Create style object
    style = ttk.Style()
    print(f"Step 1 - Style created. Current theme: {style.theme_use()}")
    
    # Step 2: Configure root window
    root.configure(bg='#F8F9FA')
    print("Step 2 - Root window background set")
    
    # Step 3: Configure frame style
    style.configure('TFrame', background='#FFFFFF', relief='flat', borderwidth=0)
    print("Step 3 - Frame style configured")
    
    # Step 4: Configure button style
    style.configure('TButton', 
                   background='#007AFF',
                   foreground='white',
                   borderwidth=0,
                   focuscolor='#007AFF',
                   font=('Helvetica', 12),
                   padding=[16, 8])
    print("Step 4 - Button style configured")
    
    # Step 5: Configure button map (state-based styling)
    style.map('TButton',
             background=[('active', '#0056CC'),
                        ('pressed', '#004499')])
    print("Step 5 - Button state mapping configured")
    
    # Step 6: Create widgets
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    print("Step 6 - Main frame created")
    
    ttk.Label(main_frame, text="Step-by-step Debug Test", 
             font=('Helvetica', 16, 'bold')).pack(pady=10)
    
    # Test multiple buttons
    for i in range(3):
        btn = ttk.Button(main_frame, text=f"Test Button {i+1}")
        btn.pack(pady=5)
        print(f"Step 6.{i+1} - Button {i+1} created")
    
    # Step 7: Force update
    root.update_idletasks()
    print("Step 7 - Force update completed")
    
    def close_test():
        root.destroy()
    
    ttk.Button(main_frame, text="Close Test", command=close_test).pack(pady=20)
    
    root.mainloop()


def run_all_tests():
    """Run all diagnostic tests"""
    print("🔍 Starting Theme Diagnostic Tests...")
    print("Close each test window to proceed to the next test.")
    
    test_basic_styling()
    test_style_order()
    test_theme_manager_integration()
    test_step_by_step()
    
    print("\n✅ All diagnostic tests completed!")
    print("\nIf colors are not showing:")
    print("1. Check if ttk widgets are being used (not tk widgets)")
    print("2. Verify style.configure() is called BEFORE widget creation")
    print("3. Ensure style names match exactly (case sensitive)")
    print("4. Check if a system theme is overriding custom styles")


if __name__ == "__main__":
    run_all_tests()