# ReqIF Tool Suite MVP

A simple but powerful tool for comparing ReqIF (Requirements Interchange Format) files with an intuitive GUI interface.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- No additional dependencies required (uses built-in libraries only!)

### Installation & Running

```bash
# Clone or download the project files
# Navigate to the project directory
cd reqif_mvp

# Run the application
python main.py
```

## 📋 Features

### ✅ Current MVP Features
- **Dual File Comparison**: Compare two ReqIF files side-by-side
- **Automatic Change Detection**: Identifies added, deleted, and modified requirements
- **Categorized Results**: Organized tabs for different change types
- **Detailed View**: Double-click any requirement for full details
- **Summary Statistics**: Overview of all changes with percentages
- **CSV Export**: Export comparison results for further analysis
- **Error Handling**: Graceful handling of parsing errors and invalid files

### 🔍 Comparison Categories
- **Added**: Requirements present only in the second file (green highlighting)
- **Deleted**: Requirements present only in the first file (red highlighting)  
- **Modified**: Requirements that changed between files (yellow highlighting)
- **Unchanged**: Requirements identical in both files

## 🖥️ User Interface

### Main Window
- File selection for two ReqIF files
- Compare button to start analysis
- Status area showing progress and results
- Menu with additional options

### Results Window
- **Tabbed Interface**:
  - Added tab: New requirements in the second file
  - Deleted tab: Requirements removed from the first file
  - Modified tab: Requirements with changes between files
  - Unchanged tab: Requirements that are identical
- **Summary Statistics Panel**: Counts and percentages for each category
- **Double-click Details**: View full requirement information
- **Export Options**: Save results to CSV or summary to text file

## 📁 Project Structure

```
reqif_mvp/
├── main.py                 # Main application entry point
├── reqif_parser.py         # ReqIF XML parsing logic
├── reqif_comparator.py     # Comparison algorithms
├── comparison_gui.py       # Results display interface
├── requirements.txt        # Python dependencies (minimal)
└── README.md              # This documentation
```

## 🔧 Technical Details

### Architecture
- **Parser Module**: Handles ReqIF XML structure and extracts requirements
- **Comparator Module**: Implements comparison logic and change detection
- **GUI Modules**: Provides user interface using tkinter
- **Export System**: CSV and text export functionality

### ReqIF Support
- Parses standard ReqIF XML structure (.reqif files)
- Extracts and processes ReqIF ZIP archives (.reqifz files)
- Handles single or multiple ReqIF files within archives
- Extracts requirement ID, title, description, type, and attributes
- Handles SPEC-OBJECT elements and attribute values
- Supports both namespaced and non-namespaced XML
- Graceful fallback for non-standard ReqIF structures
- Automatic temporary file management for archives

### Comparison Algorithm
1. **ID Matching**: Primary matching by requirement ID
2. **Content Comparison**: Text-based comparison for modifications
3. **Change Categorization**: Automatic sorting into added/deleted/modified/unchanged
4. **Detailed Change Tracking**: Field-level change identification

## 🚀 Usage Examples

### Basic Comparison
1. Launch the application: `python main.py`
2. Click "Browse" for File 1 and select your original ReqIF file
3. Click "Browse" for File 2 and select your modified ReqIF file
4. Click "Compare Files"
5. Review results in the tabbed interface
6. Export results if needed

### Viewing Requirement Details
- Double-click any requirement in the results to see full details
- For modified requirements, view original, modified, and changes summary tabs

### Exporting Results
- Click "Export Results to CSV" for spreadsheet analysis
- Click "Export Summary" for a text summary report

## 🧪 Testing

### Testing with Sample Data
Create simple ReqIF files for testing:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd">
  <THE-HEADER>
    <REQ-IF-HEADER IDENTIFIER="sample"/>
  </THE-HEADER>
  <CORE-CONTENT>
    <REQ-IF-CONTENT>
      <SPEC-OBJECTS>
        <SPEC-OBJECT IDENTIFIER="REQ-001">
          <VALUES>
            <ATTRIBUTE-VALUE-STRING ATTRIBUTE-DEFINITION-REF="Title">
              <THE-VALUE>System shall start</THE-VALUE>
            </ATTRIBUTE-VALUE-STRING>
            <ATTRIBUTE-VALUE-STRING ATTRIBUTE-DEFINITION-REF="Description">
              <THE-VALUE>The system shall start within 5 seconds</THE-VALUE>
            </ATTRIBUTE-VALUE-STRING>
          </VALUES>
        </SPEC-OBJECT>
      </SPEC-OBJECTS>
    </REQ-IF-CONTENT>
  </CORE-CONTENT>
</REQ-IF>
```

### Expected Results
- Parser should extract requirements with ID, title, and description
- Comparator should identify differences between file versions
- GUI should display results in organized tabs

## 🐛 Troubleshooting

### Common Issues

**"No requirements found"**
- Check that your ReqIF file contains SPEC-OBJECT elements
- Verify the XML structure is valid
- Try with a known working ReqIF file

**"XML parsing error"**
- Ensure the file is valid XML
- Check for special characters or encoding issues
- Verify the file is actually a ReqIF file

**"Comparison fails"**
- Ensure both files are valid ReqIF files
- Check that requirements have ID attributes
- Verify files are not corrupted

### Debug Information
- Check the status area in the main window for parsing progress
- Error messages will appear in popup dialogs
- File information is logged during parsing

## 🔮 Future Enhancements

### Next Sprint (2-4 hours)
- Enhanced XML parsing for more ReqIF variants
- Better error messages and validation
- Search and filter functionality in results
- Improved GUI styling and user experience

### Short-term Goals
- Advanced similarity matching for requirements without exact ID matches
- More export formats (Excel, PDF)
- Configuration options for comparison sensitivity
- Batch processing for multiple file pairs

### Long-term Vision
- Real-time diff highlighting
- Version control integration
- Web-based interface
- Advanced analytics and reporting
- Plugin system for custom parsers

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional ReqIF format support
- Enhanced comparison algorithms
- UI/UX improvements
- Performance optimizations
- Documentation and examples

## 📞 Support

For issues or questions:
1. Check this README for common solutions
2. Review the troubleshooting section
3. Create an issue with sample files and error details

---

**Built with Python and tkinter - Professional requirements engineering made simple!**