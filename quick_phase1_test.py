#!/usr/bin/env python3
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
        print("\n1. Testing imports...")
        from comparison_profile import ComparisonProfile, ProfileManager
        from attribute_analyzer import analyze_requirements_for_profile
        from advanced_comparison_settings import show_advanced_comparison_settings
        print("✅ All imports successful")
        
        # Test profile creation
        print("\n2. Testing profile creation...")
        profile = ComparisonProfile("Test Profile")
        profile.add_attribute("test_attr", "Test Attribute", weight=0.8)
        print(f"✅ Created profile: {profile.name}")
        
        # Test profile manager
        print("\n3. Testing profile manager...")
        manager = ProfileManager()
        manager.add_profile(profile)
        profiles = manager.list_profiles()
        print(f"✅ Profile manager working: {len(profiles)} profiles")
        
        # Test requirements analysis
        print("\n4. Testing requirements analysis...")
        test_reqs = [
            {'id': 'REQ-001', 'title': 'Test', 'description': 'Test requirement'}
        ]
        
        stats = analyze_requirements_for_profile(test_reqs, test_reqs)
        print(f"✅ Requirements analysis: {len(stats)} attributes found")
        
        print("\n🎉 Phase 1 integration test PASSED!")
        print("\nAdvanced Comparison Settings are ready to use!")
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 1 integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase1_integration()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
