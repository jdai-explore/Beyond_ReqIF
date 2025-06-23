# Beyond ReqIF - Native Edition

Professional ReqIF (Requirements Interchange Format) file parser, comparison, and visualization tool with pure native tkinter interface.

## ✨ Features

- **Parse ReqIF files** (.reqif and .reqifz archives) with enhanced content extraction
- **Compare requirements** between two files with detailed change analysis
- **Visualize data** with intelligent content prioritization and search
- **Native GUI** - Pure tkinter interface with no external dependencies
- **Export results** to CSV for further analysis
- **Robust parsing** handles complex namespace structures and XHTML content
- **Cross-platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start

```bash
# Launch the application
python run_reqif_tool.py

# Or run directly
python main.py
```

## 📊 Native Interface

**Pure tkinter design:**
- No external theme dependencies
- Native look and feel on all platforms
- Consistent behavior across operating systems
- Lightweight and fast startup

**Key interface features:**
- Tabbed interface for compare and analyze functions
- Intelligent column selection in data views
- Real-time search and filtering
- Side-by-side diff viewer for changes
- Export capabilities for all views

## 🛠️ System Requirements

- **Python 3.7+**
- **tkinter** (usually included with Python)
- **Built-in libraries only** - no external dependencies required

## 📁 Project Structure

```
reqif_tool_suite/
├── main.py                 # Main application (native GUI)
├── reqif_parser.py        # Enhanced ReqIF parser
├── reqif_comparator.py    # File comparison logic
├── comparison_gui.py      # Comparison results interface (native)
├── visualizer_gui.py      # Single file explorer (native)
├── error_handler.py       # Error handling and logging
├── run_reqif_tool.py     # Native application launcher
├── dev_tools/            # Development and debugging tools
└── docs/                 # Documentation
```

## 🎯 Quick Usage

### Compare Files
1. **Launch app**: Run `python run_reqif_tool.py`
2. **Compare tab**: Select two ReqIF files (original and modified)
3. **Click Compare**: View categorized results (added, deleted, modified, unchanged)
4. **View differences**: Double-click modified requirements for detailed diff view
5. **Export results**: Save comparison results to CSV

### Analyze Single File
1. **Analyze tab**: Select a single ReqIF file
2. **Click Analyze**: Explore requirements in intelligent table view
3. **Search and filter**: Use real-time search to find specific requirements
4. **View statistics**: Check data quality and content metrics
5. **Export data**: Save filtered results to CSV

## 📚 Interface Guide

### Main Window
- **Compare Files Tab**: Side-by-side file comparison
- **Analyze File Tab**: Single file exploration and analysis
- **Status Bar**: Shows current operation status and progress

### Comparison Results
- **Summary Statistics**: Overview with colored indicators
- **Added Requirements**: New requirements in second file (green)
- **Deleted Requirements**: Requirements removed from first file (red)
- **Modified Requirements**: Changed requirements with diff viewer (orange)
- **Unchanged Requirements**: Identical requirements (blue)

### Diff Viewer
- **Field Selector**: Choose which field to compare
- **Side-by-side View**: Original vs Modified content
- **Syntax Highlighting**: Visual indicators for changes
- **Navigation**: Previous/Next buttons for easy browsing
- **Export Options**: Save diff reports and copy content

### File Analysis
- **Intelligent Columns**: Automatically shows most relevant data
- **Real-time Search**: Filter across all content instantly
- **Statistics View**: Data quality metrics and type analysis
- **Detail View**: Double-click any requirement for full details

## 🔧 Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Run validation
python run_reqif_tool.py --validate

# Try safe mode
python run_reqif_tool.py --safe-mode
```

**No requirements found:**
- Verify file format (.reqif or .reqifz)
- Check file isn't corrupted
- Run diagnostics: `python dev_tools/reqif_diagnostics.py your_file.reqif`

**Poor parsing quality:**
- Check Statistics tab for parsing metrics
- Complex ReqIF structures may have lower extraction rates
- Raw attributes still accessible even if field mapping incomplete

### Performance Tips
- **Large files (>50MB)**: May take time to process, use search to filter results
- **Memory usage**: Approximately 5x file size during processing
- **Export optimization**: Filter data before export for faster CSV generation

## 📱 Keyboard Shortcuts

### Global
- **F1**: About/Help information
- **Ctrl+1**: Switch to Compare Files tab
- **Ctrl+2**: Switch to Analyze File tab
- **Escape**: Clear search filters

### File Operations
- **Ctrl+O**: Open first file (Compare tab)
- **Ctrl+Shift+O**: Open second file (Compare tab)
- **Ctrl+L**: Load file (Analyze tab)

### Actions
- **F5**: Start comparison
- **F6**: Start analysis
- **Ctrl+F**: Focus search box
- **Ctrl+E**: Export current view

## 💡 Features Detail

### Enhanced Parsing
- **Namespace-aware**: Handles full URI namespaces and fallback strategies
- **Content extraction**: Supports STRING, XHTML, ENUMERATION, and numeric types
- **Reference resolution**: Converts IDs to human-readable names
- **Quality metrics**: Tracks parsing success rates and content extraction

### Smart Comparison
- **Three-way analysis**: Categorizes all changes comprehensively
- **Field-level tracking**: Identifies exactly what changed in each requirement
- **Attribute comparison**: Includes all custom attributes in comparison
- **Change summaries**: Provides quick overview of modification types

### Intelligent Visualization
- **Adaptive columns**: Shows most relevant data automatically
- **Content prioritization**: Highlights high-quality content
- **Search optimization**: Searches across all fields and attributes
- **Export flexibility**: Includes all data in exports, not just visible columns

## 🔍 Advanced Usage

### Command Line Options
```bash
# Normal startup with GUI dialog
python run_reqif_tool.py

# Direct normal startup
python run_reqif_tool.py --normal

# Run system validation first
python run_reqif_tool.py --validate

# Start in safe mode
python run_reqif_tool.py --safe-mode

# Show help
python run_reqif_tool.py --help
```

### Development Tools
```bash
# Analyze specific ReqIF file structure
python dev_tools/reqif_diagnostics.py your_file.reqif

# Check parsing quality and namespace handling
python dev_tools/reqif_diagnostics.py --verbose your_file.reqif
```

## 🤝 Contributing

This native edition focuses on:
- **Pure tkinter implementation** - No external GUI dependencies
- **Cross-platform compatibility** - Consistent behavior everywhere
- **Performance optimization** - Fast startup and responsive interface
- **Accessibility** - Clear visual design and keyboard navigation

## 📄 License

Developed for professional ReqIF file processing and analysis with native Python tools.

---

**Current Status**: Production ready native edition with enhanced parsing and pure tkinter interface

**Platform Support**: Windows, macOS, Linux - no platform-specific dependencies