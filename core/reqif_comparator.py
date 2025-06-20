"""
ReqIF Comparison Tool
A Python-based GUI application for comparing ReqIF files and folders
with side-by-side content comparison and summary statistics.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import zipfile
import tempfile
import difflib
import filecmp
from collections import defaultdict
import json
from pathlib import Path
from datetime import datetime

# For XML parsing (ReqIF is XML-based)
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    import xml.etree.ElementTree as etree
    HAS_LXML = False

class ReqIFParser:
    """Parser for ReqIF files"""
    
    def __init__(self):
        self.namespaces = {
            'reqif': 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
    
    def parse_reqif_file(self, file_path):
        """Parse a ReqIF file and extract requirements"""
        try:
            if file_path.endswith('.reqifz'):
                return self._parse_reqifz(file_path)
            else:
                return self._parse_reqif(file_path)
        except Exception as e:
            raise Exception(f"Error parsing ReqIF file {file_path}: {str(e)}")
    
    def _parse_reqifz(self, file_path):
        """Parse a zipped ReqIF file"""
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # Find the .reqif file inside the zip
            reqif_files = [f for f in zip_file.namelist() if f.endswith('.reqif')]
            if not reqif_files:
                raise Exception("No .reqif file found in the archive")
            
            # Extract and parse the first .reqif file
            with zip_file.open(reqif_files[0]) as reqif_file:
                return self._parse_xml_content(reqif_file.read())
    
    def _parse_reqif(self, file_path):
        """Parse a regular ReqIF file"""
        with open(file_path, 'rb') as f:
            return self._parse_xml_content(f.read())
    
    def _parse_xml_content(self, xml_content):
        """Parse XML content and extract requirements"""
        try:
            if HAS_LXML:
                root = etree.fromstring(xml_content)
            else:
                root = etree.fromstring(xml_content)
        except:
            # Fallback for malformed XML
            if HAS_LXML:
                root = etree.fromstring(xml_content, parser=etree.XMLParser(recover=True))
            else:
                # Standard library doesn't have recover option
                root = etree.fromstring(xml_content)
        
        requirements = {}
        
        # Find requirements using appropriate method based on available library
        if HAS_LXML:
            # Use XPath with lxml
            spec_objects = root.xpath('.//SPEC-OBJECT', namespaces=self.namespaces)
            if not spec_objects:
                # Fallback: look for elements with IDENTIFIER attribute
                spec_objects = root.xpath('.//*[@IDENTIFIER]')
        else:
            # Use manual traversal with standard library
            spec_objects = self._find_elements_by_tag(root, 'SPEC-OBJECT')
            if not spec_objects:
                # Fallback: look for elements with IDENTIFIER attribute
                spec_objects = self._find_elements_with_attribute(root, 'IDENTIFIER')
        
        for spec_obj in spec_objects:
            req_id = spec_obj.get('IDENTIFIER', '')
            if not req_id:
                continue
                
            # Extract requirement text and attributes
            req_data = {
                'id': req_id,
                'text': self._extract_text_content(spec_obj),
                'attributes': self._extract_attributes(spec_obj)
            }
            
            requirements[req_id] = req_data
        
        return requirements
    
    def _find_elements_by_tag(self, root, tag_name):
        """Find elements by tag name using standard library"""
        elements = []
        for elem in root.iter():
            if elem.tag and elem.tag.endswith(tag_name):
                elements.append(elem)
        return elements
    
    def _find_elements_with_attribute(self, root, attr_name):
        """Find elements with specific attribute using standard library"""
        elements = []
        for elem in root.iter():
            if elem.get(attr_name):
                elements.append(elem)
        return elements
    
    def _extract_text_content(self, element):
        """Extract text content from XML element"""
        text_parts = []
        
        if HAS_LXML:
            # Use XPath with lxml
            attr_values = element.xpath('.//ATTRIBUTE-VALUE-STRING | .//ATTRIBUTE-VALUE-XHTML', 
                                      namespaces=self.namespaces)
            
            for attr_val in attr_values:
                # Try to get the value
                value_elem = attr_val.find('.//THE-VALUE', self.namespaces)
                if value_elem is not None:
                    if value_elem.text:
                        text_parts.append(value_elem.text.strip())
                    # Also check for XHTML content
                    xhtml_content = value_elem.xpath('.//xhtml:*', namespaces=self.namespaces)
                    for xhtml_elem in xhtml_content:
                        if xhtml_elem.text:
                            text_parts.append(xhtml_elem.text.strip())
        else:
            # Use manual traversal with standard library
            for elem in element.iter():
                if (elem.tag and 
                    ('ATTRIBUTE-VALUE-STRING' in elem.tag or 'ATTRIBUTE-VALUE-XHTML' in elem.tag)):
                    # Look for THE-VALUE elements
                    for child in elem.iter():
                        if child.tag and 'THE-VALUE' in child.tag and child.text:
                            text_parts.append(child.text.strip())
        
        # Fallback: get all text content
        if not text_parts:
            text_parts = [element.text or '']
            for child in element.iter():
                if child.text:
                    text_parts.append(child.text.strip())
        
        return ' '.join(filter(None, text_parts))
    
    def _extract_attributes(self, element):
        """Extract attributes from XML element"""
        attributes = {}
        
        # Get XML attributes
        for key, value in element.attrib.items():
            if key != 'IDENTIFIER':
                attributes[key] = value
        
        # Get child element attributes
        for child in element:
            if child.tag and child.text:
                attributes[child.tag] = child.text.strip()
        
        return attributes

class ReqIFComparator:
    """Compares ReqIF files and generates statistics"""
    
    def __init__(self):
        self.parser = ReqIFParser()
    
    def compare_files(self, file1_path, file2_path):
        """Compare two ReqIF files"""
        try:
            reqs1 = self.parser.parse_reqif_file(file1_path)
            reqs2 = self.parser.parse_reqif_file(file2_path)
            
            return self._compare_requirements(reqs1, reqs2)
        except Exception as e:
            raise Exception(f"Error comparing files: {str(e)}")
    
    def compare_folders(self, folder1_path, folder2_path):
        """Compare two folders containing ReqIF files"""
        results = {}
        
        # Get all ReqIF files in both folders
        files1 = self._get_reqif_files(folder1_path)
        files2 = self._get_reqif_files(folder2_path)
        
        all_files = set(files1.keys()) | set(files2.keys())
        
        for filename in all_files:
            if filename in files1 and filename in files2:
                # Compare existing files
                try:
                    result = self.compare_files(files1[filename], files2[filename])
                    results[filename] = result
                except Exception as e:
                    results[filename] = {'error': str(e)}
            elif filename in files1:
                # File only in folder1 (deleted)
                results[filename] = {'status': 'deleted', 'file1': files1[filename]}
            else:
                # File only in folder2 (added)
                results[filename] = {'status': 'added', 'file2': files2[filename]}
        
        return results
    
    def _get_reqif_files(self, folder_path):
        """Get all ReqIF files in a folder"""
        files = {}
        folder = Path(folder_path)
        
        for ext in ['*.reqif', '*.reqifz']:
            for file_path in folder.glob(ext):
                files[file_path.name] = str(file_path)
        
        return files
    
    def _compare_requirements(self, reqs1, reqs2):
        """Compare two sets of requirements"""
        added = {}
        modified = {}
        deleted = {}
        unchanged = {}
        
        all_ids = set(reqs1.keys()) | set(reqs2.keys())
        
        for req_id in all_ids:
            if req_id in reqs1 and req_id in reqs2:
                # Requirement exists in both
                req1 = reqs1[req_id]
                req2 = reqs2[req_id]
                
                if self._requirements_equal(req1, req2):
                    unchanged[req_id] = req2
                else:
                    modified[req_id] = {
                        'old': req1,
                        'new': req2,
                        'diff': self._generate_diff(req1, req2)
                    }
            elif req_id in reqs1:
                # Requirement deleted
                deleted[req_id] = reqs1[req_id]
            else:
                # Requirement added
                added[req_id] = reqs2[req_id]
        
        return {
            'added': added,
            'modified': modified,
            'deleted': deleted,
            'unchanged': unchanged,
            'summary': {
                'added_count': len(added),
                'modified_count': len(modified),
                'deleted_count': len(deleted),
                'unchanged_count': len(unchanged),
                'total_old': len(reqs1),
                'total_new': len(reqs2)
            }
        }
    
    def _requirements_equal(self, req1, req2):
        """Check if two requirements are equal"""
        return (req1.get('text', '') == req2.get('text', '') and 
                req1.get('attributes', {}) == req2.get('attributes', {}))
    
    def _generate_diff(self, req1, req2):
        """Generate a diff between two requirements"""
        text1 = req1.get('text', '')
        text2 = req2.get('text', '')
        
        differ = difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            fromfile='old',
            tofile='new',
            lineterm=''
        )
        
        return ''.join(differ)

class ReqIFVisualizerGUI:
    """GUI for visualizing ReqIF files in Excel-like format"""
    
    def __init__(self, parent_window, back_callback):
        self.parent_window = parent_window
        self.back_callback = back_callback
        self.parser = ReqIFParser()
        self.current_requirements = {}
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the visualizer GUI"""
        # Clear parent window
        for widget in self.parent_window.winfo_children():
            widget.destroy()
        
        self.parent_window.title("ReqIF Visualizer")
        
        # Main frame
        main_frame = ttk.Frame(self.parent_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.parent_window.columnconfigure(0, weight=1)
        self.parent_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header frame with back button and file selection
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Back button
        ttk.Button(header_frame, text="← Back to Main Menu", 
                  command=self.back_callback).grid(row=0, column=0, sticky=tk.W)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select ReqIF File", padding="5")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="ReqIF File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_var, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(file_frame, text="Load", command=self.load_file, style="Accent.TButton").grid(row=0, column=3)
        
        # Info frame for file statistics
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="5")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=3, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(0, weight=1)
        
        # Main content frame with notebook for different views
        content_frame = ttk.LabelFrame(main_frame, text="Requirements View", padding="5")
        content_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Export frame
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(export_frame, text="Export to CSV", command=self.export_to_csv).grid(row=0, column=0, sticky=tk.E)
    
    def browse_file(self):
        """Browse for a ReqIF file"""
        file_path = filedialog.askopenfilename(
            title="Select ReqIF File",
            filetypes=[("ReqIF files", "*.reqif *.reqifz"), ("All files", "*.*")]
        )
        if file_path:
            self.file_var.set(file_path)
    
    def load_file(self):
        """Load and parse the selected ReqIF file"""
        file_path = self.file_var.get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a ReqIF file.")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Selected file does not exist.")
            return
        
        try:
            self.parent_window.config(cursor="wait")
            self.parent_window.update()
            
            # Parse the file
            self.current_requirements = self.parser.parse_reqif_file(file_path)
            
            # Update info
            self.update_file_info(file_path)
            
            # Display requirements
            self.display_requirements()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
        finally:
            self.parent_window.config(cursor="")
    
    def update_file_info(self, file_path):
        """Update file information display"""
        self.info_text.delete(1.0, tk.END)
        
        file_size = os.path.getsize(file_path)
        file_size_str = f"{file_size:,} bytes" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f} MB"
        
        info_text = f"""File: {os.path.basename(file_path)}
Size: {file_size_str} | Requirements: {len(self.current_requirements)}
Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        self.info_text.insert(tk.END, info_text)
    
    def display_requirements(self):
        """Display requirements in Excel-like format"""
        # Clear existing tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        if not self.current_requirements:
            return
        
        # Create table view tab
        self.create_table_view()
        
        # Create details view tab
        self.create_details_view()
        
        # Create statistics view tab
        self.create_statistics_view()
    
    def create_table_view(self):
        """Create Excel-like table view of requirements"""
        table_frame = ttk.Frame(self.notebook)
        self.notebook.add(table_frame, text="Table View")
        
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define columns
        columns = ('ID', 'Text', 'Type', 'Status', 'Priority', 'Attributes')
        
        # Create treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure column headings and widths
        tree.heading('ID', text='Requirement ID')
        tree.heading('Text', text='Requirement Text')
        tree.heading('Type', text='Type')
        tree.heading('Status', text='Status')
        tree.heading('Priority', text='Priority')
        tree.heading('Attributes', text='Other Attributes')
        
        # Set column widths
        tree.column('ID', width=150, minwidth=100)
        tree.column('Text', width=400, minwidth=200)
        tree.column('Type', width=100, minwidth=80)
        tree.column('Status', width=100, minwidth=80)
        tree.column('Priority', width=100, minwidth=80)
        tree.column('Attributes', width=200, minwidth=150)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Populate tree with requirements
        for req_id, req_data in self.current_requirements.items():
            text = req_data.get('text', '')[:100] + ('...' if len(req_data.get('text', '')) > 100 else '')
            
            attributes = req_data.get('attributes', {})
            req_type = attributes.get('TYPE', attributes.get('type', 'N/A'))
            status = attributes.get('STATUS', attributes.get('status', 'N/A'))
            priority = attributes.get('PRIORITY', attributes.get('priority', 'N/A'))
            
            # Create a summary of other attributes
            other_attrs = []
            for key, value in attributes.items():
                if key.upper() not in ['TYPE', 'STATUS', 'PRIORITY']:
                    other_attrs.append(f"{key}: {value}")
            other_attrs_str = '; '.join(other_attrs[:3])  # Show first 3 attributes
            if len(other_attrs) > 3:
                other_attrs_str += '...'
            
            tree.insert('', tk.END, values=(
                req_id, text, req_type, status, priority, other_attrs_str
            ))
        
        # Add double-click event to show full requirement
        tree.bind('<Double-1>', lambda event: self.show_requirement_details(tree, event))
        
        # Add search functionality
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        def search_requirements():
            search_term = search_var.get().lower()
            if not search_term:
                return
            
            # Clear current selection
            for item in tree.selection():
                tree.selection_remove(item)
            
            # Search and select matching items
            for item in tree.get_children():
                values = tree.item(item, 'values')
                if any(search_term in str(value).lower() for value in values):
                    tree.selection_add(item)
                    tree.see(item)
                    break
        
        ttk.Button(search_frame, text="Search", command=search_requirements).pack(side=tk.LEFT)
    
    def create_details_view(self):
        """Create detailed view of requirements"""
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="Details View")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(details_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for formatting
        text_widget.tag_configure("header", font=('Consolas', 12, 'bold'), foreground="blue")
        text_widget.tag_configure("id", font=('Consolas', 10, 'bold'), foreground="darkgreen")
        text_widget.tag_configure("text", font=('Consolas', 10), foreground="black")
        text_widget.tag_configure("attr", font=('Consolas', 9), foreground="gray")
        
        # Add all requirements to text widget
        for i, (req_id, req_data) in enumerate(self.current_requirements.items(), 1):
            text_widget.insert(tk.END, f"Requirement #{i}\n", "header")
            text_widget.insert(tk.END, f"ID: {req_id}\n", "id")
            text_widget.insert(tk.END, f"Text: {req_data.get('text', 'N/A')}\n", "text")
            
            if req_data.get('attributes'):
                text_widget.insert(tk.END, "Attributes:\n", "attr")
                for key, value in req_data['attributes'].items():
                    text_widget.insert(tk.END, f"  {key}: {value}\n", "attr")
            
            text_widget.insert(tk.END, "-" * 100 + "\n\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def create_statistics_view(self):
        """Create statistics view"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        # Create text widget for statistics
        stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD, height=20)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Generate statistics
        total_reqs = len(self.current_requirements)
        
        # Count by attributes
        type_counts = defaultdict(int)
        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        
        text_lengths = []
        attr_counts = []
        
        for req_data in self.current_requirements.values():
            attributes = req_data.get('attributes', {})
            
            # Count types, statuses, priorities
            req_type = attributes.get('TYPE', attributes.get('type', 'Unknown'))
            status = attributes.get('STATUS', attributes.get('status', 'Unknown'))
            priority = attributes.get('PRIORITY', attributes.get('priority', 'Unknown'))
            
            type_counts[req_type] += 1
            status_counts[status] += 1
            priority_counts[priority] += 1
            
            # Text length statistics
            text_lengths.append(len(req_data.get('text', '')))
            attr_counts.append(len(attributes))
        
        # Generate statistics text
        stats_text.insert(tk.END, f"REQIF FILE STATISTICS\n{'='*50}\n\n")
        stats_text.insert(tk.END, f"Total Requirements: {total_reqs}\n\n")
        
        # Type distribution
        stats_text.insert(tk.END, "REQUIREMENT TYPES:\n")
        for req_type, count in sorted(type_counts.items()):
            percentage = (count / total_reqs) * 100
            stats_text.insert(tk.END, f"  {req_type}: {count} ({percentage:.1f}%)\n")
        
        stats_text.insert(tk.END, "\nSTATUS DISTRIBUTION:\n")
        for status, count in sorted(status_counts.items()):
            percentage = (count / total_reqs) * 100
            stats_text.insert(tk.END, f"  {status}: {count} ({percentage:.1f}%)\n")
        
        stats_text.insert(tk.END, "\nPRIORITY DISTRIBUTION:\n")
        for priority, count in sorted(priority_counts.items()):
            percentage = (count / total_reqs) * 100
            stats_text.insert(tk.END, f"  {priority}: {count} ({percentage:.1f}%)\n")
        
        # Text length statistics
        if text_lengths:
            avg_length = sum(text_lengths) / len(text_lengths)
            min_length = min(text_lengths)
            max_length = max(text_lengths)
            
            stats_text.insert(tk.END, f"\nTEXT LENGTH STATISTICS:\n")
            stats_text.insert(tk.END, f"  Average: {avg_length:.1f} characters\n")
            stats_text.insert(tk.END, f"  Minimum: {min_length} characters\n")
            stats_text.insert(tk.END, f"  Maximum: {max_length} characters\n")
        
        # Attribute statistics
        if attr_counts:
            avg_attrs = sum(attr_counts) / len(attr_counts)
            min_attrs = min(attr_counts)
            max_attrs = max(attr_counts)
            
            stats_text.insert(tk.END, f"\nATTRIBUTE STATISTICS:\n")
            stats_text.insert(tk.END, f"  Average attributes per requirement: {avg_attrs:.1f}\n")
            stats_text.insert(tk.END, f"  Minimum attributes: {min_attrs}\n")
            stats_text.insert(tk.END, f"  Maximum attributes: {max_attrs}\n")
        
        stats_text.config(state=tk.DISABLED)
    
    def show_requirement_details(self, tree, event):
        """Show detailed view of selected requirement"""
        selection = tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = tree.item(item, 'values')
        req_id = values[0]
        
        if req_id in self.current_requirements:
            req_data = self.current_requirements[req_id]
            
            # Create detail window
            detail_window = tk.Toplevel(self.parent_window)
            detail_window.title(f"Requirement Details - {req_id}")
            detail_window.geometry("800x600")
            
            # Create text widget
            text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD, font=('Consolas', 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add requirement details
            text_widget.insert(tk.END, f"REQUIREMENT ID: {req_id}\n")
            text_widget.insert(tk.END, "=" * 50 + "\n\n")
            text_widget.insert(tk.END, f"TEXT:\n{req_data.get('text', 'N/A')}\n\n")
            
            if req_data.get('attributes'):
                text_widget.insert(tk.END, "ATTRIBUTES:\n")
                text_widget.insert(tk.END, "-" * 20 + "\n")
                for key, value in req_data['attributes'].items():
                    text_widget.insert(tk.END, f"{key}: {value}\n")
            
            text_widget.config(state=tk.DISABLED)
    
    def export_to_csv(self):
        """Export requirements to CSV file"""
        if not self.current_requirements:
            messagebox.showwarning("Warning", "No requirements loaded to export.")
            return
        
        file_path = filedialog.asksavename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    # Get all unique attribute keys
                    all_attr_keys = set()
                    for req_data in self.current_requirements.values():
                        all_attr_keys.update(req_data.get('attributes', {}).keys())
                    
                    # Create header
                    fieldnames = ['ID', 'Text'] + sorted(all_attr_keys)
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    
                    # Write requirements
                    for req_id, req_data in self.current_requirements.items():
                        row = {
                            'ID': req_id,
                            'Text': req_data.get('text', '')
                        }
                        row.update(req_data.get('attributes', {}))
                        writer.writerow(row)
                
                messagebox.showinfo("Success", f"Requirements exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

class MainMenuGUI:
    """Main menu for selecting between Compare and Visualize modes"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ReqIF Tool Suite")
        self.root.geometry("600x400")
        
        self.setup_main_menu()
    
    def setup_main_menu(self):
        """Setup the main menu GUI"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ReqIF Tool Suite", 
                               font=('Helvetica', 20, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Choose a tool to work with ReqIF files:",
                              font=('Helvetica', 12))
        desc_label.grid(row=1, column=0, pady=(0, 40))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 20))
        
        # Compare button with icon-like styling
        compare_frame = ttk.Frame(button_frame, relief='raised', borderwidth=2)
        compare_frame.grid(row=0, column=0, padx=20, pady=10)
        
        ttk.Label(compare_frame, text="📊", font=('Helvetica', 40)).pack(pady=(20, 10))
        ttk.Label(compare_frame, text="ReqIF Compare", 
                 font=('Helvetica', 14, 'bold')).pack()
        ttk.Label(compare_frame, text="Compare two ReqIF files\nor folders side-by-side", 
                 font=('Helvetica', 10), justify=tk.CENTER).pack(pady=(5, 15))
        
        compare_btn = ttk.Button(compare_frame, text="Open Compare Tool", 
                               command=self.open_compare_tool, style="Accent.TButton")
        compare_btn.pack(pady=(0, 20), padx=20)
        
        # Visualize button with icon-like styling
        visualize_frame = ttk.Frame(button_frame, relief='raised', borderwidth=2)
        visualize_frame.grid(row=0, column=1, padx=20, pady=10)
        
        ttk.Label(visualize_frame, text="📋", font=('Helvetica', 40)).pack(pady=(20, 10))
        ttk.Label(visualize_frame, text="ReqIF Visualizer", 
                 font=('Helvetica', 14, 'bold')).pack()
        ttk.Label(visualize_frame, text="View and analyze ReqIF\nfiles in Excel-like format", 
                 font=('Helvetica', 10), justify=tk.CENTER).pack(pady=(5, 15))
        
        visualize_btn = ttk.Button(visualize_frame, text="Open Visualizer", 
                                 command=self.open_visualizer, style="Accent.TButton")
        visualize_btn.pack(pady=(0, 20), padx=20)
        
        # Version info
        version_label = ttk.Label(main_frame, text="Version 2.0 - Enhanced with Visualization", 
                                 font=('Helvetica', 9), foreground='gray')
        version_label.grid(row=3, column=0, pady=(40, 0))
    
    def open_compare_tool(self):
        """Open the ReqIF comparison tool"""
        ReqIFComparisonGUI(self.root, self.setup_main_menu)
    
    def open_visualizer(self):
        """Open the ReqIF visualizer"""
        ReqIFVisualizerGUI(self.root, self.setup_main_menu)

class ReqIFComparisonGUI:
    """Main GUI application for ReqIF comparison"""
    
    def __init__(self, parent_window, back_callback):
        self.parent_window = parent_window
        self.back_callback = back_callback
        
        self.comparator = ReqIFComparator()
        self.comparison_result = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Clear parent window
        for widget in self.parent_window.winfo_children():
            widget.destroy()
        
        self.parent_window.title("ReqIF Comparison Tool")
        
        # Main frame
        main_frame = ttk.Frame(self.parent_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.parent_window.columnconfigure(0, weight=1)
        self.parent_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Back button
        ttk.Button(main_frame, text="← Back to Main Menu", 
                  command=self.back_callback).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # File/Folder selection frame
        selection_frame = ttk.LabelFrame(main_frame, text="Select Files or Folders", padding="5")
        selection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
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
            self.parent_window.config(cursor="wait")
            self.parent_window.update()
            
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
            self.parent_window.config(cursor="")
    
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

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = MainMenuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()