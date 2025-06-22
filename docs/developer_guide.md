# ReqIF Tool Suite - Developer Guide

Technical documentation for developers working with the ReqIF Tool Suite.

## 🏗️ Architecture Overview

### Core Components
```
ReqIFParser → ReqIFComparator → GUI Components
     ↓              ↓                ↓
Namespace      Difference      Theme Manager
Handling       Analysis        & Visualization
```

### Key Classes
- **`ReqIFParser`**: Enhanced parser with namespace awareness
- **`ReqIFComparator`**: File comparison and change detection  
- **`ComparisonResultsGUI`**: Results visualization interface
- **`VisualizerGUI`**: Single-file exploration interface
- **`ThemeManager`**: Professional UI theming system

## 🔧 Parser Implementation

### Enhanced Features
The current parser addresses specific ReqIF challenges:

**Namespace Handling:**
```python
# Robust element discovery with fallback strategies
def _find_elements_namespace_aware(self, parent, element_name):
    # Strategy 1: Full namespace URI
    # Strategy 2: XPath with registered namespace  
    # Strategy 3: Pattern matching (fallback)
    # Strategy 4: Case insensitive (last resort)
```

**Content Extraction:**
```python
# Multi-strategy content extraction
def _extract_content_enhanced(self, attr_value_elem, value_type):
    if 'STRING' in value_type:
        return self._extract_string_content_enhanced(attr_value_elem)
    elif 'XHTML' in value_type:
        return self._extract_xhtml_content_enhanced(attr_value_elem)
    # ... handles all ReqIF value types
```

### Parser API

**Basic Usage:**
```python
from reqif_parser import ReqIFParser

parser = ReqIFParser()
requirements = parser.parse_file("file.reqif")

# Each requirement is a dictionary:
{
    'id': 'unique_identifier',
    'title': 'human_readable_title', 
    'description': 'detailed_description',
    'type': 'requirement_type',
    'attributes': {'attr_name': 'attr_value', ...},
    'raw_attributes': {'attr_ref': 'raw_value', ...}
}
```

**Advanced Usage:**
```python
# Get detailed file information
file_info = parser.get_file_info("file.reqif")
print(f"Found {file_info['requirement_count']} requirements")

# Get parsing diagnostics
debug_info = parser.get_debug_info()
print(f"Namespace: {debug_info['namespace_info']['namespace_uri']}")
```

## 🔍 Comparison System

### Comparison Algorithm
```python
# Three-way categorization
results = comparator.compare_requirements(file1_reqs, file2_reqs)

# Returns structured results:
{
    'added': [...],      # Requirements only in file2
    'deleted': [...],    # Requirements only in file1  
    'modified': [...],   # Requirements changed between files
    'unchanged': [...],  # Requirements identical in both
    'statistics': {...}  # Summary metrics
}
```

### Change Detection
The comparator identifies changes at multiple levels:
- **Requirement level**: Added/deleted requirements
- **Field level**: Title, description, type changes
- **Attribute level**: Individual attribute modifications

## 🎨 GUI Architecture

### Component Structure
```
main.py
├── ReqIFToolMVP (main application)
├── ThemeManager (styling system)
├── ComparisonResultsGUI (results display)
└── VisualizerGUI (single file explorer)
```

### Theme System
Professional theming with three built-in themes:
```python
themes = {
    "light": {name: "Light Professional", colors: {...}},
    "dark": {name: "Dark Professional", colors: {...}}, 
    "blue": {name: "Professional Blue", colors: {...}}
}
```

**Custom themes:**
```python
# Extend ThemeManager for custom themes
theme_manager.themes["custom"] = {
    "name": "Custom Theme",
    "bg": "#FFFFFF", 
    "fg": "#000000",
    # ... other color definitions
}
```

## 🛠️ Development Tools

### Diagnostic Tool
**Location:** `dev_tools/reqif_diagnostics.py`

**Usage:**
```bash
python dev_tools/reqif_diagnostics.py your_file.reqif
```

**Output:** Comprehensive analysis of:
- File structure and XML validity
- Namespace detection and handling
- Element discovery success rates
- Content extraction testing
- Reference resolution analysis

### Legacy Parsers
**Location:** `dev_tools/legacy/`

Contains previous parser iterations for reference:
- `reqif_parser_original_backup.py`: Original implementation
- `targeted_reqif_parser.py`: Development version with full test suite
- `reqif_parser_improved.py`: Intermediate improvement attempt

## 🧪 Testing and Validation

### Parser Testing
```python
# Test parser with diagnostics
from dev_tools.reqif_diagnostics import ReqIFDiagnostics

diagnostics = ReqIFDiagnostics() 
findings = diagnostics.analyze_file("test_file.reqif")

# Check quality metrics
if findings['parsing_attempts']['definitions_found'] > 10:
    print("✅ Good definition discovery")
```

### Quality Metrics
The parser tracks several quality indicators:
- **Resolution success rate**: % of requirements fully processed
- **Content extraction count**: Number of attribute values extracted
- **Definition catalog size**: Number of attribute definitions found
- **Reference resolution**: Success rate of ID → human-readable mapping

## 🔧 Customization and Extension

### Adding New Value Types
```python
# In ReqIFParser class, add to _extract_content_enhanced:
elif 'CUSTOM-TYPE' in value_type:
    return self._extract_custom_content(attr_value_elem)

def _extract_custom_content(self, elem):
    # Custom extraction logic
    return custom_value
```

### Custom Field Mapping
```python
# Modify _smart_field_mapping in ReqIFParser:
field_keywords = {
    'priority': ['priority', 'importance', 'your_custom_field'],
    'custom_field': ['custom', 'special', 'unique']
}
```

### GUI Extensions
```python
# Add custom tabs to main notebook
custom_frame = ttk.Frame(self.notebook)
self.notebook.add(custom_frame, text="🔧 Custom Tool")
# Add your custom interface
```

## 📊 Performance Considerations

### File Size Limits
- **Recommended**: < 50MB for optimal performance
- **Maximum tested**: 100MB+ files work but slower
- **Memory usage**: ~5x file size during processing

### Optimization Tips
```python
# For large files, consider:
# 1. Progress indicators for user feedback
# 2. Chunked processing for memory efficiency  
# 3. Background threading for GUI responsiveness
```

## 🚨 Error Handling

### Parser Errors
```python
try:
    requirements = parser.parse_file("file.reqif")
except FileNotFoundError:
    # Handle missing file
except ValueError as e:
    # Handle invalid XML or ReqIF structure
except RuntimeError as e:
    # Handle parsing failures
```

### GUI Error Recovery
- **ErrorHandler**: Global exception handling and logging
- **StartupValidator**: System requirement validation
- **Safe mode**: Fallback GUI with basic functionality

## 🔗 API Reference

### ReqIFParser Methods
```python
parse_file(file_path: str) -> List[Dict[str, Any]]
get_file_info(file_path: str) -> Dict[str, Any]  
get_debug_info() -> Dict[str, Any]
```

### ReqIFComparator Methods
```python
compare_requirements(file1_reqs: List, file2_reqs: List) -> Dict
get_text_diff(text1: str, text2: str) -> List[str]
export_comparison_summary(results: Dict) -> str
```

### ThemeManager Methods
```python
apply_theme(theme_name: str = None)
toggle_theme()
get_available_themes() -> List[Tuple[str, str]]
```

## 📈 Future Enhancements

### Planned Features
- **Plugin system**: Custom parser extensions
- **Batch processing**: Multiple file operations
- **Advanced filtering**: Complex requirement queries
- **Report generation**: Automated documentation

### Extension Points
- **Parser plugins**: New ReqIF variant support
- **Export formats**: Additional output formats
- **Visualization**: Custom chart types
- **Integration**: API for external tools

---

**Development Environment:** Python 3.7+, tkinter, built-in libraries only
**Architecture:** Modular design with clear separation of concerns
**Testing:** Diagnostic tools and quality metrics for validation