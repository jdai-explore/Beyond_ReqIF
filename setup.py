#!/usr/bin/env python3
"""
ReqIF Tool Suite - Setup Script
===============================

Installation script for the ReqIF Tool Suite package.
Supports both development and production installations.

Usage:
    python setup.py install          # Standard installation
    python setup.py develop          # Development installation
    pip install -e .                 # Editable installation (recommended for dev)
    pip install .                    # Standard pip installation

Author: ReqIF Tool Suite Team
Version: 2.0.0
License: MIT
"""

import sys
import os
from pathlib import Path
from setuptools import setup, find_packages

# Ensure Python version compatibility
if sys.version_info < (3, 8):
    sys.exit("Error: Python 3.8 or higher is required.")

# Get the directory containing this setup.py file
HERE = Path(__file__).parent.absolute()

# Read the README file for long description
def read_readme():
    """Read README.md for package description"""
    readme_path = HERE / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A comprehensive tool suite for ReqIF (Requirements Interchange Format) files."

# Read requirements from requirements.txt
def read_requirements(filename="requirements.txt"):
    """Read requirements from file, filtering out comments and options"""
    req_file = HERE / filename
    if not req_file.exists():
        return []
    
    requirements = []
    with open(req_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines, comments, and pip options
            if line and not line.startswith("#") and not line.startswith("-"):
                # Handle conditional dependencies (platform-specific)
                if ";" in line:
                    requirements.append(line)
                else:
                    requirements.append(line)
    return requirements

# Read version from a dedicated file or module
def get_version():
    """Get version from utils/constants.py or fallback to default"""
    try:
        # Try to read from constants file
        version_file = HERE / "utils" / "constants.py"
        if version_file.exists():
            # Read version from constants.py
            namespace = {}
            with open(version_file, "r", encoding="utf-8") as f:
                exec(f.read(), namespace)
            # Look for VERSION in APP_CONFIG or as standalone
            if "APP_CONFIG" in namespace:
                return getattr(namespace["APP_CONFIG"], "VERSION", "2.0.0")
            elif "VERSION" in namespace:
                return namespace["VERSION"]
    except Exception:
        pass
    
    # Fallback version
    return "2.0.0"

# Get development requirements
def get_dev_requirements():
    """Get development requirements"""
    return read_requirements("requirements-dev.txt")

# Get build requirements  
def get_build_requirements():
    """Get build requirements"""
    return read_requirements("requirements-build.txt")

# Package configuration
PACKAGE_NAME = "reqif-tool-suite"
VERSION = get_version()
DESCRIPTION = "A comprehensive tool suite for ReqIF (Requirements Interchange Format) files"
LONG_DESCRIPTION = read_readme()
AUTHOR = "ReqIF Tool Suite Team"
AUTHOR_EMAIL = "support@reqif-tools.com"
URL = "https://github.com/your-org/reqif-tool-suite"
LICENSE = "MIT"

# Classifiers for PyPI
CLASSIFIERS = [
    # Development Status
    "Development Status :: 4 - Beta",
    
    # Intended Audience
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Manufacturing",
    "Intended Audience :: Science/Research",
    
    # Topic
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Software Development :: Documentation",
    "Topic :: Office/Business",
    "Topic :: Scientific/Engineering",
    "Topic :: Utilities",
    
    # License
    "License :: OSI Approved :: MIT License",
    
    # Operating Systems
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
    
    # Programming Language
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3 :: Only",
    
    # User Interface
    "Environment :: X11 Applications",
    "Environment :: Win32 (MS Windows)",
    "Environment :: MacOS X",
    
    # Natural Language
    "Natural Language :: English",
]

# Keywords for PyPI search
KEYWORDS = [
    "reqif", "requirements", "interchange", "format", "comparison", 
    "visualization", "analysis", "engineering", "quality", "assurance",
    "documentation", "traceability", "automotive", "aerospace", "medical",
    "xml", "diff", "excel", "csv", "pdf", "export"
]

# Project URLs
PROJECT_URLS = {
    "Homepage": URL,
    "Documentation": f"{URL}/docs",
    "Bug Reports": f"{URL}/issues",
    "Source Code": URL,
    "Discussions": f"{URL}/discussions",
    "Changelog": f"{URL}/blob/main/CHANGELOG.md",
    "Download": f"{URL}/releases",
}

# Entry points for command-line scripts
ENTRY_POINTS = {
    "console_scripts": [
        "reqif-tool-suite=main:main",
        "reqif-compare=cli.compare:main",
        "reqif-visualize=cli.visualize:main",
        "reqif-analyze=cli.analyze:main",
    ],
    "gui_scripts": [
        "reqif-gui=main:main",
    ],
}

# Package data to include
PACKAGE_DATA = {
    "": [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "requirements*.txt",
    ],
    "resources": [
        "icons/*",
        "themes/*",
        "templates/*",
        "config/*",
    ],
    "docs": [
        "*.md",
        "*.rst",
        "images/*",
    ],
    "tests": [
        "fixtures/*",
        "*.reqif",
        "*.reqifz",
    ],
}

# Data files to install (system-wide)
DATA_FILES = [
    # Desktop integration files (Linux)
    ("share/applications", ["resources/desktop/reqif-tool-suite.desktop"]),
    ("share/icons/hicolor/48x48/apps", ["resources/icons/reqif-tool-suite-48.png"]),
    ("share/icons/hicolor/64x64/apps", ["resources/icons/reqif-tool-suite-64.png"]),
    ("share/icons/hicolor/128x128/apps", ["resources/icons/reqif-tool-suite-128.png"]),
    
    # Documentation
    ("share/doc/reqif-tool-suite", ["README.md", "LICENSE"]),
]

# Platform-specific requirements
def get_platform_requirements():
    """Get platform-specific requirements"""
    extras = {}
    
    # Windows-specific
    extras["windows"] = [
        "pywin32>=227; platform_system=='Windows'",
    ]
    
    # macOS-specific
    extras["macos"] = [
        "pyobjc-core>=9.0; platform_system=='Darwin'",
    ]
    
    # Advanced analytics
    extras["analytics"] = [
        "numpy>=1.21.0,<2.0.0",
        "pandas>=1.5.0,<3.0.0",
        "scipy>=1.7.0,<2.0.0",
    ]
    
    # Web interface (future)
    extras["web"] = [
        "flask>=2.0.0,<3.0.0",
        "flask-cors>=3.0.0,<5.0.0",
        "requests>=2.28.0,<3.0.0",
    ]
    
    # Database support (future)
    extras["database"] = [
        "sqlalchemy>=1.4.0,<3.0.0",
    ]
    
    # All optional features
    extras["all"] = (
        extras["analytics"] + 
        extras["web"] + 
        extras["database"]
    )
    
    # Development dependencies
    extras["dev"] = get_dev_requirements()
    
    # Build dependencies
    extras["build"] = get_build_requirements()
    
    return extras

# Custom commands
class CustomCommand:
    """Base class for custom setup commands"""
    
    def __init__(self):
        pass

# Custom test command
try:
    from setuptools.command.test import test as TestCommand
    
    class PyTest(TestCommand):
        """Custom test command using pytest"""
        
        user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]
        
        def initialize_options(self):
            TestCommand.initialize_options(self)
            self.pytest_args = []
        
        def run_tests(self):
            import pytest
            errno = pytest.main(self.pytest_args)
            sys.exit(errno)
    
    cmdclass = {"test": PyTest}
    
except ImportError:
    cmdclass = {}

# Custom clean command
try:
    from setuptools import Command
    
    class CleanCommand(Command):
        """Custom clean command to remove build artifacts"""
        
        description = "Remove build artifacts"
        user_options = []
        
        def initialize_options(self):
            pass
        
        def finalize_options(self):
            pass
        
        def run(self):
            import shutil
            
            # Directories to remove
            dirs_to_remove = [
                "build",
                "dist",
                "*.egg-info",
                "__pycache__",
                ".pytest_cache",
                ".coverage",
                "htmlcov",
            ]
            
            for dir_pattern in dirs_to_remove:
                for path in Path(".").glob(dir_pattern):
                    if path.is_dir():
                        print(f"Removing directory: {path}")
                        shutil.rmtree(path)
                    elif path.is_file():
                        print(f"Removing file: {path}")
                        path.unlink()
    
    cmdclass["clean"] = CleanCommand
    
except ImportError:
    pass

# Main setup configuration
def main():
    """Main setup function"""
    
    # Validate environment
    if not (HERE / "main.py").exists():
        sys.exit("Error: main.py not found. Run setup.py from the project root.")
    
    # Setup configuration
    setup(
        # Basic package information
        name=PACKAGE_NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        
        # Author information
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=AUTHOR,
        maintainer_email=AUTHOR_EMAIL,
        
        # URLs
        url=URL,
        project_urls=PROJECT_URLS,
        
        # License
        license=LICENSE,
        
        # Package discovery
        packages=find_packages(exclude=["tests*", "docs*", "build*"]),
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        include_package_data=True,
        
        # Dependencies
        install_requires=read_requirements(),
        extras_require=get_platform_requirements(),
        python_requires=">=3.8",
        
        # Entry points
        entry_points=ENTRY_POINTS,
        
        # Metadata
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        platforms=["any"],
        
        # Custom commands
        cmdclass=cmdclass,
        
        # Test suite
        test_suite="tests",
        
        # Zip safety
        zip_safe=False,
        
        # Options
        options={
            "build_exe": {
                "packages": ["tkinter", "lxml", "openpyxl", "reportlab"],
                "include_files": [
                    ("resources/", "resources/"),
                    ("README.md", "README.md"),
                    ("LICENSE", "LICENSE"),
                ],
                "excludes": ["pytest", "sphinx", "setuptools"],
            },
            "bdist_wheel": {
                "universal": False,  # Not universal due to platform-specific features
            },
        },
    )

if __name__ == "__main__":
    main()