import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Dict, List, Any
import os


class ReqIFVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("ReqIF Visualizer")
        self.root.geometry("1200x800")
        
        # Data storage
        self.requirements_data = []
        self.columns = []
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for buttons
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        ttk.Button(top_frame, text="Open ReqIF File", 
                  command=self.open_reqif_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(top_frame, text="Export to Excel", 
                  command=self.export_to_excel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(top_frame, text="Refresh View", 
                  command=self.refresh_view).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(top_frame, text="No file loaded")
        self.status_label.pack(side=tk.RIGHT)
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for Excel-like display
        self.tree = ttk.Treeview(tree_frame, show='headings')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bottom frame for details
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Details text widget
        ttk.Label(bottom_frame, text="Requirement Details:").pack(anchor=tk.W)
        self.details_text = tk.Text(bottom_frame, height=8, wrap=tk.WORD)
        details_scroll = ttk.Scrollbar(bottom_frame, orient=tk.VERTICAL, 
                                     command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind treeview selection
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
    def open_reqif_file(self):
        """Open and parse ReqIF file"""
        file_path = filedialog.askopenfilename(
            title="Select ReqIF File",
            filetypes=[("ReqIF files", "*.reqif"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.parse_reqif_file(file_path)
                self.populate_treeview()
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse ReqIF file:\n{str(e)}")
                
    def parse_reqif_file(self, file_path: str):
        """Parse ReqIF XML file and extract requirements"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Define namespaces (ReqIF typically uses these)
            namespaces = {
                'reqif': 'http://www.omg.org/reqif',
                'xhtml': 'http://www.w3.org/1999/xhtml'
            }
            
            # Try to find namespaces in the root element
            if root.tag.startswith('{'):
                default_ns = root.tag.split('}')[0][1:]
                namespaces = {'': default_ns, 'reqif': default_ns}
            
            self.requirements_data = []
            self.columns = set()
            
            # Look for spec objects (requirements)
            spec_objects = root.findall('.//SPEC-OBJECT', namespaces) or \
                          root.findall('.//spec-object', namespaces) or \
                          root.findall('.//SpecObject', namespaces)
            
            if not spec_objects:
                # Try without namespaces
                spec_objects = root.findall('.//SPEC-OBJECT') or \
                              root.findall('.//spec-object') or \
                              root.findall('.//SpecObject')
            
            for spec_obj in spec_objects:
                req_data = {}
                
                # Get identifier
                identifier = spec_obj.get('IDENTIFIER') or spec_obj.get('identifier') or \
                           spec_obj.get('ID') or spec_obj.get('id')
                if identifier:
                    req_data['ID'] = identifier
                    self.columns.add('ID')
                
                # Get long name
                long_name = spec_obj.get('LONG-NAME') or spec_obj.get('long-name')
                if long_name:
                    req_data['Name'] = long_name
                    self.columns.add('Name')
                
                # Get values (attributes)
                values = spec_obj.findall('.//ATTRIBUTE-VALUE', namespaces) or \
                        spec_obj.findall('.//attribute-value', namespaces) or \
                        spec_obj.findall('.//AttributeValue', namespaces)
                
                if not values:
                    values = spec_obj.findall('.//ATTRIBUTE-VALUE') or \
                            spec_obj.findall('.//attribute-value') or \
                            spec_obj.findall('.//AttributeValue')
                
                for value in values:
                    # Get attribute definition reference
                    def_ref = value.get('DEFINITION') or value.get('definition')
                    
                    # Get the actual value
                    attr_value = None
                    
                    # Try different value types
                    if value.find('.//THE-VALUE', namespaces) is not None:
                        attr_value = value.find('.//THE-VALUE', namespaces).text
                    elif value.find('.//the-value', namespaces) is not None:
                        attr_value = value.find('.//the-value', namespaces).text
                    elif value.find('.//THE-VALUE') is not None:
                        attr_value = value.find('.//THE-VALUE').text
                    elif value.find('.//the-value') is not None:
                        attr_value = value.find('.//the-value').text
                    elif value.text:
                        attr_value = value.text
                    
                    # Use definition reference as column name, or generate one
                    if def_ref:
                        col_name = def_ref.split('.')[-1]  # Get last part of reference
                    else:
                        col_name = f"Attribute_{len(req_data)}"
                    
                    if attr_value:
                        req_data[col_name] = attr_value
                        self.columns.add(col_name)
                
                # Add requirement text/description if available
                desc_elem = spec_obj.find('.//ATTRIBUTE-VALUE-XHTML', namespaces) or \
                           spec_obj.find('.//attribute-value-xhtml', namespaces)
                
                if not desc_elem:
                    desc_elem = spec_obj.find('.//ATTRIBUTE-VALUE-XHTML') or \
                               spec_obj.find('.//attribute-value-xhtml')
                
                if desc_elem is not None:
                    # Extract text content from XHTML
                    desc_text = self.extract_text_from_xhtml(desc_elem)
                    if desc_text:
                        req_data['Description'] = desc_text
                        self.columns.add('Description')
                
                if req_data:  # Only add if we found some data
                    self.requirements_data.append(req_data)
            
            # Convert columns to sorted list
            self.columns = sorted(list(self.columns))
            
            if not self.requirements_data:
                raise ValueError("No requirements found in the ReqIF file")
                
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML structure: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing ReqIF file: {str(e)}")
    
    def extract_text_from_xhtml(self, element):
        """Extract text content from XHTML elements"""
        text_content = []
        
        if element.text:
            text_content.append(element.text)
        
        for child in element:
            if child.text:
                text_content.append(child.text)
            if child.tail:
                text_content.append(child.tail)
        
        return ' '.join(text_content).strip()
    
    def populate_treeview(self):
        """Populate the treeview with requirements data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.requirements_data:
            return
        
        # Configure columns
        self.tree['columns'] = self.columns
        
        # Set column headings and widths
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, minwidth=100)
        
        # Insert data
        for i, req in enumerate(self.requirements_data):
            values = [req.get(col, '') for col in self.columns]
            self.tree.insert('', 'end', values=values, tags=(f'req_{i}',))
        
        # Configure alternating row colors
        self.tree.tag_configure('oddrow', background='#f0f0f0')
        for i, item in enumerate(self.tree.get_children()):
            if i % 2 == 1:
                self.tree.item(item, tags=('oddrow',))
    
    def on_select(self, event):
        """Handle treeview selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            
            # Display detailed information
            details = "Requirement Details:\n" + "="*50 + "\n\n"
            
            for i, col in enumerate(self.columns):
                if i < len(values) and values[i]:
                    details += f"{col}: {values[i]}\n\n"
            
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)
    
    def refresh_view(self):
        """Refresh the treeview display"""
        self.populate_treeview()
    
    def export_to_excel(self):
        """Export requirements data to Excel file"""
        if not self.requirements_data:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Create DataFrame
                df = pd.DataFrame(self.requirements_data)
                
                # Ensure all columns are present
                for col in self.columns:
                    if col not in df.columns:
                        df[col] = ''
                
                # Reorder columns
                df = df[self.columns]
                
                # Export to Excel
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export to Excel:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ReqIFVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()