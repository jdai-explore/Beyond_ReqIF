# Beyond ReqIF

Professional ReqIF (Requirements Interchange Format) file parser, comparison, and visualization tool.

## ✨ Features

- **Parse ReqIF files** (.reqif and .reqifz archives) with enhanced content extraction
- **Compare requirements** between two files with detailed change analysis
- **Visualize data** with intelligent content prioritization and search
- **Professional UI** with light/dark themes and modern interface
- **Export results** to CSV for further analysis
- **Robust parsing** handles complex namespace structures and XHTML content

## 🚀 Quick Start

```bash
# Launch the application
python run_reqif_tool.py

# Or run directly
python main.py
```

## 📊 Parsing Performance

- **High accuracy**: 70%+ quality scores on complex ReqIF files
- **Comprehensive extraction**: Handles STRING, XHTML, and ENUMERATION values
- **Namespace aware**: Works with full URI namespaces
- **Large file support**: Tested with 20MB+ files and 400+ requirements

## 🛠️ System Requirements

- **Python 3.7+**
- **tkinter** (usually included with Python)
- **Built-in libraries only** - no external dependencies required

## 📁 Project Structure

```
reqif_tool_suite/
├── main.py                 # Main application
├── reqif_parser.py        # Enhanced ReqIF parser
├── reqif_comparator.py    # File comparison logic
├── *_gui.py              # User interface components
├── run_reqif_tool.py     # Application launcher
├── dev_tools/            # Development and debugging tools
└── docs/                 # Documentation
```

## 🎯 Quick Usage

1. **Parse single file**: Use Visualize tab to explore requirements
2. **Compare files**: Use Compare tab to analyze changes between versions
3. **Export data**: Click export buttons to save results as CSV
4. **Troubleshoot**: Use `dev_tools/reqif_diagnostics.py` for file analysis

## 📚 Documentation

- **User Guide**: `docs/user_guide.md` - End-user instructions
- **Developer Guide**: `docs/developer_guide.md` - Technical details and API reference

## 🔧 Troubleshooting

If you encounter parsing issues:
```bash
# Run diagnostics on your file
python dev_tools/reqif_diagnostics.py your_file.reqif
```

## 🤝 Contributing

This tool was developed through systematic analysis and iterative improvement. The diagnostic tools in `dev_tools/` can help analyze new ReqIF file variants.

## 📄 License

Developed for professional ReqIF file processing and analysis.

---

**Current Status**: Production ready with enhanced parsing for complex ReqIF structures