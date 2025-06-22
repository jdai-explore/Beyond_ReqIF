#!/usr/bin/env python3
"""
Cleaned ComparisonResultsGUI - Simple Theme Integration
Performance optimized with minimal theme dependencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import Dict, List, Any

# Simple theme import
from theme_manager import apply_theme, get_color


class ComparisonResultsGUI:
    """
    Comparison Results GUI with simple theme integration
    """
    
    def __init__(self, parent: tk.Widget, results: Dict[str, Any]):
        self.parent = parent
        self.results = results
        
        # Create independent window
        self.window = tk.Toplevel(parent)
        self.window.title("Requirements Comparison Results")
        self.window.geometry("1200x800")
        
        # Ensure window independence
        self.window.transient(parent)
        self.window.focus_set()
        
        # Apply simple theme
        apply_theme(widget=self.window)
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def setup_gui(self):
        """Setup GUI using grid geometry manager"""
        # Configure main window grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Create main container
        self.main_frame = ttk.Frame(self.window, padding="15")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Create sections
        self._create_header_section()
        self._create_summary_section()
        self._create_results_section()
        self._create_controls_section()
    
    def _create_header_section(self):
        """Create header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="📊 Requirements Comparison Results",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=(tk.W))
        
        # Timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_label = ttk.Label(
            header_frame,
            text=f"Generated: {timestamp}",
            font=("Helvetica", 9)
        )
        timestamp_label.grid(row=0, column=1, sticky=(tk.E))
    
    def _create_summary_section(self):
        """Create summary statistics"""
        summary_frame = ttk.LabelFrame(self.main_frame, text="📈 Summary Statistics", padding="10")
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Configure grid for 4 columns
        for i in range(4):
            summary_frame.columnconfigure(i, weight=1)
        
        # Get statistics
        stats = self.results.get('statistics', {})
        
        # Create summary cards
        self._create_summary_card(summary_frame, "➕ Added", 
                                stats.get('added_count', 0), 0, 0)
        self._create_summary_card(summary_frame, "➖ Deleted", 
                                stats.get('deleted_count', 0), 0, 1)
        self._create_summary_card(summary_frame, "✏️ Modified", 
                                stats.get('modified_count', 0), 0, 2)
        self._create_summary_card(summary_frame, "✅ Unchanged", 
                                stats.get('unchanged_count', 0), 0, 3)
    
    def _create_summary_card(self, parent, title, count, row, col):
        """Create a summary card"""
        card_frame = ttk.Frame(parent, relief="ridge", borderwidth=1)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
        card_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(card_frame, text=title, font=("Helvetica", 10, "bold"))
        title_label.grid(row=0, column=0, pady=(5, 0))
        
        # Count
        count_label = ttk.Label(card_frame, text=str(count), font=("Helvetica", 16, "bold"))
        count_label.grid(row=1, column=0, pady=(0, 5))
    
    def _create_results_section(self):
        """Create results with tabs"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self._create_added_tab()
        self._create_deleted_tab()
        self._create_modified_tab()
        self._create_unchanged_tab()
    
    def _create_added_tab(self):
        """Create added requirements tab"""
        added_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(added_frame, text=f"➕ Added ({len(self.results.get('added', []))})")
        self._create_requirements_tree(added_frame, self.results.get('added', []), "added")
    
    def _create_deleted_tab(self):
        """Create deleted requirements tab"""
        deleted_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(deleted_frame, text=f"➖ Deleted ({len(self.results.get('deleted', []))})")
        self._create_requirements_tree(deleted_frame, self.results.get('deleted', []), "deleted")
    
    def _create_modified_tab(self):
        """Create modified requirements tab"""
        modified_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(modified_frame, text=f"✏️ Modified ({len(self.results.get('modified', []))})")
        self._create_requirements_tree(modified_frame, self.results.get('modified', []), "modified")
    
    def _create_unchanged_tab(self):
        """Create unchanged requirements tab"""
        unchanged_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(unchanged_frame, text=f"✅ Unchanged ({len(self.results.get('unchanged', []))})")
        self._create_requirements_tree(unchanged_frame, self.results.get('unchanged', []), "unchanged")
    
    def _create_requirements_tree(self, parent, requirements: List[Dict], category: str):
        """Create treeview for requirements"""
        # Configure parent grid
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create frame
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Define columns
        columns = ['id', 'title', 'description', 'type']
        if category == "modified":
            columns.extend(['changes'])
        
        # Create treeview
        tree = ttk.Treeview(tree_frame, columns=columns[1:], show='tree headings', selectmode='extended')
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure columns
        tree.heading('#0', text='ID', anchor=tk.W)
        tree.column('#0', width=120, minwidth=80)
        
        for col in columns[1:]:
            tree.heading(col, text=col.title(), anchor=tk.W)
            if col == 'description':
                tree.column(col, width=300, minwidth=200)
            elif col == 'changes':
                tree.column(col, width=200, minwidth=150)
            else:
                tree.column(col, width=150, minwidth=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Populate tree
        self._populate_tree(tree, requirements, category)
        
        # Bind events
        tree.bind('<Double-1>', lambda event: self._on_item_double_click(tree, requirements, category))
        
        # Store references
        setattr(self, f"{category}_tree", tree)
        setattr(self, f"{category}_data", requirements)
    
    def _populate_tree(self, tree, requirements: List[Dict], category: str):
        """Populate treeview with data"""
        for i, req in enumerate(requirements):
            try:
                req_id = str(req.get('id', f'{category.upper()}_{i}'))
                title = str(req.get('title', ''))[:100]
                description = str(req.get('description', ''))[:150]
                req_type = str(req.get('type', ''))
                
                values = [title, description, req_type]
                
                if category == "modified":
                    changes = req.get('changes', {})
                    change_summary = ', '.join(changes.keys()) if changes else 'Unknown changes'
                    values.append(change_summary[:100])
                
                tree.insert('', 'end', text=req_id, values=values)
                
            except Exception as e:
                print(f"Error inserting {category} requirement {i}: {e}")
                continue
    
    def _create_controls_section(self):
        """Create control buttons"""
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        controls_frame.columnconfigure(2, weight=1)
        
        # Export controls
        export_frame = ttk.LabelFrame(controls_frame, text="💾 Export", padding="5")
        export_frame.grid(row=0, column=0, sticky=(tk.W), padx=(0, 15))
        
        ttk.Button(export_frame, text="📄 Export All Results", 
                  command=self._export_all_results).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(export_frame, text="📋 Export Current Tab", 
                  command=self._export_current_tab).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(export_frame, text="📝 Export Summary", 
                  command=self._export_summary).grid(row=0, column=2)
        
        # Close button
        ttk.Button(controls_frame, text="✖️ Close", 
                  command=self._on_closing).grid(row=0, column=3, sticky=(tk.E))
    
    def _on_item_double_click(self, tree, requirements: List[Dict], category: str):
        """Handle double-click on tree item"""
        selection = tree.selection()
        if not selection:
            return
        
        try:
            item = selection[0]
            item_index = tree.index(item)
            
            if item_index < len(requirements):
                req = requirements[item_index]
                self._show_requirement_details(req, category)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show details: {str(e)}")
    
    def _show_requirement_details(self, requirement: Dict, category: str):
        """Show detailed requirement information"""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Requirement Details - {category.title()}")
        details_window.geometry("600x500")
        details_window.transient(self.window)
        
        # Apply theme
        apply_theme(widget=details_window)
        
        # Configure grid
        details_window.columnconfigure(0, weight=1)
        details_window.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title = requirement.get('title', requirement.get('id', 'Unknown'))
        ttk.Label(main_frame, text=f"📋 {title}", 
                 font=("Helvetica", 14, "bold")).grid(row=0, column=0, sticky=(tk.W), pady=(0, 15))
        
        # Details in scrollable text
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        details_text = tk.Text(text_frame, wrap=tk.WORD, state=tk.NORMAL)
        details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Populate details
        details_text.insert(tk.END, f"Category: {category.title()}\n\n")
        details_text.insert(tk.END, f"ID: {requirement.get('id', 'N/A')}\n\n")
        details_text.insert(tk.END, f"Title: {requirement.get('title', 'N/A')}\n\n")
        details_text.insert(tk.END, f"Description: {requirement.get('description', 'N/A')}\n\n")
        details_text.insert(tk.END, f"Type: {requirement.get('type', 'N/A')}\n\n")
        
        # Show changes for modified requirements
        if category == "modified" and 'changes' in requirement:
            details_text.insert(tk.END, "Changes:\n")
            for field, change in requirement['changes'].items():
                details_text.insert(tk.END, f"  {field}: {change}\n")
            details_text.insert(tk.END, "\n")
        
        # Show attributes
        attributes = requirement.get('attributes', {})
        if attributes:
            details_text.insert(tk.END, "Attributes:\n")
            for attr_name, attr_value in attributes.items():
                details_text.insert(tk.END, f"  {attr_name}: {attr_value}\n")
        
        details_text.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=details_window.destroy).grid(
            row=2, column=0, pady=(15, 0))
    
    def _export_all_results(self):
        """Export all results to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export All Results",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname="comparison_results_all.csv"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Category', 'ID', 'Title', 'Description', 'Type', 'Changes'])
                
                for category in ['added', 'deleted', 'modified', 'unchanged']:
                    requirements = self.results.get(category, [])
                    for req in requirements:
                        changes = ''
                        if category == 'modified' and 'changes' in req:
                            changes = ', '.join(req['changes'].keys())
                        
                        writer.writerow([
                            category.title(),
                            req.get('id', ''),
                            req.get('title', ''),
                            req.get('description', ''),
                            req.get('type', ''),
                            changes
                        ])
            
            messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    def _export_current_tab(self):
        """Export current tab to CSV"""
        current_tab = self.notebook.index(self.notebook.select())
        categories = ['added', 'deleted', 'modified', 'unchanged']
        
        if current_tab < len(categories):
            category = categories[current_tab]
            requirements = self.results.get(category, [])
            
            try:
                filename = filedialog.asksaveasfilename(
                    title=f"Export {category.title()} Requirements",
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialname=f"comparison_results_{category}.csv"
                )
                
                if not filename:
                    return
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    header = ['ID', 'Title', 'Description', 'Type']
                    if category == 'modified':
                        header.append('Changes')
                    writer.writerow(header)
                    
                    for req in requirements:
                        row = [
                            req.get('id', ''),
                            req.get('title', ''),
                            req.get('description', ''),
                            req.get('type', '')
                        ]
                        
                        if category == 'modified':
                            changes = ', '.join(req.get('changes', {}).keys())
                            row.append(changes)
                        
                        writer.writerow(row)
                
                messagebox.showinfo("Export Complete", 
                                   f"{category.title()} requirements exported to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export {category} requirements:\n{str(e)}")
    
    def _export_summary(self):
        """Export summary to text file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Summary",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname="comparison_summary.txt"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', encoding='utf-8') as txtfile:
                stats = self.results.get('statistics', {})
                
                txtfile.write("Requirements Comparison Summary\n")
                txtfile.write("=" * 40 + "\n\n")
                
                txtfile.write(f"Added Requirements: {stats.get('added_count', 0)}\n")
                txtfile.write(f"Deleted Requirements: {stats.get('deleted_count', 0)}\n")
                txtfile.write(f"Modified Requirements: {stats.get('modified_count', 0)}\n")
                txtfile.write(f"Unchanged Requirements: {stats.get('unchanged_count', 0)}\n\n")
                
                total = sum([stats.get('added_count', 0), stats.get('deleted_count', 0),
                           stats.get('modified_count', 0), stats.get('unchanged_count', 0)])
                txtfile.write(f"Total Requirements Analyzed: {total}\n\n")
                
                if total > 0:
                    txtfile.write("Change Percentages:\n")
                    txtfile.write(f"  Added: {stats.get('added_count', 0)/total*100:.1f}%\n")
                    txtfile.write(f"  Deleted: {stats.get('deleted_count', 0)/total*100:.1f}%\n")
                    txtfile.write(f"  Modified: {stats.get('modified_count', 0)/total*100:.1f}%\n")
                    txtfile.write(f"  Unchanged: {stats.get('unchanged_count', 0)/total*100:.1f}%\n")
                
                import datetime
                txtfile.write(f"\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            messagebox.showinfo("Export Complete", f"Summary exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export summary:\n{str(e)}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            self.window.destroy()
        except:
            pass


# Example usage
if __name__ == "__main__":
    print("🔧 Cleaned ComparisonResultsGUI - Performance Optimized")
    print("✅ Key features:")
    print("  - Simple theme integration")
    print("  - Fast, clean interface")
    print("  - Full comparison functionality")
    print("  - Professional appearance")