#!/usr/bin/env python3
"""
Quick syntax check for all Phase 1 files
"""

import ast
import os

def check_syntax(filename):
    """Check syntax of a Python file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the source code
        ast.parse(source, filename=filename)
        print(f"✓ {filename} - Syntax OK")
        return True
        
    except SyntaxError as e:
        print(f"✗ {filename} - Syntax Error:")
        print(f"  Line {e.lineno}: {e.text.strip() if e.text else ''}")
        print(f"  {' ' * (e.offset - 1 if e.offset else 0)}^")
        print(f"  {e.msg}")
        return False
        
    except FileNotFoundError:
        print(f"⚠ {filename} - File not found")
        return False
        
    except Exception as e:
        print(f"✗ {filename} - Error: {e}")
        return False

def main():
    """Check syntax of all Phase 1 files"""
    print("Phase 1 Syntax Check")
    print("=" * 40)
    
    files_to_check = [
        'comparison_profile.py',
        'attribute_analyzer.py', 
        'advanced_comparison_settings.py',
        'reqif_comparator.py',
        'main.py',
        'test_phase1.py'
    ]
    
    passed = 0
    total = len(files_to_check)
    
    for filename in files_to_check:
        if check_syntax(filename):
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Syntax Check Results: {passed}/{total} files OK")
    
    if passed == total:
        print("🎉 All files have correct syntax!")
        return True
    else:
        print(f"❌ {total - passed} files have syntax errors")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)