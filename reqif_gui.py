import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from reqif_comparator import ReqIFComparator

class ReqIFComparisonGUI:
    """Main GUI application for ReqIF comparison"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ReqIF Comparison Tool")
        self.root.geometry("1200x800")
        
        self.comparator = ReqIFComparator()
        self.comparison_result = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # File/Folder selection frame
        selection_frame = ttk.LabelFrame(main_frame, text="Select Files or Folders", padding="5")
        selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        selection_frame.columnconfigure(1, weight=1)
        
        # File 1 selection
        ttk.Label(selection_frame, text="File/Folder 1:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file1_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.file1_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(selection_frame, text="Browse File", command=lambda: self.browse_file(1)).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(selection_frame, text="Browse Folder", command=lambda: self.browse_folder(1)).grid(row=0, column=3)
        
        # File 2 selection
        ttk.Label(selection_frame, text="File/Folder 2:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.file2_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.file2_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        ttk.Button(selection_frame, text="Browse File", command=lambda: self.browse_file(2)).grid(row=1, column=2, padx=(0, 5), pady=(5, 0))
        ttk.Button(selection_frame, text="Browse Folder", command=lambda: self.browse_folder(2)).grid(row=1, column=3, pady=(5, 0))
        
        # Compare button
        ttk.Button(selection_frame, text="Compare", command=self.compare_files, style="Accent.TButton").grid(row=2, column=1, pady=(10, 0))
        
        # Summary frame
        summary_frame = ttk.LabelFrame(main_frame, text="Summary Statistics", padding="5")
        summary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.summary_text = tk.Text(summary_frame, height=4, wrap=tk.WORD)
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        summary_frame.columnconfigure(0, weight=1)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Comparison Results", padding="5")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Results notebook for tabs
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Export button
        ttk.Button(main_frame, text="Export Results", command=self.export_results).grid(row=3, column=1, sticky=tk.E, pady=(10, 0))
    
    def browse_file(self, file_num):
        """Browse for a ReqIF file"""
        file_path = filedialog.askopenfilename(
            title=f"Select ReqIF File {file_num}",
            filetypes=[("ReqIF files", "*.reqif *.reqifz"), ("All files", "*.*")]
        )
        if file_path:
            if file_num == 1:
                self.file1_var.set(file_path)
            else:
                self.file2_var.set(file_path)
    
    def browse_folder(self, file_num):
        """Browse for a folder containing ReqIF files"""
        folder_path = filedialog.askdirectory(title=f"Select Folder {file_num}")
        if folder_path:
            if file_num == 1:
                self.file1_var.set(folder_path)
            else:
                self.file2_var.set(folder_path)
    
    def compare_files(self):
        """Compare the selected files or folders"""
        path1 = self.file1_var.get().strip()
        path2 = self.file2_var.get().strip()
        
        if not path1 or not path2:
            messagebox.showerror("Error", "Please select both files or folders to compare.")
            return
        
        if not os.path.exists(path1) or not os.path.exists(path2):
            messagebox.showerror("Error", "One or both selected paths do not exist.")
            return
        
        try:
            self.root.config(cursor="wait")
            self.root.update()
            
            # Determine if we're comparing files or folders
            if os.path.isfile(path1) and os.path.isfile(path2):
                # Compare files
                self.comparison_result = {'single_file': self.comparator.compare_files(path1, path2)}
            elif os.path.isdir(path1) and os.path.isdir(path2):
                # Compare folders
                self.comparison_result = self.comparator.compare_folders(path1, path2)
            else:
                messagebox.showerror("Error", "Please select either two files or two folders, not a mix.")
                return
            
            self.display_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def display_results(self):
        """Display the comparison results"""
        if not self.comparison_result:
            return
        
        # Clear existing tabs
        for tab in self.results_notebook.tabs():
            self.results_notebook.forget(tab)
        
        # Display summary
        self.display_summary()
        
        # Display detailed results
        if 'single_file' in self.comparison_result:
            # Single file comparison
            self.display_single_file_results(self.comparison_result['single_file'])
        else:
            # Folder comparison
            self.display_folder_results(self.comparison_result)
    
    def display_summary(self):
        """Display summary statistics"""
        self.summary_text.delete(1.0, tk.END)
        
        if 'single_file' in self.comparison_result:
            summary = self.comparison_result['single_file']['summary']
            summary_text = f"""Single File Comparison Summary:
Added: {summary['added_count']} requirements
Modified: {summary['modified_count']} requirements  
Deleted: {summary['deleted_count']} requirements
Unchanged: {summary['unchanged_count']} requirements
Total in file 1: {summary['total_old']} | Total in file 2: {summary['total_new']}"""
        else:
            # Folder comparison summary
            total_files = len(self.comparison_result)
            files_with_changes = sum(1 for result in self.comparison_result.values() 
                                   if 'summary' in result and 
                                   (result['summary']['added_count'] > 0 or 
                                    result['summary']['modified_count'] > 0 or 
                                    result['summary']['deleted_count'] > 0))
            
            summary_text = f"""Folder Comparison Summary:
Total files compared: {total_files}
Files with changes: {files_with_changes}
Files unchanged: {total_files - files_with_changes}"""
        
        self.summary_text.insert(tk.END, summary_text)
    
    def display_single_file_results(self, result):
        """Display results for single file comparison"""
        # Added requirements tab
        if result['added']:
            self.create_requirements_tab("Added", result['added'], "green")
        
        # Modified requirements tab
        if result['modified']:
            self.create_modified_tab("Modified", result['modified'])
        
        # Deleted requirements tab
        if result['deleted']:
            self.create_requirements_tab("Deleted", result['deleted'], "red")
        
        # Unchanged requirements tab
        if result['unchanged']:
            self.create_requirements_tab("Unchanged", result['unchanged'], "black")
    
    def display_folder_results(self, results):
        """Display results for folder comparison"""
        # Create a summary tab for all files
        summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="File Summary")
        
        # Create treeview for file summary
        tree_frame = ttk.Frame(summary_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('File', 'Status', 'Added', 'Modified', 'Deleted')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Populate tree with file results
        for filename, result in results.items():
            if 'error' in result:
                tree.insert('', tk.END, values=(filename, 'Error', '', '', ''))
            elif 'status' in result:
                tree.insert('', tk.END, values=(filename, result['status'].title(), '', '', ''))
            elif 'summary' in result:
                summary = result['summary']
                status = 'Changed' if (summary['added_count'] > 0 or 
                                     summary['modified_count'] > 0 or 
                                     summary['deleted_count'] > 0) else 'Unchanged'
                tree.insert('', tk.END, values=(
                    filename, status, 
                    summary['added_count'],
                    summary['modified_count'], 
                    summary['deleted_count']
                ))
    
    def create_requirements_tab(self, tab_name, requirements, color):
        """Create a tab for displaying requirements"""
        frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(frame, text=f"{tab_name} ({len(requirements)})")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure color tag
        text_widget.tag_configure(color, foreground=color)
        
        # Add requirements to text widget
        for req_id, req_data in requirements.items():
            text_widget.insert(tk.END, f"ID: {req_id}\n", color)
            text_widget.insert(tk.END, f"Text: {req_data.get('text', 'N/A')}\n", color)
            if req_data.get('attributes'):
                text_widget.insert(tk.END, f"Attributes: {req_data['attributes']}\n", color)
            text_widget.insert(tk.END, "-" * 80 + "\n\n", color)
        
        text_widget.config(state=tk.DISABLED)
    
    def create_modified_tab(self, tab_name, modified_requirements):
        """Create a tab for displaying modified requirements with diffs"""
        frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(frame, text=f"{tab_name} ({len(modified_requirements)})")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure color tags
        text_widget.tag_configure("red", foreground="red")
        text_widget.tag_configure("green", foreground="green")
        text_widget.tag_configure("blue", foreground="blue")
        
        # Add modified requirements to text widget
        for req_id, req_data in modified_requirements.items():
            text_widget.insert(tk.END, f"ID: {req_id}\n", "blue")
            text_widget.insert(tk.END, "DIFF:\n", "blue")
            
            # Add diff content
            diff_text = req_data.get('diff', 'No diff available')
            for line in diff_text.splitlines():
                if line.startswith('-'):
                    text_widget.insert(tk.END, line + "\n", "red")
                elif line.startswith('+'):
                    text_widget.insert(tk.END, line + "\n", "green")
                else:
                    text_widget.insert(tk.END, line + "\n")
            
            text_widget.insert(tk.END, "=" * 80 + "\n\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def export_results(self):
        """Export comparison results to a file"""
        if not self.comparison_result:
            messagebox.showwarning("Warning", "No comparison results to export.")
            return
        
        file_path = filedialog.asksavename(
            title="Export Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w') as f:
                        json.dump(self.comparison_result, f, indent=2, default=str)
                else:
                    with open(file_path, 'w') as f:
                        f.write("ReqIF Comparison Results\n")
                        f.write("=" * 50 + "\n\n")
                        
                        if 'single_file' in self.comparison_result:
                            result = self.comparison_result['single_file']
                            f.write(f"Added: {len(result['added'])} requirements\n")
                            f.write(f"Modified: {len(result['modified'])} requirements\n")
                            f.write(f"Deleted: {len(result['deleted'])} requirements\n")
                            f.write(f"Unchanged: {len(result['unchanged'])} requirements\n\n")
                        else:
                            f.write(f"Total files compared: {len(self.comparison_result)}\n\n")
                            for filename, result in self.comparison_result.items():
                                f.write(f"File: {filename}\n")
                                if 'summary' in result:
                                    summary = result['summary']
                                    f.write(f"  Added: {summary['added_count']}\n")
                                    f.write(f"  Modified: {summary['modified_count']}\n")
                                    f.write(f"  Deleted: {summary['deleted_count']}\n")
                                f.write("\n")
                
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
