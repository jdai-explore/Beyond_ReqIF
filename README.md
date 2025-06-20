## ReqIF Comparison Tool

The ReqIF Comparison Tool is a Python-based GUI application designed to compare ReqIF files and folders, providing side-by-side content comparison and detailed summary statistics. This tool is particularly useful for validating and reconciling requirement documents in software development projects.

### Features

- **Single-File Comparison**: Compare two ReqIF files and generate a detailed report on added, modified, and deleted requirements.
- **Folder Comparison**: Compare two directories containing ReqIF files, summarizing changes across all files in each directory.
- **Summary Statistics**: Display an overview of changes, including counts of added, modified, and deleted requirements.
- **User-Friendly Interface**: Utilize a simple and intuitive graphical user interface for easy navigation and interaction.
- **Export Results**: Optionally export comparison results as text or JSON files for offline analysis or further integration.

### Installation and Setup

- **Prerequisites**: This tool requires Python 3.x and Tkinter (GUI library) to be installed on your machine.
- **Dependencies**: The required libraries are `lxml` (for XML parsing) and standard library modules.
- **Installation**: Save the Python script in a directory of your choice and run it using Python directly: `python requif_comparison_tool.py`.

### Usage

1. **File/Folder Selection**: The user can either choose two ReqIF files or two folders containing ReqIF files for comparison.
2. **Comparison**: Select "Compare" button to initiate the comparison process.
3. **Result Display**: After comparison, the results will be displayed in a user-friendly format with tabs for each type of change (added, modified, deletions, unchanged, and summaries).

### Exporting Results

- Users can save the comparison results in text (`.txt`) or JSON (`.json`) format for use in reports or further analysis.

### Contact

For any issues, feedback, or suggestions, please contact us at [development@miraiflow.tech]
