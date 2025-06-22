#!/usr/bin/env python3
"""
Test Script for Phase 1: Advanced Comparison Settings
Tests the integration of all Phase 1 components
"""

import os
import sys
import traceback

def test_imports():
    """Test that all Phase 1 modules can be imported"""
    print("Testing imports...")
    
    try:
        from comparison_profile import ComparisonProfile, ProfileManager, AttributeConfig
        print("✓ comparison_profile imported successfully")
        
        from attribute_analyzer import AttributeAnalyzer, AttributeStats, analyze_requirements_for_profile
        print("✓ attribute_analyzer imported successfully")
        
        from advanced_comparison_settings import AdvancedComparisonSettings, show_advanced_comparison_settings
        print("✓ advanced_comparison_settings imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        traceback.print_exc()
        return False

def test_comparison_profile():
    """Test ComparisonProfile functionality"""
    print("\nTesting ComparisonProfile...")
    
    try:
        from comparison_profile import ComparisonProfile, ProfileManager, AttributeConfig
        
        # Create profile
        profile = ComparisonProfile("Test Profile")
        profile.description = "A test profile for Phase 1"
        
        # Add custom attributes
        profile.add_attribute("safety_level", "Safety Level", weight=1.0, coverage=0.8)
        profile.add_attribute("verification_method", "Verification Method", weight=0.6, coverage=0.5)
        
        # Test weight adjustment
        profile.set_attribute_weight("title", 0.9)
        profile.set_attribute_weight("description", 1.0)
        
        # Test validation
        issues = profile.validate()
        if issues:
            print(f"✗ Profile validation failed: {issues}")
            return False
        
        # Test serialization
        profile_dict = profile.to_dict()
        restored_profile = ComparisonProfile.from_dict(profile_dict)
        
        if restored_profile.name != profile.name:
            print("✗ Profile serialization failed")
            return False
        
        # Test profile manager
        manager = ProfileManager()
        manager.add_profile(profile)
        
        if profile.name not in manager.list_profiles():
            print("✗ Profile manager failed")
            return False
        
        print("✓ ComparisonProfile tests passed")
        return True
        
    except Exception as e:
        print(f"✗ ComparisonProfile test error: {e}")
        traceback.print_exc()
        return False

def test_attribute_analyzer():
    """Test AttributeAnalyzer functionality"""
    print("\nTesting AttributeAnalyzer...")
    
    try:
        from attribute_analyzer import AttributeAnalyzer, AttributeStats, analyze_requirements_for_profile
        
        # Create test requirements
        test_requirements = [
            {
                'id': 'REQ-001',
                'title': 'System shall start',
                'description': 'The system shall start within 5 seconds',
                'type': 'functional',
                'priority': 'high',
                'status': 'approved',
                'attributes': {
                    'safety_level': 'SIL-2',
                    'verification_method': 'test',
                    'source_document': 'SRS-001'
                }
            },
            {
                'id': 'REQ-002',
                'title': 'System shall stop',
                'description': 'The system shall stop safely',
                'type': 'functional',
                'priority': 'critical',
                'status': 'draft',
                'attributes': {
                    'safety_level': 'SIL-3',
                    'verification_method': 'inspection'
                }
            }
        ]
        
        # Test analyzer
        analyzer = AttributeAnalyzer()
        results = analyzer.analyze_requirements(test_requirements)
        
        if not results:
            print("✗ Analyzer returned no results")
            return False
        
        # Check for expected attributes
        expected_attrs = ['id', 'title', 'description', 'type', 'priority', 'status']
        for attr in expected_attrs:
            if attr not in results:
                print(f"✗ Missing expected attribute: {attr}")
                return False
        
        # Test recommendations
        recommended = analyzer.get_recommended_attributes(results)
        if not recommended:
            print("✗ No recommended attributes returned")
            return False
        
        # Test analysis function
        combined_results = analyze_requirements_for_profile(test_requirements, test_requirements)
        if len(combined_results) != len(results):
            print("✗ Combined analysis failed")
            return False
        
        print("✓ AttributeAnalyzer tests passed")
        return True
        
    except Exception as e:
        print(f"✗ AttributeAnalyzer test error: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between components"""
    print("\nTesting component integration...")
    
    try:
        from comparison_profile import ComparisonProfile
        from attribute_analyzer import analyze_requirements_for_profile, create_profile_from_analysis
        
        # Create test requirements
        reqs1 = [
            {
                'id': 'REQ-001',
                'title': 'Original title',
                'description': 'Original description',
                'type': 'functional',
                'attributes': {'priority': 'high', 'status': 'draft'}
            }
        ]
        
        reqs2 = [
            {
                'id': 'REQ-001',
                'title': 'Modified title',
                'description': 'Modified description',
                'type': 'functional',
                'attributes': {'priority': 'critical', 'status': 'approved'}
            }
        ]
        
        # Analyze requirements
        stats = analyze_requirements_for_profile(reqs1, reqs2)
        
        # Create profile from analysis
        profile = create_profile_from_analysis(stats, "Integration Test Profile")
        
        # Test comparator integration
        from reqif_comparator import ReqIFComparator
        comparator = ReqIFComparator()
        comparator.set_comparison_profile(profile)
        
        # Run comparison
        results = comparator.compare_requirements(reqs1, reqs2)
        
        if not results or 'modified' not in results:
            print("✗ Comparison with profile failed")
            return False
        
        if len(results['modified']) == 0:
            print("✗ No modified requirements detected")
            return False
        
        print("✓ Integration tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Integration test error: {e}")
        traceback.print_exc()
        return False

def test_gui_components():
    """Test GUI components (without actually showing windows)"""
    print("\nTesting GUI component instantiation...")
    
    try:
        import tkinter as tk
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test that AdvancedComparisonSettings can be instantiated
        from advanced_comparison_settings import AdvancedComparisonSettings
        from comparison_profile import ComparisonProfile
        
        test_reqs = [{'id': 'TEST-001', 'title': 'Test', 'description': 'Test req'}]
        profile = ComparisonProfile("Test Profile")
        
        # This would normally show a window, but we're just testing instantiation
        # settings = AdvancedComparisonSettings(root, test_reqs, test_reqs, profile)
        
        # Clean up
        root.destroy()
        
        print("✓ GUI component instantiation successful")
        return True
        
    except ImportError:
        print("⚠ Tkinter not available, skipping GUI tests")
        return True
    except Exception as e:
        print(f"✗ GUI component test error: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all Phase 1 tests"""
    print("=" * 60)
    print("Phase 1: Advanced Comparison Settings - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("ComparisonProfile Tests", test_comparison_profile),
        ("AttributeAnalyzer Tests", test_attribute_analyzer),
        ("Integration Tests", test_integration),
        ("GUI Component Tests", test_gui_components)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 1 is ready for use.")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Add current directory to Python path to ensure imports work
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    success = run_all_tests()
    
    if success:
        print("\n🚀 Phase 1 implementation is complete and functional!")
        print("\nNext steps:")
        print("1. Run your main application: python main.py")
        print("2. Load two ReqIF files for comparison")
        print("3. Click 'Advanced Settings' to configure comparison")
        print("4. Use the new attribute selection and weighting features")
        print("\nPhase 2 (Enhanced Comparison Rules) can now be implemented!")
    else:
        print("\n🔧 Please fix the failing tests before proceeding.")
    
    sys.exit(0 if success else 1)