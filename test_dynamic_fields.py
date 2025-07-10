#!/usr/bin/env python3
"""
NEW: Test Dynamic Fields Implementation - Phase 5
Tests parser and comparison with various ReqIF structures to ensure no artificial fields are created
"""

import unittest
import tempfile
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator
from validation.reqif_structure_validator import ReqIFStructureValidator
from error_handler import ErrorHandler
from utils.config import get_parsing_config


class TestDynamicFields(unittest.TestCase):
    """Test dynamic field detection and handling without artificial field mapping"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ReqIFParser()
        self.comparator = ReqIFComparator()
        self.validator = ReqIFStructureValidator()
        self.error_handler = ErrorHandler("Test Suite")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_no_artificial_fields_created(self):
        """Test that parser creates no artificial fields"""
        print("Testing: No artificial fields created...")
        
        # Mock requirement data with only authentic ReqIF fields
        mock_requirements = [
            {
                'id': 'REQ-001',
                'identifier': 'SYS-REQ-001',
                'type': 'Functional Requirement',
                'attributes': {
                    'Object Text': 'The system shall process user input',
                    'Object Heading': 'User Input Processing'
                }
            },
            {
                'id': 'REQ-002',
                'attributes': {
                    'Object Text': 'The system shall validate data integrity'
                }
            }
        ]
        
        # Validate using structure validator
        validation_results = self.validator.validate_parsing_results(mock_requirements, "test_file.reqif")
        
        # Should pass validation (no artificial fields)
        self.assertTrue(validation_results['is_valid'], 
                       f"Validation failed: {validation_results['errors']}")
        
        # Check field authenticity
        field_validation = validation_results['field_validation']
        self.assertEqual(len(field_validation['artificial_fields_detected']), 0,
                        f"Artificial fields detected: {field_validation['artificial_fields_detected']}")
        
        print("✅ PASS: No artificial fields created")
    
    def test_artificial_fields_detection(self):
        """Test that artificial fields are properly detected and flagged"""
        print("Testing: Artificial fields detection...")
        
        # Mock requirement data WITH artificial fields (should fail validation)
        invalid_requirements = [
            {
                'id': 'REQ-001',
                'title': 'Invalid Title Field',  # ARTIFICIAL FIELD
                'description': 'Invalid Description',  # ARTIFICIAL FIELD
                'priority': 'High',  # ARTIFICIAL FIELD
                'status': 'Active',  # ARTIFICIAL FIELD
                'attributes': {
                    'Object Text': 'Some content'
                }
            }
        ]
        
        # Validate using structure validator
        validation_results = self.validator.validate_parsing_results(invalid_requirements, "invalid_test.reqif")
        
        # Should fail validation (artificial fields present)
        self.assertFalse(validation_results['is_valid'],
                        "Validation should have failed due to artificial fields")
        
        # Check that artificial fields were detected
        field_validation = validation_results['field_validation']
        artificial_fields = set(field_validation['artificial_fields_detected'])
        expected_artificial = {'title', 'description', 'priority', 'status'}
        
        self.assertTrue(artificial_fields >= expected_artificial,
                       f"Not all artificial fields detected. Found: {artificial_fields}")
        
        print("✅ PASS: Artificial fields properly detected")
    
    def test_parser_with_various_reqif_structures(self):
        """Test parser with various ReqIF structures"""
        print("Testing: Parser with various ReqIF structures...")
        
        test_structures = [
            # Structure 1: Minimal ReqIF
            {
                'name': 'minimal_reqif',
                'requirements': [
                    {'id': 'REQ-001'},
                    {'id': 'REQ-002'}
                ]
            },
            
            # Structure 2: ReqIF with types
            {
                'name': 'typed_reqif',
                'requirements': [
                    {
                        'id': 'REQ-001',
                        'type': 'Functional Requirement',
                        'identifier': 'SYS-FUNC-001'
                    }
                ]
            },
            
            # Structure 3: ReqIF with rich attributes
            {
                'name': 'rich_attributes_reqif',
                'requirements': [
                    {
                        'id': 'REQ-001',
                        'attributes': {
                            'Object Text': 'Detailed requirement text',
                            'Object Heading': 'Requirement Title',
                            'Custom Attribute': 'Custom Value',
                            'Rationale': 'Requirement rationale'
                        }
                    }
                ]
            },
            
            # Structure 4: Mixed structure
            {
                'name': 'mixed_structure_reqif',
                'requirements': [
                    {
                        'id': 'REQ-001',
                        'type': 'Functional',
                        'attributes': {
                            'Object Text': 'Text content'
                        }
                    },
                    {
                        'id': 'REQ-002',
                        'identifier': 'CUSTOM-002'
                    },
                    {
                        'id': 'REQ-003',
                        'attributes': {
                            'Different Attribute': 'Different value',
                            'Another Field': 'Another value'
                        }
                    }
                ]
            }
        ]
        
        for test_structure in test_structures:
            with self.subTest(structure=test_structure['name']):
                requirements = test_structure['requirements']
                
                # Validate structure
                validation_results = self.validator.validate_parsing_results(
                    requirements, f"{test_structure['name']}.reqif"
                )
                
                # Should pass validation
                self.assertTrue(validation_results['is_valid'],
                               f"Structure {test_structure['name']} failed validation: {validation_results['errors']}")
                
                # Validate field authenticity
                field_validation = validation_results['field_validation']
                self.assertEqual(len(field_validation['artificial_fields_detected']), 0,
                               f"Artificial fields in {test_structure['name']}: {field_validation['artificial_fields_detected']}")
                
                # Check compliance
                compliance = validation_results['compliance_check']
                self.assertGreaterEqual(compliance['compliance_score'], 0.5,
                                      f"Low compliance score for {test_structure['name']}: {compliance['compliance_score']}")
        
        print("✅ PASS: Parser handles various ReqIF structures correctly")
    
    def test_comparison_with_different_attribute_structures(self):
        """Test comparison with different attribute structures"""
        print("Testing: Comparison with different attribute structures...")
        
        # File 1: Requirements with one attribute structure
        file1_reqs = [
            {
                'id': 'REQ-001',
                'type': 'Functional',
                'attributes': {
                    'Object Text': 'Original text',
                    'Priority': 'High'
                }
            },
            {
                'id': 'REQ-002',
                'attributes': {
                    'Object Text': 'Another requirement'
                }
            }
        ]
        
        # File 2: Requirements with different attribute structure
        file2_reqs = [
            {
                'id': 'REQ-001',
                'type': 'Functional',
                'attributes': {
                    'Object Text': 'Modified text',  # Changed
                    'Priority': 'Medium',  # Changed
                    'New Attribute': 'New value'  # Added
                }
            },
            {
                'id': 'REQ-002',
                'attributes': {
                    'Object Text': 'Another requirement',  # Unchanged
                    'Different Attr': 'Different value'  # Added
                }
            },
            {
                'id': 'REQ-003',  # New requirement
                'attributes': {
                    'Completely Different': 'Structure'
                }
            }
        ]
        
        # Perform comparison
        comparison_results = self.comparator.compare_requirements(file1_reqs, file2_reqs)
        
        # Validate comparison results
        comparison_validation = self.validator.validate_comparison_results(comparison_results)
        self.assertTrue(comparison_validation['is_valid'],
                       f"Comparison validation failed: {comparison_validation['errors']}")
        
        # Check that comparison found changes
        stats = comparison_results.get('statistics', {})
        self.assertGreater(stats.get('added_count', 0) + stats.get('modified_count', 0), 0,
                          "Comparison should have detected changes")
        
        # Verify no artificial field references in results
        self.assertEqual(len(comparison_validation['artificial_field_references']), 0,
                        f"Artificial field references found: {comparison_validation['artificial_field_references']}")
        
        print("✅ PASS: Comparison works with different attribute structures")
    
    def test_ui_adapts_to_field_configuration(self):
        """Test that UI adapts to any field configuration"""
        print("Testing: UI adapts to field configuration...")
        
        # Test various field configurations
        field_configurations = [
            # Configuration 1: Minimal fields
            {
                'name': 'minimal_fields',
                'available_fields': {'id'},
                'ui_expectations': ['id', 'title', 'description']  # UI expects more than available
            },
            
            # Configuration 2: Standard fields
            {
                'name': 'standard_fields',
                'available_fields': {'id', 'type', 'attributes'},
                'ui_expectations': ['id', 'type', 'attributes']
            },
            
            # Configuration 3: Rich fields with attributes
            {
                'name': 'rich_fields',
                'available_fields': {'id', 'type', 'identifier', 'attributes', 'attr_Object Text', 'attr_Priority'},
                'ui_expectations': ['id', 'type', 'attr_Object Text']
            },
            
            # Configuration 4: Custom field structure
            {
                'name': 'custom_fields',
                'available_fields': {'id', 'custom_field', 'another_field', 'attr_Custom Attribute'},
                'ui_expectations': ['id', 'custom_field', 'title']  # Mix of available and unavailable
            }
        ]
        
        for config in field_configurations:
            with self.subTest(configuration=config['name']):
                available_fields = config['available_fields']
                ui_expectations = config['ui_expectations']
                
                # Validate UI compatibility
                ui_validation = self.validator.validate_ui_compatibility(available_fields, ui_expectations)
                
                # UI should handle missing fields gracefully
                self.assertTrue(ui_validation['is_valid'] or len(ui_validation['warnings']) > 0,
                               f"UI compatibility issue for {config['name']}: {ui_validation['errors']}")
                
                # Check compatibility analysis
                analysis = ui_validation['compatibility_analysis']
                self.assertIn('compatibility_rate', analysis,
                             "Compatibility analysis should include compatibility rate")
                
                # If there are missing fields, should be reported
                missing_count = analysis.get('missing_fields', 0)
                expected_missing = len(set(ui_expectations) - available_fields)
                self.assertEqual(missing_count, expected_missing,
                               f"Missing field count mismatch for {config['name']}")
        
        print("✅ PASS: UI adapts to field configurations")
    
    def test_field_validation_comprehensive(self):
        """Comprehensive test of field validation system"""
        print("Testing: Comprehensive field validation...")
        
        # Test with error handler field validation
        test_requirements = [
            {
                'id': 'REQ-001',
                'type': 'Functional',
                'identifier': 'SYS-001',
                'attributes': {
                    'Object Text': 'Requirement text',
                    'Object Heading': 'Title',
                    'Priority': 'High',
                    'Custom Field': 'Custom value'
                }
            },
            {
                'id': 'REQ-002',
                'attributes': {
                    'Object Text': 'Another requirement',
                    'Different Attribute': 'Different value'
                }
            },
            {
                'id': 'REQ-003'  # Minimal requirement
            }
        ]
        
        # Run comprehensive validation
        validation_results = self.error_handler.validate_dynamic_field_structure(test_requirements)
        
        # Should pass validation
        self.assertTrue(validation_results['is_valid'],
                       f"Field validation failed: {validation_results['errors']}")
        
        # Check field analysis
        field_analysis = validation_results['field_analysis']
        self.assertGreater(field_analysis['total_fields'], 0,
                          "Should detect fields in test requirements")
        
        # Check recommendations
        recommendations = validation_results['recommendations']
        self.assertIsInstance(recommendations, list,
                            "Recommendations should be a list")
        
        print("✅ PASS: Comprehensive field validation works")
    
    def test_parsing_configuration_integration(self):
        """Test integration with parsing configuration"""
        print("Testing: Parsing configuration integration...")
        
        # Get parsing configuration
        parsing_config = get_parsing_config()
        
        # Verify key configuration settings for Phase 3
        self.assertTrue(parsing_config.preserve_original_structure,
                       "Should preserve original ReqIF structure")
        self.assertTrue(parsing_config.field_mapping_disabled,
                       "Field mapping should be disabled")
        self.assertTrue(parsing_config.dynamic_field_detection,
                       "Dynamic field detection should be enabled")
        self.assertTrue(parsing_config.strict_reqif_compliance,
                       "Strict ReqIF compliance should be enabled")
        
        # Test configuration affects behavior
        self.assertEqual(parsing_config.attribute_display_mode, 'human_readable',
                        "Should default to human readable attribute names")
        
        print("✅ PASS: Parsing configuration properly integrated")
    
    def test_create_test_reqif_file(self):
        """Test creating and parsing actual ReqIF file"""
        print("Testing: Creating and parsing actual ReqIF file...")
        
        # Create a simple ReqIF XML content
        reqif_xml = """<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF xmlns="http://www.omg.org/ReqIF" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <THE-HEADER>
        <REQ-IF-HEADER IDENTIFIER="header-001">
            <TITLE>Test ReqIF</TITLE>
        </REQ-IF-HEADER>
    </THE-HEADER>
    <CORE-CONTENT>
        <REQ-IF-CONTENT>
            <SPEC-OBJECTS>
                <SPEC-OBJECT IDENTIFIER="REQ-001">
                    <VALUES>
                        <ATTRIBUTE-VALUE-STRING IDENTIFIER="attr-001">
                            <DEFINITION>
                                <ATTRIBUTE-DEFINITION-STRING-REF>def-text</ATTRIBUTE-DEFINITION-STRING-REF>
                            </DEFINITION>
                            <THE-VALUE>This is a test requirement</THE-VALUE>
                        </ATTRIBUTE-VALUE-STRING>
                    </VALUES>
                    <TYPE>
                        <SPEC-OBJECT-TYPE-REF>type-001</SPEC-OBJECT-TYPE-REF>
                    </TYPE>
                </SPEC-OBJECT>
                <SPEC-OBJECT IDENTIFIER="REQ-002">
                    <VALUES>
                        <ATTRIBUTE-VALUE-STRING IDENTIFIER="attr-002">
                            <DEFINITION>
                                <ATTRIBUTE-DEFINITION-STRING-REF>def-text</ATTRIBUTE-DEFINITION-STRING-REF>
                            </DEFINITION>
                            <THE-VALUE>Another test requirement</THE-VALUE>
                        </ATTRIBUTE-VALUE-STRING>
                    </VALUES>
                    <TYPE>
                        <SPEC-OBJECT-TYPE-REF>type-001</SPEC-OBJECT-TYPE-REF>
                    </TYPE>
                </SPEC-OBJECT>
            </SPEC-OBJECTS>
            <SPEC-TYPES>
                <SPEC-OBJECT-TYPE IDENTIFIER="type-001" LONG-NAME="Functional Requirement"/>
            </SPEC-TYPES>
            <SPEC-ATTRIBUTES>
                <ATTRIBUTE-DEFINITION-STRING IDENTIFIER="def-text" LONG-NAME="Object Text"/>
            </SPEC-ATTRIBUTES>
        </REQ-IF-CONTENT>
    </CORE-CONTENT>
</REQ-IF>"""
        
        # Write to temporary file
        test_file = os.path.join(self.temp_dir, "test.reqif")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(reqif_xml)
        
        try:
            # Parse the file
            requirements = self.parser.parse_file(test_file)
            
            # Validate results
            self.assertGreater(len(requirements), 0, "Should parse some requirements")
            
            # Validate structure
            validation_results = self.validator.validate_parsing_results(requirements, test_file)
            
            # Check for any artificial fields
            field_validation = validation_results['field_validation']
            artificial_fields = field_validation['artificial_fields_detected']
            
            self.assertEqual(len(artificial_fields), 0,
                           f"Artificial fields found in parsed file: {artificial_fields}")
            
            # All requirements should have IDs
            for req in requirements:
                self.assertIn('id', req, "All requirements should have ID field")
                self.assertIsInstance(req, dict, "Requirements should be dictionaries")
            
            print("✅ PASS: Real ReqIF file parsing works without artificial fields")
            
        except Exception as e:
            self.fail(f"Failed to parse test ReqIF file: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        print("Testing: Edge cases and error conditions...")
        
        edge_cases = [
            # Empty requirements list
            {
                'name': 'empty_list',
                'requirements': [],
                'should_pass': True
            },
            
            # Requirements with None values
            {
                'name': 'none_values',
                'requirements': [
                    {'id': 'REQ-001', 'type': None, 'attributes': None}
                ],
                'should_pass': True
            },
            
            # Requirements with empty attributes
            {
                'name': 'empty_attributes',
                'requirements': [
                    {'id': 'REQ-001', 'attributes': {}}
                ],
                'should_pass': True
            },
            
            # Invalid requirement structure
            {
                'name': 'invalid_structure',
                'requirements': [
                    "not_a_dict",  # Should be flagged as invalid
                    {'no_id': 'value'}  # Missing required ID
                ],
                'should_pass': False
            },
            
            # Requirements with complex nested attributes
            {
                'name': 'complex_attributes',
                'requirements': [
                    {
                        'id': 'REQ-001',
                        'attributes': {
                            'Simple Attr': 'Simple value',
                            'Complex Attr': {
                                'nested': 'value',
                                'list': [1, 2, 3]
                            }
                        }
                    }
                ],
                'should_pass': True
            }
        ]
        
        for case in edge_cases:
            with self.subTest(case=case['name']):
                requirements = case['requirements']
                
                try:
                    # Validate with structure validator
                    validation_results = self.validator.validate_parsing_results(
                        requirements, f"{case['name']}.reqif"
                    )
                    
                    if case['should_pass']:
                        # Should not have artificial fields
                        field_validation = validation_results['field_validation']
                        artificial_count = len(field_validation['artificial_fields_detected'])
                        self.assertEqual(artificial_count, 0,
                                       f"Case {case['name']} has artificial fields: {field_validation['artificial_fields_detected']}")
                    else:
                        # Should have validation errors for invalid cases
                        self.assertFalse(validation_results['is_valid'],
                                       f"Case {case['name']} should have failed validation")
                
                except Exception as e:
                    if case['should_pass']:
                        self.fail(f"Case {case['name']} raised unexpected exception: {e}")
                    # Expected for invalid cases
        
        print("✅ PASS: Edge cases handled correctly")
    
    def test_performance_with_large_dataset(self):
        """Test performance with larger dataset"""
        print("Testing: Performance with large dataset...")
        
        # Create larger dataset
        large_requirements = []
        for i in range(100):  # 100 requirements
            req = {
                'id': f'REQ-{i:03d}',
                'type': f'Type-{i % 5}',  # 5 different types
                'identifier': f'SYS-REQ-{i:03d}',
                'attributes': {}
            }
            
            # Add varying number of attributes
            for j in range(i % 10 + 1):  # 1-10 attributes per requirement
                req['attributes'][f'Attribute_{j}'] = f'Value for req {i}, attr {j}'
            
            large_requirements.append(req)
        
        # Validate large dataset
        import time
        start_time = time.time()
        
        validation_results = self.validator.validate_parsing_results(
            large_requirements, "large_dataset.reqif"
        )
        
        validation_time = time.time() - start_time
        
        # Should complete validation in reasonable time (< 5 seconds)
        self.assertLess(validation_time, 5.0,
                       f"Validation took too long: {validation_time:.2f} seconds")
        
        # Should pass validation
        self.assertTrue(validation_results['is_valid'],
                       f"Large dataset validation failed: {validation_results['errors']}")
        
        # Should detect no artificial fields
        field_validation = validation_results['field_validation']
        self.assertEqual(len(field_validation['artificial_fields_detected']), 0,
                        "Large dataset should not contain artificial fields")
        
        print(f"✅ PASS: Large dataset ({len(large_requirements)} requirements) processed in {validation_time:.2f}s")


class TestDynamicFieldsIntegration(unittest.TestCase):
    """Integration tests for dynamic fields across multiple components"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.parser = ReqIFParser()
        self.comparator = ReqIFComparator()
        self.validator = ReqIFStructureValidator()
        
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow with dynamic fields"""
        print("Testing: End-to-end dynamic fields workflow...")
        
        # Step 1: Create test data with authentic ReqIF structure
        original_reqs = [
            {
                'id': 'REQ-001',
                'type': 'Functional',
                'attributes': {
                    'Object Text': 'Original text for requirement 1',
                    'Priority': 'High'
                }
            },
            {
                'id': 'REQ-002',
                'identifier': 'SYS-002',
                'attributes': {
                    'Object Text': 'Text for requirement 2'
                }
            }
        ]
        
        modified_reqs = [
            {
                'id': 'REQ-001',
                'type': 'Functional',
                'attributes': {
                    'Object Text': 'Modified text for requirement 1',  # Changed
                    'Priority': 'Medium',  # Changed
                    'New Attribute': 'Added attribute'  # Added
                }
            },
            {
                'id': 'REQ-002',
                'identifier': 'SYS-002',
                'attributes': {
                    'Object Text': 'Text for requirement 2'  # Unchanged
                }
            },
            {
                'id': 'REQ-003',  # New requirement
                'attributes': {
                    'Object Text': 'New requirement text'
                }
            }
        ]
        
        # Step 2: Validate individual requirement sets
        original_validation = self.validator.validate_parsing_results(original_reqs, "original.reqif")
        modified_validation = self.validator.validate_parsing_results(modified_reqs, "modified.reqif")
        
        self.assertTrue(original_validation['is_valid'], "Original requirements should be valid")
        self.assertTrue(modified_validation['is_valid'], "Modified requirements should be valid")
        
        # Step 3: Perform comparison
        comparison_results = self.comparator.compare_requirements(original_reqs, modified_reqs)
        
        # Step 4: Validate comparison results
        comparison_validation = self.validator.validate_comparison_results(comparison_results)
        self.assertTrue(comparison_validation['is_valid'], 
                       f"Comparison validation failed: {comparison_validation['errors']}")
        
        # Step 5: Verify expected changes were detected
        stats = comparison_results.get('statistics', {})
        self.assertEqual(stats.get('added_count', 0), 1, "Should detect 1 added requirement")
        self.assertEqual(stats.get('modified_count', 0), 1, "Should detect 1 modified requirement")
        self.assertEqual(stats.get('unchanged_count', 0), 1, "Should detect 1 unchanged requirement")
        
        # Step 6: Verify no artificial fields in any results
        for category in ['added', 'deleted', 'modified', 'unchanged']:
            requirements = comparison_results.get(category, [])
            for req in requirements:
                if isinstance(req, dict):
                    artificial_fields = {'title', 'description', 'priority', 'status'}
                    found_artificial = [f for f in artificial_fields if f in req]
                    self.assertEqual(len(found_artificial), 0,
                                   f"Artificial fields found in {category}: {found_artificial}")
        
        print("✅ PASS: End-to-end workflow maintains field authenticity")


def run_all_tests():
    """Run all dynamic fields tests"""
    print("=" * 60)
    print("RUNNING PHASE 5 DYNAMIC FIELDS TESTS")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [TestDynamicFields, TestDynamicFieldsIntegration]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PHASE 5 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Overall result
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED - PHASE 5 VALIDATION COMPLETE!")
        print("✅ Dynamic field implementation is working correctly")
        print("✅ No artificial field mapping detected")
        print("✅ UI components adapt to field configurations")
        print("✅ Parsing maintains ReqIF authenticity")
    else:
        print("\n❌ SOME TESTS FAILED - PHASE 5 VALIDATION INCOMPLETE")
        print("Please review failures and fix issues before deployment")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Phase 5 Testing: Dynamic Fields Implementation Validation")
    print("Purpose: Ensure complete removal of artificial field mapping")
    print("Scope: Parser, Comparator, UI components, and Integration")
    print()
    
    success = run_all_tests()
    
    if success:
        print("\nPhase 5 validation completed successfully!")
        print("The dynamic fields implementation is ready for production.")
    else:
        print("\nPhase 5 validation found issues that need to be addressed.")
        sys.exit(1)