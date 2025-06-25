# Beyond ReqIF - Native Edition

Professional ReqIF (Requirements Interchange Format) file parser, comparison, and visualization tool with pure native tkinter interface.

## ✨ Features

- **Parse ReqIF files** (.reqif and .reqifz archives) with enhanced content extraction
- **Compare requirements** between two files with detailed change analysis
- **Visualize data** with intelligent content prioritization and search
- **Native GUI** - Pure tkinter interface with no external dependencies
- **Export results** to CSV for further analysis
- **Cross-platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start

```bash
# Launch the application
python run_reqif_tool.py

# Or run directly
python main.py
```

## 🛠️ System Requirements

- **Python 3.7+**
- **tkinter** (usually included with Python)
- **Built-in libraries only** - no external dependencies required

## 🎯 Usage

### Compare Files
1. Launch app → **Compare Files** tab
2. Select original and modified ReqIF files
3. Click **Compare** → View categorized results
4. Double-click modified requirements for detailed differences
5. Export results to CSV

### Analyze Single File
1. Launch app → **Analyze File** tab
2. Select ReqIF file → Click **Analyze**
3. Use search/filter to explore requirements
4. View statistics and export filtered data

## 📱 Key Features

- **Real-time search** across all requirement content
- **Side-by-side diff viewer** for modified requirements
- **Intelligent column selection** showing most relevant data
- **Statistics dashboard** with data quality metrics
- **Multiple themes** (Light, Dark, Professional Blue)
- **Keyboard shortcuts** for efficient navigation

## 🔧 Troubleshooting

**No requirements found:**
- Check file format (.reqif or .reqifz)
- Run diagnostics: `python dev_tools/reqif_diagnostics.py your_file.reqif`

**Application issues:**
- Try safe mode: `python run_reqif_tool.py --safe-mode`
- Run validation: `python run_reqif_tool.py --validate`

## 📊 For Developers

### Core Components
- `reqif_parser.py` - Enhanced ReqIF parsing with namespace handling
- `reqif_comparator.py` - Three-way comparison (added/deleted/modified/unchanged)
- `main.py` - Native tkinter GUI application
- `comparison_gui.py` - Results visualization with diff viewer
- `visualizer_gui.py` - Single file analysis interface

### Parser API
```python
from reqif_parser import ReqIFParser

parser = ReqIFParser()
requirements = parser.parse_file("file.reqif")
# Returns list of requirement dictionaries with id, title, description, etc.
```

### Comparison API
```python
from reqif_comparator import ReqIFComparator

comparator = ReqIFComparator()
results = comparator.compare_requirements(file1_reqs, file2_reqs)
# Returns dict with 'added', 'deleted', 'modified', 'unchanged', 'statistics'
```

## 🔍 Advanced Features

- **Namespace-aware parsing** with fallback strategies
- **XHTML content extraction** for rich text requirements
- **Reference resolution** converting IDs to human-readable names
- **Quality metrics** tracking parsing success rates
- **Fuzzy file matching** for folder comparisons

## 📄 License

Developed for professional ReqIF file processing and analysis with native Python tools.

---

**Platform Support**: Windows, macOS, Linux