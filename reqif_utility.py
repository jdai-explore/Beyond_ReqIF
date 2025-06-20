#!/usr/bin/env python3
"""
ReqIF Comparison Tool
A Python-based GUI application for comparing ReqIF files and folders
with side-by-side content comparison and summary statistics..
"""

import tkinter as tk
from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator
from reqif_gui import ReqIFComparisonGUI

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ReqIFComparisonGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
