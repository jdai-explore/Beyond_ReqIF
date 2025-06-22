#!/usr/bin/env python3
"""
Phase 1 Completion Script
Applies all Phase 1 Advanced Comparison Settings integration
"""

import os
import shutil

def backup_and_update_files():
    """Backup original files and apply Phase 1 updates"""
    
    files_to_update = [
        ('main.py', 'Updated main.py with Advanced Comparison integration'),
        ('comparison_gui.py', 'Updated comparison_gui.py with profile information display'),
        ('theme_manager.py', 'Updated theme_manager.py with Apple Design Guidelines')
    ]
    
    print("🚀 Phase 1: Advanced Comparison Settings - Completion")
    print("=" * 60)
    
    # Create backups
    print("\n📋 Creating backups...")
    for filename, description in files_to_update:
        if os.path.exists(filename):
            backup_name = f"{filename}.phase0.backup"
            try:
                shutil.copy2(filename, backup_name)
                print(f"✅ Backed up {filename} → {backup_name}")
            except Exception as e:
                print(f"❌ Failed to backup {filename}: {e}")
                return False
        else:
            print(f"ℹ️  {filename} not found - will be created")
    
    print("\n🔧 Files ready for Phase 1 integration!")
    print("\nNext steps:")
    print("1. Replace your main.py with the updated version")
    print("2. Replace your comparison_gui.py with the updated version") 
    print("3. Replace your theme_manager.py with the Apple Design Guidelines version")
    print("4. Run: python test_phase1.py")
    print("5. Run: python main.py")
    
    return True

def verify_phase1_components():
    """Verify all Phase 1 components are present"""
    
    print("\n🔍 Verifying Phase 1 components...")
    
    required_files = [
        ('comparison_profile.py', 'Core data models for comparison profiles'),
        ('attribute_analyzer.py', 'Attribute analysis and discovery'),
        ('advanced_comparison_settings.py', 'Advanced settings GUI'),
        ('test_phase1.py', 'Phase 1 test suite')
    ]
    
    all_present = True
    
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename} - {description}")
        else:
            print(f"❌ {filename} - {description} - MISSING")
            all_present = False
    
    if all_present:
        print("\n🎉 All Phase 1 components are present!")
        return True
    else:
        print("\n⚠️  Some Phase 1 components are missing.")
        print("Please ensure all Phase 1 files are in place before proceeding.")
        return False

def test_imports():
    """Test that Phase 1 imports work correctly"""
    
    print("\n🧪 Testing Phase 1 imports...")
    
    try:
        from comparison_profile import ComparisonProfile, ProfileManager
        print("✅ comparison_profile imports successfully")
        
        from attribute_analyzer import AttributeAnalyzer, analyze_requirements_for_profile
        print("✅ attribute_analyzer imports successfully")
        
        from advanced_comparison_settings import show_advanced_comparison_settings
        print("✅ advanced_comparison_settings imports successfully")
        
        print("\n🎯 All Phase 1 imports working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease ensure all Phase 1 files are present and have correct syntax.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_quick_test():
    """Create a quick test to verify Phase 1 integration"""
    
    test_script = '''#!/usr/bin/env python3
"""
Quick Phase 1 Integration Test
Tests the core Advanced Comparison functionality
"""

def test_phase1_integration():
    """Quick test of Phase 1 integration"""
    
    print("🧪 Phase 1 Integration Test")
    print("=" * 30)
    
    try:
        # Test imports
        print("\\n1. Testing imports...")
        from comparison_profile import ComparisonProfile, ProfileManager
        from attribute_analyzer import analyze_requirements_for_profile
        from advanced_comparison_settings import show_advanced_comparison_settings
        print("✅ All imports successful")
        
        # Test profile creation
        print("\\n2. Testing profile creation...")
        profile = ComparisonProfile("Test Profile")
        profile.add_attribute("test_attr", "Test Attribute", weight=0.8)
        print(f"✅ Created profile: {profile.name}")
        
        # Test profile manager
        print("\\n3. Testing profile manager...")
        manager = ProfileManager()
        manager.add_profile(profile)
        profiles = manager.list_profiles()
        print(f"✅ Profile manager working: {len(profiles)} profiles")
        
        # Test requirements analysis
        print("\\n4. Testing requirements analysis...")
        test_reqs = [
            {'id': 'REQ-001', 'title': 'Test', 'description': 'Test requirement'}
        ]
        
        stats = analyze_requirements_for_profile(test_reqs, test_reqs)
        print(f"✅ Requirements analysis: {len(stats)} attributes found")
        
        print("\\n🎉 Phase 1 integration test PASSED!")
        print("\\nAdvanced Comparison Settings are ready to use!")
        return True
        
    except Exception as e:
        print(f"\\n❌ Phase 1 integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase1_integration()
    print(f"\\nTest result: {'PASS' if success else 'FAIL'}")
'''
    
    try:
        with open('quick_phase1_test.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        print("✅ Created quick_phase1_test.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create test script: {e}")
        return False

def show_phase1_summary():
    """Show Phase 1 completion summary"""
    
    print("\n" + "=" * 60)
    print("🎯 PHASE 1: ADVANCED COMPARISON SETTINGS - COMPLETE")
    print("=" * 60)
    
    print("\n📋 What's been implemented:")
    print("• ✅ ComparisonProfile system for storing comparison settings")
    print("• ✅ AttributeAnalyzer for intelligent attribute discovery")
    print("• ✅ Advanced Settings GUI with 3 tabs (Attribute Selection, Rules, Profiles)")
    print("• ✅ Profile management (save, load, import, export)")
    print("• ✅ Weighted attribute comparison")
    print("• ✅ Integration with main application")
    print("• ✅ Profile information display in results")
    print("• ✅ Apple Design Guidelines styling")
    
    print("\n🔧 How to use:")
    print("1. Run: python main.py")
    print("2. Select two ReqIF files for comparison")
    print("3. Choose a comparison profile or click 'Advanced Settings...'")
    print("4. Customize which attributes to compare and their weights")
    print("5. Run comparison to see profile-based results")
    
    print("\n🎨 Key features:")
    print("• Smart attribute detection from your ReqIF files")
    print("• Customizable attribute weights (0.0 to 1.0)")
    print("• Multiple comparison profiles for different use cases")
    print("• Professional Apple-inspired interface")
    print("• Detailed comparison results with profile information")
    
    print("\n📈 What this enables:")
    print("• Focus on attributes that matter most to your workflow")
    print("• Consistent comparison settings across multiple file pairs")
    print("• Better change detection through weighted comparison")
    print("• Reusable profiles for different types of analysis")
    
    print("\n🚀 Ready for Phase 2:")
    print("• Enhanced comparison rules (fuzzy matching, field-specific rules)")
    print("• Advanced diff viewer with weighted highlighting")
    print("• Smart profile suggestions based on file analysis")
    print("• Machine learning for optimal attribute weights")

def main():
    """Main Phase 1 completion function"""
    
    print("🍎 Beyond ReqIF - Phase 1 Advanced Comparison Settings")
    print("Completion and Integration Script")
    print()
    
    # Step 1: Verify components
    if not verify_phase1_components():
        print("\n❌ Phase 1 components missing. Please ensure all files are present.")
        return False
    
    # Step 2: Test imports
    if not test_imports():
        print("\n❌ Phase 1 imports failed. Please check file syntax.")
        return False
    
    # Step 3: Backup and prepare files
    if not backup_and_update_files():
        print("\n❌ Failed to prepare files for Phase 1 integration.")
        return False
    
    # Step 4: Create quick test
    create_quick_test()
    
    # Step 5: Show summary
    show_phase1_summary()
    
    print("\n🎉 Phase 1 completion script finished successfully!")
    print("\nNow update your files with the new versions and test:")
    print("• python quick_phase1_test.py")
    print("• python test_phase1.py") 
    print("• python main.py")
    
    return True

if __name__ == "__main__":
    main()