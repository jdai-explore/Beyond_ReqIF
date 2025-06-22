# ReqIF Tool Suite - User Guide

Complete guide for using the ReqIF Tool Suite for requirements analysis and comparison.

## 🚀 Getting Started

### Launch the Application
```bash
python run_reqif_tool.py
```

The welcome screen offers startup options:
- **Normal startup** (recommended)
- **Run validation first** (if having issues)
- **Safe mode** (basic features only)

## 📊 Main Interface

The application has two main tabs:

### 🔄 Compare Files Tab
Compare two ReqIF files to analyze changes.

**Steps:**
1. **Select File 1** (original): Click "Browse" or drag-and-drop
2. **Select File 2** (modified): Click "Browse" or drag-and-drop  
3. **Click "Compare Files"**: Analysis runs automatically
4. **View Results**: New window shows detailed comparison

**Results Window:**
- **Summary Statistics**: Overview of changes
- **Added Tab**: New requirements in File 2
- **Deleted Tab**: Requirements removed from File 1
- **Modified Tab**: Changed requirements with details
- **Unchanged Tab**: Requirements that stayed the same

### 📈 Visualize File Tab
Explore a single ReqIF file in detail.

**Steps:**
1. **Select ReqIF File**: Click "Browse" or drag-and-drop
2. **Click "Load & Visualize"**: File analysis begins
3. **Explore Data**: Use the visualization interface

**Visualization Features:**
- **Requirements Table**: All requirements with intelligent column selection
- **Search & Filter**: Real-time search across all content
- **Statistics Tab**: Data quality analysis and metrics
- **Export**: Save filtered results to CSV

## 🔍 Search and Navigation

### Search Features
- **Real-time search**: Type in search box for instant filtering
- **Cross-field search**: Searches titles, descriptions, and all attributes
- **Clear search**: Click ❌ or press Escape

### Content Quality Indicators
- **✅ Good content quality**: Meaningful titles and descriptions
- **⚠️ Minor issues**: Some content needs improvement
- **❌ Content issues**: Significant parsing problems

## 💾 Export Options

### From Comparison Results
- **Export Results to CSV**: All changes with categorization
- **Export Summary**: Text summary of comparison statistics

### From Visualization
- **Export CSV**: Current filtered view with all attributes
- **Custom filename**: Automatically suggests meaningful names

## ⚙️ Settings and Themes

### Theme Options
- **Light Professional**: Clean, traditional interface
- **Dark Professional**: Modern dark mode
- **Professional Blue**: Corporate blue theme

**Change themes:**
- Click 🌓 button in header
- Use View menu → Themes
- Keyboard shortcut: Ctrl+T

### File Format Support
- **.reqif files**: Direct ReqIF XML files
- **.reqifz files**: ReqIF ZIP archives (automatically extracted)

## 🎯 Best Practices

### File Preparation
- **Large files**: Files up to 100MB are supported
- **Archive files**: .reqifz files are automatically handled
- **File naming**: Use descriptive names for easy identification

### Comparison Workflow
1. **Baseline first**: Use older version as File 1
2. **Changes second**: Use newer version as File 2
3. **Review systematically**: Check each change category
4. **Export results**: Save comparison for documentation

### Visualization Workflow
1. **Start with statistics**: Review data quality first
2. **Use search**: Filter to specific requirements
3. **Double-click details**: View full requirement information
4. **Export filtered data**: Save relevant subsets

## 🔧 Troubleshooting

### Common Issues

**No requirements found:**
- Check file format (.reqif or .reqifz)
- Verify file is not corrupted
- Run diagnostics: `python dev_tools/reqif_diagnostics.py your_file.reqif`

**Poor content quality:**
- Some ReqIF files have complex structures
- Check Statistics tab for specific issues
- Content still accessible in raw attributes

**Slow performance:**
- Large files (>50MB) may take time to process
- Use search to filter results
- Consider splitting very large files

### Error Recovery
- **Application freezes**: Force quit and restart
- **Parsing fails**: Check file with diagnostic tool
- **GUI issues**: Try safe mode: `python run_reqif_tool.py --safe-mode`

## 📱 Keyboard Shortcuts

### File Operations
- **Ctrl+O**: Open File 1
- **Ctrl+Shift+O**: Open File 2
- **Ctrl+R**: Clear file selections

### Actions
- **F5**: Start comparison
- **F6**: Load visualization
- **Ctrl+F**: Focus search box
- **Esc**: Clear search / Cancel

### Interface
- **Ctrl+T**: Toggle theme
- **Ctrl+1**: Compare tab
- **Ctrl+2**: Visualize tab
- **F1**: About dialog

## 💡 Tips and Tricks

### Efficient Comparison
- **Use filters**: Export specific change types only
- **Check modified details**: Double-click for change breakdown
- **Save summaries**: Text summaries good for reports

### Effective Visualization  
- **Sort intelligently**: Click column headers to sort
- **Search strategically**: Use specific terms for better results
- **Export filtered views**: Get exactly what you need

### Data Quality
- **Review statistics first**: Understand parsing quality
- **Check sample content**: Verify extraction accuracy
- **Use raw attributes**: Fallback if mapped fields incomplete

---

**Need help?** Check the Developer Guide for technical details or run the diagnostic tool for file-specific issues.