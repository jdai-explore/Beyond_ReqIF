#!/usr/bin/env python3
"""
Test Script for Improved ReqIF Parser
Use this to test the improved parsing logic with your existing application.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_parser_comparison(file_path: str):
    """Compare original vs improved parser on the same file"""
    print("🔄 PARSER COMPARISON TEST")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Test original parser
    print("📊 Testing ORIGINAL parser...")
    try:
        from reqif_parser import ReqIFParser
        original_parser = ReqIFParser()
        original_reqs = original_parser.parse_file(file_path)
        
        print(f"✅ Original parser: {len(original_reqs)} requirements")
        
        # Show sample from original
        if original_reqs:
            sample_orig = original_reqs[0]
            print(f"   Sample ID: {sample_orig.get('id', 'N/A')}")
            print(f"   Sample Title: {sample_orig.get('title', 'N/A')}")
            print(f"   Sample Attributes: {len(sample_orig.get('attributes', {}))}")
        
    except Exception as e:
        print(f"❌ Original parser failed: {str(e)}")
        original_reqs = []
    
    print()
    
    # Test improved parser
    print("📊 Testing IMPROVED parser...")
    try:
        from reqif_parser_improved import ImprovedReqIFParser
        improved_parser = ImprovedReqIFParser()
        improved_reqs = improved_parser.parse_file(file_path)
        
        print(f"✅ Improved parser: {len(improved_reqs)} requirements")
        
        # Quality analysis
        quality = improved_parser.validate_parsing_quality(improved_reqs)
        print(f"   Quality Score: {quality['quality_score']}%")
        
        # Show sample from improved
        if improved_reqs:
            sample_imp = improved_reqs[0]
            print(f"   Sample ID: {sample_imp.get('id', 'N/A')}")
            print(f"   Sample Title: {sample_imp.get('title', 'N/A')}")
            print(f"   Sample Attributes: {len(sample_imp.get('attributes', {}))}")
        
        # Show diagnostics
        diagnostics = improved_parser.get_parsing_diagnostics()
        print(f"   Namespace: {diagnostics['namespace_info']['root_namespace']}")
        
    except Exception as e:
        print(f"❌ Improved parser failed: {str(e)}")
        improved_reqs = []
    
    print()
    
    # Comparison summary
    print("📈 COMPARISON SUMMARY")
    print("-"*40)
    print(f"Original parser requirements: {len(original_reqs)}")
    print(f"Improved parser requirements: {len(improved_reqs)}")
    
    if len(improved_reqs) > len(original_reqs):
        print(f"✅ Improved parser found {len(improved_reqs) - len(original_reqs)} more requirements")
    elif len(improved_reqs) < len(original_reqs):
        print(f"⚠️ Improved parser found {len(original_reqs) - len(improved_reqs)} fewer requirements")
    else:
        print("ℹ️ Both parsers found the same number of requirements")
    
    # Content quality comparison
    if original_reqs and improved_reqs:
        print("\n📊 CONTENT QUALITY COMPARISON")
        print("-"*40)
        
        # Compare first requirement in detail
        orig_first = original_reqs[0]
        imp_first = improved_reqs[0]
        
        print(f"First requirement comparison:")
        print(f"  Original title: '{orig_first.get('title', 'N/A')}'")
        print(f"  Improved title: '{imp_first.get('title', 'N/A')}'")
        print(f"  Original desc length: {len(orig_first.get('description', ''))}")
        print(f"  Improved desc length: {len(imp_first.get('description', ''))}")
        print(f"  Original attributes: {len(orig_first.get('attributes', {}))}")
        print(f"  Improved attributes: {len(imp_first.get('attributes', {}))}")


def replace_parser_temporarily():
    """Temporarily replace the original parser for testing"""
    print("🔄 TEMPORARILY REPLACING PARSER")
    print("="*40)
    
    try:
        # Import the improved parser
        from reqif_parser_improved import create_improved_parser_replacement
        
        # Create replacement
        improved_parser = create_improved_parser_replacement()
        
        # Replace in sys.modules so imports will use the improved version
        import reqif_parser
        reqif_parser.ReqIFParser = lambda: improved_parser
        
        print("✅ Parser temporarily replaced!")
        print("💡 Now you can run your main application and it will use the improved parser")
        print("💡 Run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to replace parser: {str(e)}")
        return False


def create_permanent_backup_and_replace():
    """Create backup of original parser and replace it"""
    print("🔄 CREATING PERMANENT REPLACEMENT")
    print("="*40)
    
    try:
        # Create backup
        original_file = Path("reqif_parser.py")
        backup_file = Path("reqif_parser_original_backup.py")
        
        if original_file.exists():
            if not backup_file.exists():
                import shutil
                shutil.copy2(original_file, backup_file)
                print(f"✅ Created backup: {backup_file}")
            else:
                print(f"ℹ️ Backup already exists: {backup_file}")
        
        # Create new parser file that uses improved logic
        replacement_content = '''#!/usr/bin/env python3
"""
ReqIF Parser Module - Enhanced Version
This file now uses the improved parsing logic while maintaining compatibility.
"""

from reqif_parser_improved import ImprovedReqIFParser
from typing import List, Dict, Any

class ReqIFParser:
    """Enhanced ReqIF Parser using improved logic"""
    
    def __init__(self):
        self.improved_parser = ImprovedReqIFParser()
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse ReqIF file using improved logic"""
        return self.improved_parser.parse_file(file_path)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            requirements = self.parse_file(file_path)
            quality = self.improved_parser.validate_parsing_quality(requirements)
            
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_type': 'ReqIFZ' if file_path.lower().endswith('.reqifz') else 'ReqIF',
                'file_size': os.path.getsize(file_path),
                'requirement_count': len(requirements),
                'quality_score': quality['quality_score'],
                'parsing_success': True
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'error': str(e),
                'parsing_success': False
            }
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information"""
        return self.improved_parser.get_parsing_diagnostics()


# For backward compatibility
if __name__ == "__main__":
    print("Enhanced ReqIF Parser loaded successfully!")
'''
        
        # Write the replacement file
        with open("reqif_parser.py", "w", encoding="utf-8") as f:
            f.write(replacement_content)
        
        print("✅ Parser replaced with improved version!")
        print("✅ Original parser backed up as reqif_parser_original_backup.py")
        print("💡 You can now run your application normally")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create permanent replacement: {str(e)}")
        return False


def restore_original_parser():
    """Restore the original parser from backup"""
    print("🔄 RESTORING ORIGINAL PARSER")
    print("="*40)
    
    try:
        backup_file = Path("reqif_parser_original_backup.py")
        original_file = Path("reqif_parser.py")
        
        if backup_file.exists():
            import shutil
            shutil.copy2(backup_file, original_file)
            print("✅ Original parser restored!")
            return True
        else:
            print("❌ No backup file found")
            return False
            
    except Exception as e:
        print(f"❌ Failed to restore: {str(e)}")
        return False


def main():
    """Main test interface"""
    print("🧪 ReqIF Parser Testing & Replacement Tool")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("Usage options:")
        print("  python test_improved_parser.py <reqif_file>           # Compare parsers")
        print("  python test_improved_parser.py --replace-temp        # Replace temporarily")
        print("  python test_improved_parser.py --replace-permanent   # Replace permanently")
        print("  python test_improved_parser.py --restore             # Restore original")
        print()
        print("Examples:")
        print("  python test_improved_parser.py myfile.reqif")
        print("  python test_improved_parser.py --replace-permanent")
        return
    
    arg = sys.argv[1]
    
    if arg == "--replace-temp":
        success = replace_parser_temporarily()
        if success:
            # Try to start the main application
            try:
                print("\n🚀 Starting main application with improved parser...")
                from main import ReqIFToolMVP
                app = ReqIFToolMVP()
                app.run()
            except Exception as e:
                print(f"❌ Failed to start application: {str(e)}")
    
    elif arg == "--replace-permanent":
        success = create_permanent_backup_and_replace()
        if success:
            print("\n💡 Next steps:")
            print("  1. Run: python main.py")
            print("  2. Test with your ReqIF files")
            print("  3. If issues occur, run: python test_improved_parser.py --restore")
    
    elif arg == "--restore":
        restore_original_parser()
    
    else:
        # Treat as file path
        file_path = arg
        test_parser_comparison(file_path)
        
        print("\n💡 Want to use the improved parser?")
        print("  Run: python test_improved_parser.py --replace-permanent")


if __name__ == "__main__":
    main()