# ReqIF Tool Suite

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)]()

A comprehensive, professional-grade tool suite for working with ReqIF (Requirements Interchange Format) files. Provides powerful comparison, visualization, and analysis capabilities with an intuitive graphical user interface.

![ReqIF Tool Suite Screenshot](docs/images/main_interface.png)

## 🎯 **Features**

### **📊 ReqIF Comparison Tool**
- **Side-by-side comparison** of ReqIF files and entire folders
- **Advanced diff highlighting** with color-coded changes (added/modified/deleted)
- **Intelligent requirement matching** by ID and content similarity
- **Comprehensive statistics** showing change summaries
- **Bulk folder comparison** for managing large requirement sets
- **Export comparison results** in multiple formats

### **📋 ReqIF Visualizer**
- **Excel-like table view** for easy requirement browsing
- **Detailed requirement inspection** with full text and attributes
- **Advanced search and filtering** capabilities
- **Statistical analysis** with distribution charts and metrics
- **Interactive requirement exploration** with double-click details
- **Export to CSV/Excel** for external analysis

### **🔍 Advanced Analytics**
- **Requirement distribution analysis** by type, status, priority
- **Text complexity metrics** and readability analysis
- **Attribute completeness reporting**
- **Trend analysis** across requirement versions
- **Custom metrics** through plugin system

### **💾 Multiple Export Formats**
- **CSV Export**: Spreadsheet-compatible format
- **Excel Export**: Rich formatting with multiple sheets
- **PDF Reports**: Professional documentation
- **JSON Export**: API-friendly structured data

## 🚀 **Quick Start**

### **Installation**

#### **Option 1: Download Executable (Recommended for End Users)**
1. Download the latest release from [Releases](https://github.com/your-org/reqif-tool-suite/releases)
2. Extract the ZIP file
3. Run `ReqIFToolSuite.exe` (Windows) or `ReqIFToolSuite` (macOS/Linux)

#### **Option 2: Install from Source (For Developers)**
```bash
# Clone the repository
git clone https://github.com/your-org/reqif-tool-suite.git
cd reqif-tool-suite

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### **Option 3: Install via pip (Coming Soon)**
```bash
pip install reqif-tool-suite
reqif-tool-suite
```

### **First Usage**

1. **Launch the application**
2. **Choose your tool**:
   - Click **"ReqIF Compare"** to compare two files or folders
   - Click **"ReqIF Visualizer"** to explore a single ReqIF file
3. **Load your files** using the browse buttons
4. **Explore the results** in the tabbed interface
5. **Export your findings** using the export buttons

## 📁 **Supported File Formats**

| Format | Extension | Support Level |
|--------|-----------|---------------|
| ReqIF | `.reqif` | ✅ Full Support |
| ReqIF Archive | `.reqifz` | ✅ Full Support |
| CSV Export | `.csv` | ✅ Export Only |
| Excel Export | `.xlsx` | ✅ Export Only |
| PDF Reports | `.pdf` | ✅ Export Only |
| JSON Data | `.json` | ✅ Export Only |

## 🖥️ **System Requirements**

### **Minimum Requirements**
- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher (if running from source)
- **RAM**: 4 GB
- **Storage**: 100 MB free space

### **Recommended Requirements**
- **OS**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **RAM**: 8 GB or more
- **Storage**: 500 MB free space (for large file processing)

## 📖 **User Guide**

### **Comparing ReqIF Files**

1. **Select Comparison Mode**: Click "ReqIF Compare" from the main menu
2. **Choose Files**: Use "Browse File" for single files or "Browse Folder" for entire directories
3. **Run Comparison**: Click "Compare" to analyze differences
4. **Review Results**: Explore the tabbed results:
   - **Added**: Requirements present only in the second file
   - **Modified**: Requirements that changed between files
   - **Deleted**: Requirements present only in the first file
   - **Unchanged**: Requirements that are identical
5. **Export Results**: Use "Export Results" to save findings

### **Visualizing ReqIF Files**

1. **Select Visualizer Mode**: Click "ReqIF Visualizer" from the main menu
2. **Load File**: Browse and select a ReqIF file, then click "Load"
3. **Explore Views**:
   - **Table View**: Excel-like browsing with search functionality
   - **Details View**: Complete requirement information
   - **Statistics**: Analytical insights and distributions
4. **Search & Filter**: Use the search box to find specific requirements
5. **Export Data**: Use "Export to CSV" for external analysis

## 🔧 **Advanced Configuration**

### **Configuration File**
The application stores settings in `config/user_config.json`:

```json
{
  "window": {
    "width": 1200,
    "height": 800,
    "remember_position": true
  },
  "theme": "default",
  "export": {
    "default_format": "csv",
    "include_timestamps": true
  },
  "comparison": {
    "ignore_whitespace": false,
    "case_sensitive": true
  }
}
```

### **Logging**
Logs are stored in the `logs/` directory:
- `app.log`: General application logs
- `error.log`: Error-specific logs
- `debug.log`: Detailed debugging information (when enabled)

## 🛠️ **Development**

### **Project Structure**
```
reqif_tool_suite/
├── main.py                    # Application entry point
├── core/                      # Business logic
│   ├── reqif_parser.py       # ReqIF parsing
│   ├── reqif_comparator.py   # Comparison algorithms
│   └── reqif_analyzer.py     # Statistical analysis
├── gui/                       # User interface
│   ├── main_menu.py          # Main application menu
│   ├── comparison_gui.py     # Comparison interface
│   └── visualizer_gui.py     # Visualization interface
├── utils/                     # Utilities
├── exporters/                 # Export functionality
├── models/                    # Data models
├── plugins/                   # Plugin system
└── tests/                     # Test suite
```

### **Setting Up Development Environment**

```bash
# Clone and setup
git clone https://github.com/your-org/reqif-tool-suite.git
cd reqif-tool-suite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run the application in development mode
python main.py --debug
```

### **Running Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=gui --cov=utils

# Run specific test categories
pytest tests/test_core/        # Core functionality tests
pytest tests/test_gui/         # GUI tests
pytest tests/test_integration/ # Integration tests
```

### **Building Executables**

```bash
# Install build dependencies
pip install pyinstaller

# Build for current platform
python build.py

# Build for multiple platforms (requires Docker)
python build.py --all-platforms
```

## 🔌 **Plugin System**

The ReqIF Tool Suite supports custom plugins for extending functionality:

### **Creating a Custom Parser Plugin**
```python
from plugins.base_plugin import BasePlugin

class CustomParserPlugin(BasePlugin):
    name = "Custom Format Parser"
    version = "1.0.0"
    
    def parse_file(self, file_path):
        # Your custom parsing logic
        pass
```

### **Available Plugin Types**
- **Parsers**: Support for additional file formats
- **Exporters**: Custom export formats
- **Analyzers**: Additional statistical analysis
- **Themes**: Custom visual themes

## 📊 **Performance**

### **Benchmarks**
| File Size | Requirements | Load Time | Memory Usage |
|-----------|--------------|-----------|--------------|
| Small     | < 100        | < 1s      | < 50 MB      |
| Medium    | 100-1,000    | 1-5s      | 50-200 MB    |
| Large     | 1,000-10,000 | 5-30s     | 200-500 MB   |
| Very Large| 10,000+      | 30s+      | 500 MB+      |

### **Optimization Tips**
- **Use folder comparison** for bulk analysis instead of individual files
- **Enable caching** in settings for repeated comparisons
- **Close unused tabs** to free memory
- **Export large datasets** in chunks for better performance

## 🤝 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Areas for Contribution**
- 🐛 **Bug Reports**: Found an issue? Please report it!
- 💡 **Feature Requests**: Have an idea? We'd love to hear it!
- 🔧 **Code Contributions**: Pull requests welcome!
- 📖 **Documentation**: Help improve our docs
- 🎨 **UI/UX**: Design improvements and themes
- 🧪 **Testing**: Help us test edge cases

### **Development Workflow**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to your branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

### **Getting Help**
- 📖 **Documentation**: Check our [User Guide](docs/user_guide.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/reqif-tool-suite/discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-org/reqif-tool-suite/issues)
- 📧 **Email Support**: support@reqif-tools.com

### **FAQ**

**Q: What is ReqIF?**
A: ReqIF (Requirements Interchange Format) is an international standard for exchanging requirements between different tools and organizations.

**Q: Can I compare files from different ReqIF tools?**
A: Yes! The tool is designed to work with ReqIF files from any compliant tool (DOORS, PTC, Siemens, etc.).

**Q: Is my data secure?**
A: Yes. The tool works entirely offline - your files never leave your computer.

**Q: Can I automate comparisons?**
A: Yes, we provide a command-line interface for batch operations. See [CLI Documentation](docs/cli_guide.md).

## 🗺️ **Roadmap**

### **Version 2.1 (Q2 2024)**
- [ ] Command-line interface for automation
- [ ] Advanced filtering and search
- [ ] Custom requirement attributes
- [ ] Performance optimizations

### **Version 2.2 (Q3 2024)**
- [ ] Database storage support
- [ ] Version control integration (Git)
- [ ] Collaborative features
- [ ] Web-based interface

### **Version 3.0 (Q4 2024)**
- [ ] AI-powered requirement analysis
- [ ] Natural language processing
- [ ] Integration with ALM tools
- [ ] Cloud synchronization

## 🏆 **Acknowledgments**

- **ReqIF Standard**: [Object Management Group (OMG)](https://www.omg.org/)
- **Python Community**: For excellent libraries and tools
- **Contributors**: All our amazing contributors and testers
- **Users**: Thank you for your feedback and support!

---

<div align="center">

**Made with ❤️ for the Requirements Engineering Community**

[Website](https://reqif-tools.com) • [Documentation](docs/) • [Support](mailto:support@reqif-tools.com) • [Contributing](CONTRIBUTING.md)

</div>