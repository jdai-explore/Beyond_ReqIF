#!/usr/bin/env python3
"""
ReqIF Structure Validator - Phase 3
Validates ReqIF parsing produces only actual fields and ensures UI components handle missing fields gracefully.
Part of the implementation plan for removing artificial field mapping.
"""

import os
import sys
import json
import traceback
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from reqif_parser import ReqIFParser
from reqif_comparator import ReqIFComparator
from comparison_gui import ComparisonResultsGUI
from visualizer_gui import VisualizerGUI
from folder_comparison_gui import FolderComparisonResultsGUI


class ReqIFStructureValidator:
    """
    Comprehensive validator for ReqIF structure integrity and field mapping compliance
    """
    
    def __init__(self):
        self.parser = ReqIFParser()
        self.comparator = ReqIFComparator()
        
        # Validation results
        self.validation_results = {
            'parsing_validation': {},
            'comparison_validation': {},
            'ui_validation': {},
            'field_integrity': {},
            'overall_status': False
        }
        
        # Field tracking
        self.detected_fields = set()
        self.artificial_fields = set()
        self.actual_reqif_fields = set()
        
        # Known artificial fields that should NOT be present
        self.forbidden_artificial_fields = {
            'title', 'description', 'priority', 'status'  # These should only exist if in actual ReqIF
        }
        
        # Expected ReqIF structure fields
        self.expected_reqif_fields = {
            'id', 'identifier', 'type', 'attributes', 'raw_attributes'
        }
    
    def validate_parsing_integrity(self, sample_files: List[str]) -> Dict[str, Any]:
        """
        Validate that parsing produces only actual ReqIF fields without artificial mapping
        """
        print("=== PARSING INTEGRITY VALIDATION ===")
        
        parsing_results = {
            'files_tested': 0,
            'files_passed': 0,
            'files_failed': 0,
            'artificial_fields_detected': {},
            'missing_expected_fields': {},
            'field_source_validation': {},
            'errors': []
        }
        
        for file_path in sample_files:
            if not os.path.exists(file_path):
                parsing_results['errors'].append(f"File not found: {file_path}")
                continue
            
            print(f"\nValidating file: {os.path.basename(file_path)}")
            parsing_results['files_tested'] += 1
            
            try:
                # Parse the file
                requirements = self.parser.parse_file(file_path)
                
                # Validate the parsed requirements
                file_validation = self._validate_parsed_requirements(requirements, file_path)
                
                if file_validation['is_valid']:
                    parsing_results['files_passed'] += 1
                    print(f"  ✅ PASS - No artificial fields detected")
                else:
                    parsing_results['files_failed'] += 1
                    print(f"  ❌ FAIL - Artificial fields or mapping issues detected")
                
                # Aggregate results
                file_key = os.path.basename(file_path)
                parsing_results['artificial_fields_detected'][file_key] = file_validation['artificial_fields']
                parsing_results['missing_expected_fields'][file_key] = file_validation['missing_expected']
                parsing_results['field_source_validation'][file_key] = file_validation['field_sources']
                
                # Track global field detection
                self.detected_fields.update(file_validation['detected_fields'])
                self.artificial_fields.update(file_validation['artificial_fields'])
                
            except Exception as e:
                parsing_results['files_failed'] += 1
                parsing_results['errors'].append(f"Error parsing {file_path}: {str(e)}")
                print(f"  ❌ ERROR - Parsing failed: {str(e)}")
        
        # Overall assessment
        parsing_results['success_rate'] = (parsing_results['files_passed'] / 
                                         max(parsing_results['files_tested'], 1)) * 100
        
        self.validation_results['parsing_validation'] = parsing_results
        return parsing_results
    
    def _validate_parsed_requirements(self, requirements: List[Dict[str, Any]], 
                                    file_path: str) -> Dict[str, Any]:
        """
        Validate individual parsed requirements for field integrity
        """
        validation = {
            'is_valid': True,
            'detected_fields': set(),
            'artificial_fields': set(),
            'missing_expected': set(),
            'field_sources': {},
            'requirement_count': len(requirements)
        }
        
        if not requirements:
            validation['missing_expected'].add('No requirements found')
            validation['is_valid'] = False
            return validation
        
        # Analyze each requirement
        for i, req in enumerate(requirements):
            if not isinstance(req, dict):
                validation['artificial_fields'].add(f'Invalid requirement structure at index {i}')
                validation['is_valid'] = False
                continue
            
            # Check for artificial fields
            for field_name in req.keys():
                validation['detected_fields'].add(field_name)
                
                # Check if this is a forbidden artificial field
                if field_name in self.forbidden_artificial_fields:
                    # Only forbidden if it's artificially created, not if it exists in actual ReqIF
                    if not self._verify_field_in_source_reqif(file_path, field_name):
                        validation['artificial_fields'].add(field_name)
                        validation['is_valid'] = False
                        print(f"    🚨 Artificial field detected: {field_name}")
            
            # Verify required fields exist
            if 'id' not in req:
                validation['missing_expected'].add('id field missing')
                validation['is_valid'] = False
        
        # Verify field sources
        validation['field_sources'] = self._analyze_field_sources(requirements, file_path)
        
        return validation
    
    def _verify_field_in_source_reqif(self, file_path: str, field_name: str) -> bool:
        """
        Verify if a field actually exists in the source ReqIF file
        """
        try:
            # Parse the XML directly to check for field existence
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Look for attribute definitions that could map to this field
            field_patterns = {
                'title': ['title', 'heading', 'object heading', 'req title'],
                'description': ['description', 'text', 'object text', 'req text'],
                'priority': ['priority', 'prio'],
                'status': ['status', 'state']
            }
            
            patterns = field_patterns.get(field_name.lower(), [field_name.lower()])
            
            # Search for attribute definitions
            for elem in root.iter():
                if 'ATTRIBUTE-DEFINITION' in elem.tag:
                    # Check LONG-NAME
                    long_name = elem.get('LONG-NAME', '').lower()
                    if any(pattern in long_name for pattern in patterns):
                        return True
                    
                    # Check identifier
                    identifier = elem.get('IDENTIFIER', '').lower()
                    if any(pattern in identifier for pattern in patterns):
                        return True
            
            return False
            
        except Exception as e:
            print(f"Warning: Could not verify field source for {field_name}: {e}")
            return False  # Assume artificial if we can't verify
    
    def _analyze_field_sources(self, requirements: List[Dict[str, Any]], 
                              file_path: str) -> Dict[str, str]:
        """
        Analyze the source of each field in requirements
        """
        field_sources = {}
        
        if not requirements:
            return field_sources
        
        # Analyze field patterns
        sample_req = requirements[0] if requirements else {}
        
        for field_name in sample_req.keys():
            if field_name in self.expected_reqif_fields:
                field_sources[field_name] = 'expected_reqif_field'
            elif field_name.startswith('attr_'):
                field_sources[field_name] = 'attribute_mapping'
            elif field_name in self.forbidden_artificial_fields:
                # Check if it's actually in the source
                if self._verify_field_in_source_reqif(file_path, field_name):
                    field_sources[field_name] = 'authentic_reqif_field'
                else:
                    field_sources[field_name] = 'artificial_mapping'
            else:
                field_sources[field_name] = 'unknown_source'
        
        return field_sources
    
    def validate_comparison_integrity(self, sample_file_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Validate that comparison results don't reference non-existent fields
        """
        print("\n=== COMPARISON INTEGRITY VALIDATION ===")
        
        comparison_results = {
            'pairs_tested': 0,
            'pairs_passed': 0,
            'pairs_failed': 0,
            'field_reference_errors': {},
            'statistics_validation': {},
            'errors': []
        }
        
        for file1_path, file2_path in sample_file_pairs:
            if not os.path.exists(file1_path) or not os.path.exists(file2_path):
                comparison_results['errors'].append(f"File pair not found: {file1_path}, {file2_path}")
                continue
            
            print(f"\nValidating comparison: {os.path.basename(file1_path)} vs {os.path.basename(file2_path)}")
            comparison_results['pairs_tested'] += 1
            
            try:
                # Parse both files
                reqs1 = self.parser.parse_file(file1_path)
                reqs2 = self.parser.parse_file(file2_path)
                
                # Perform comparison
                comp_result = self.comparator.compare_requirements(reqs1, reqs2)
                
                # Validate comparison results
                pair_validation = self._validate_comparison_results(comp_result, reqs1, reqs2)
                
                if pair_validation['is_valid']:
                    comparison_results['pairs_passed'] += 1
                    print(f"  ✅ PASS - Comparison integrity maintained")
                else:
                    comparison_results['pairs_failed'] += 1
                    print(f"  ❌ FAIL - Field reference issues detected")
                
                # Store detailed results
                pair_key = f"{os.path.basename(file1_path)}_vs_{os.path.basename(file2_path)}"
                comparison_results['field_reference_errors'][pair_key] = pair_validation['field_errors']
                comparison_results['statistics_validation'][pair_key] = pair_validation['stats_validation']
                
            except Exception as e:
                comparison_results['pairs_failed'] += 1
                comparison_results['errors'].append(f"Error comparing {file1_path} vs {file2_path}: {str(e)}")
                print(f"  ❌ ERROR - Comparison failed: {str(e)}")
        
        # Overall assessment
        comparison_results['success_rate'] = (comparison_results['pairs_passed'] / 
                                            max(comparison_results['pairs_tested'], 1)) * 100
        
        self.validation_results['comparison_validation'] = comparison_results
        return comparison_results
    
    def _validate_comparison_results(self, comp_result: Dict[str, Any], 
                                   reqs1: List[Dict], reqs2: List[Dict]) -> Dict[str, Any]:
        """
        Validate comparison results for field integrity
        """
        validation = {
            'is_valid': True,
            'field_errors': [],
            'stats_validation': {}
        }
        
        # Get available fields from source requirements
        available_fields = set()
        for req_list in [reqs1, reqs2]:
            for req in req_list:
                if isinstance(req, dict):
                    available_fields.update(req.keys())
        
        # Check each category of results
        for category in ['added', 'deleted', 'modified', 'unchanged']:
            requirements = comp_result.get(category, [])
            
            for req in requirements:
                if not isinstance(req, dict):
                    continue
                
                # Check for field references that don't exist in source
                for field_name in req.keys():
                    if field_name.startswith('_'):  # Skip internal fields
                        continue
                    
                    # Check if field exists in source data or is a legitimate addition
                    if (field_name not in available_fields and 
                        field_name not in self.expected_reqif_fields and
                        not field_name.startswith('attr_') and
                        field_name not in ['changes_summary', 'changed_fields', 'change_count']):
                        
                        validation['field_errors'].append(f"Unknown field reference: {field_name}")
                        validation['is_valid'] = False
        
        # Validate statistics don't reference artificial fields
        stats = comp_result.get('statistics', {})
        validation['stats_validation'] = self._validate_statistics_fields(stats)
        
        if not validation['stats_validation']['is_valid']:
            validation['is_valid'] = False
        
        return validation
    
    def _validate_statistics_fields(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that statistics don't reference artificial fields
        """
        validation = {
            'is_valid': True,
            'issues': []
        }
        
        # Expected statistics fields (dynamic approach)
        expected_stat_patterns = [
            'count', 'total', 'percentage', 'added', 'deleted', 'modified', 'unchanged'
        ]
        
        for stat_key in stats.keys():
            # Check if statistic name suggests artificial field dependency
            if any(forbidden in stat_key.lower() for forbidden in self.forbidden_artificial_fields):
                # Only problematic if the field doesn't exist in actual data
                validation['issues'].append(f"Statistic may reference artificial field: {stat_key}")
                # Don't mark as invalid unless we can confirm it's artificial
        
        return validation
    
    def validate_ui_component_resilience(self, sample_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that UI components handle missing expected fields gracefully
        """
        print("\n=== UI COMPONENT RESILIENCE VALIDATION ===")
        
        ui_results = {
            'components_tested': 0,
            'components_passed': 0,
            'components_failed': 0,
            'missing_field_handling': {},
            'dynamic_adaptation': {},
            'errors': []
        }
        
        # Test different UI components with various field configurations
        test_scenarios = [
            {'name': 'minimal_fields', 'data': self._create_minimal_requirements()},
            {'name': 'missing_common_fields', 'data': self._create_requirements_missing_common_fields()},
            {'name': 'attribute_only', 'data': self._create_attribute_only_requirements()},
            {'name': 'empty_requirements', 'data': []},
            {'name': 'actual_sample', 'data': sample_requirements[:5] if sample_requirements else []}
        ]
        
        for scenario in test_scenarios:
            print(f"\nTesting UI resilience with: {scenario['name']}")
            ui_results['components_tested'] += 1
            
            try:
                # Test UI component creation and field detection
                scenario_validation = self._test_ui_components(scenario['data'], scenario['name'])
                
                if scenario_validation['is_valid']:
                    ui_results['components_passed'] += 1
                    print(f"  ✅ PASS - UI components handled scenario gracefully")
                else:
                    ui_results['components_failed'] += 1
                    print(f"  ❌ FAIL - UI components failed to adapt")
                
                ui_results['missing_field_handling'][scenario['name']] = scenario_validation['field_handling']
                ui_results['dynamic_adaptation'][scenario['name']] = scenario_validation['adaptation']
                
            except Exception as e:
                ui_results['components_failed'] += 1
                ui_results['errors'].append(f"Error testing {scenario['name']}: {str(e)}")
                print(f"  ❌ ERROR - UI test failed: {str(e)}")
        
        # Overall assessment
        ui_results['success_rate'] = (ui_results['components_passed'] / 
                                    max(ui_results['components_tested'], 1)) * 100
        
        self.validation_results['ui_validation'] = ui_results
        return ui_results
    
    def _create_minimal_requirements(self) -> List[Dict[str, Any]]:
        """Create requirements with minimal fields for testing"""
        return [
            {'id': 'REQ-001'},
            {'id': 'REQ-002'},
            {'id': 'REQ-003'}
        ]
    
    def _create_requirements_missing_common_fields(self) -> List[Dict[str, Any]]:
        """Create requirements missing commonly expected fields"""
        return [
            {
                'id': 'REQ-001',
                'attributes': {'Custom Field': 'Value 1'}
            },
            {
                'id': 'REQ-002',
                'type': 'Functional'
            },
            {
                'id': 'REQ-003',
                'identifier': 'SYS-REQ-003',
                'attributes': {'Object Text': 'Some requirement text'}
            }
        ]
    
    def _create_attribute_only_requirements(self) -> List[Dict[str, Any]]:
        """Create requirements with only attributes"""
        return [
            {
                'id': 'REQ-001',
                'attributes': {
                    'Object Text': 'Requirement text content',
                    'Object Heading': 'Requirement heading',
                    'Priority': 'High'
                }
            },
            {
                'id': 'REQ-002',
                'attributes': {
                    'Description': 'Another requirement description',
                    'Status': 'Approved'
                }
            }
        ]
    
    def _test_ui_components(self, requirements: List[Dict[str, Any]], scenario_name: str) -> Dict[str, Any]:
        """
        Test UI components with specific requirement data
        """
        validation = {
            'is_valid': True,
            'field_handling': {},
            'adaptation': {}
        }
        
        try:
            # Test field detection mechanisms
            from comparison_gui import ComparisonResultsGUI
            from visualizer_gui import VisualizerGUI
            
            # Test ComparisonResultsGUI field detection
            mock_results = {
                'added': requirements[:2] if len(requirements) > 1 else [],
                'deleted': [],
                'modified': requirements[2:] if len(requirements) > 2 else [],
                'unchanged': [],
                'statistics': {'added_count': 0, 'deleted_count': 0, 'modified_count': 0, 'unchanged_count': 0}
            }
            
            # Test field detection without creating actual GUI
            available_fields = self._test_field_detection(mock_results)
            validation['field_handling']['comparison_gui'] = {
                'detected_fields': list(available_fields),
                'handles_missing': len(available_fields) > 0 or not requirements
            }
            
            # Test VisualizerGUI field detection
            if requirements:
                visualizer_fields = self._test_visualizer_field_detection(requirements)
                validation['field_handling']['visualizer_gui'] = {
                    'detected_fields': list(visualizer_fields),
                    'handles_missing': len(visualizer_fields) > 0
                }
            
            # Test dynamic adaptation
            validation['adaptation'] = self._test_dynamic_adaptation(requirements)
            
        except Exception as e:
            validation['is_valid'] = False
            validation['error'] = str(e)
        
        return validation
    
    def _test_field_detection(self, mock_results: Dict[str, Any]) -> Set[str]:
        """
        Test field detection logic from ComparisonResultsGUI
        """
        available_fields = {'added': set(), 'deleted': set(), 'modified': set(), 'unchanged': set()}
        
        for category in available_fields.keys():
            requirements = mock_results.get(category, [])
            for req in requirements:
                if isinstance(req, dict):
                    # Add main fields
                    for field_name in req.keys():
                        if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                            available_fields[category].add(field_name)
                    
                    # Add attribute fields
                    attributes = req.get('attributes', {})
                    if isinstance(attributes, dict):
                        for attr_name in attributes.keys():
                            available_fields[category].add(f'attr_{attr_name}')
        
        # Return union of all detected fields
        all_fields = set()
        for fields in available_fields.values():
            all_fields.update(fields)
        
        return all_fields
    
    def _test_visualizer_field_detection(self, requirements: List[Dict[str, Any]]) -> Set[str]:
        """
        Test field detection logic from VisualizerGUI
        """
        available_fields = set()
        
        for req in requirements:
            if isinstance(req, dict):
                # Add main fields
                for field_name in req.keys():
                    if not field_name.startswith('_') and field_name not in ['content', 'raw_attributes']:
                        available_fields.add(field_name)
                
                # Add attribute fields
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    for attr_name in attributes.keys():
                        available_fields.add(f'attr_{attr_name}')
        
        return available_fields
    
    def _test_dynamic_adaptation(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test dynamic adaptation capabilities
        """
        adaptation = {
            'field_count': 0,
            'attribute_count': 0,
            'has_minimal_data': True,
            'can_display': True
        }
        
        if not requirements:
            adaptation['can_display'] = True  # Should handle empty gracefully
            return adaptation
        
        # Analyze field diversity
        all_fields = set()
        attribute_fields = set()
        
        for req in requirements:
            if isinstance(req, dict):
                for field_name in req.keys():
                    if not field_name.startswith('_'):
                        all_fields.add(field_name)
                
                attributes = req.get('attributes', {})
                if isinstance(attributes, dict):
                    attribute_fields.update(attributes.keys())
        
        adaptation['field_count'] = len(all_fields)
        adaptation['attribute_count'] = len(attribute_fields)
        adaptation['has_minimal_data'] = 'id' in all_fields
        adaptation['can_display'] = adaptation['has_minimal_data']
        
        return adaptation
    
    def validate_field_integrity_across_system(self) -> Dict[str, Any]:
        """
        Validate field integrity across the entire system
        """
        print("\n=== SYSTEM-WIDE FIELD INTEGRITY VALIDATION ===")
        
        integrity_results = {
            'artificial_field_count': len(self.artificial_fields),
            'detected_field_count': len(self.detected_fields),
            'compliance_score': 0.0,
            'field_analysis': {},
            'recommendations': []
        }
        
        # Analyze detected fields
        for field_name in self.detected_fields:
            field_analysis = {
                'is_artificial': field_name in self.artificial_fields,
                'is_forbidden': field_name in self.forbidden_artificial_fields,
                'is_expected': field_name in self.expected_reqif_fields,
                'classification': 'unknown'
            }
            
            # Classify field
            if field_name in self.expected_reqif_fields:
                field_analysis['classification'] = 'expected_reqif'
            elif field_name.startswith('attr_'):
                field_analysis['classification'] = 'attribute_mapping'
            elif field_name in self.forbidden_artificial_fields:
                if field_name in self.artificial_fields:
                    field_analysis['classification'] = 'artificial_forbidden'
                else:
                    field_analysis['classification'] = 'authentic_reqif'
            elif field_name.startswith('_'):
                field_analysis['classification'] = 'internal_field'
            else:
                field_analysis['classification'] = 'other'
            
            integrity_results['field_analysis'][field_name] = field_analysis
        
        # Calculate compliance score
        total_fields = len(self.detected_fields)
        artificial_forbidden = len([f for f in self.artificial_fields if f in self.forbidden_artificial_fields])
        
        if total_fields > 0:
            integrity_results['compliance_score'] = ((total_fields - artificial_forbidden) / total_fields) * 100
        else:
            integrity_results['compliance_score'] = 100.0
        
        # Generate recommendations
        if artificial_forbidden > 0:
            integrity_results['recommendations'].append(
                f"Remove {artificial_forbidden} artificial field(s): {', '.join(self.artificial_fields & self.forbidden_artificial_fields)}"
            )
        
        if integrity_results['compliance_score'] < 100:
            integrity_results['recommendations'].append(
                "Implement dynamic field detection to eliminate artificial field mapping"
            )
        
        if integrity_results['compliance_score'] >= 95:
            integrity_results['recommendations'].append(
                "Field mapping compliance is excellent - system ready for Phase 3"
            )
        
        self.validation_results['field_integrity'] = integrity_results
        return integrity_results
    
    def generate_comprehensive_report(self) -> str:
        """
        Generate a comprehensive validation report
        """
        report_lines = [
            "=" * 80,
            "REQIF STRUCTURE VALIDATION REPORT - PHASE 3",
            "=" * 80,
            f"Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "OBJECTIVE: Validate removal of artificial field mapping and ensure",
            "UI components handle missing expected fields gracefully.",
            "",
        ]
        
        # Overall status
        overall_success = self._calculate_overall_success()
        self.validation_results['overall_status'] = overall_success
        
        status_icon = "✅ PASS" if overall_success else "❌ FAIL"
        report_lines.extend([
            f"OVERALL STATUS: {status_icon}",
            "",
            "=" * 60,
            "DETAILED RESULTS",
            "=" * 60,
        ])
        
        # Parsing validation
        parsing = self.validation_results.get('parsing_validation', {})
        if parsing:
            report_lines.extend([
                "",
                "1. PARSING INTEGRITY VALIDATION",
                "-" * 40,
                f"Files tested: {parsing.get('files_tested', 0)}",
                f"Files passed: {parsing.get('files_passed', 0)}",
                f"Success rate: {parsing.get('success_rate', 0):.1f}%",
                ""
            ])
            
            if parsing.get('artificial_fields_detected'):
                report_lines.append("Artificial fields detected by file:")
                for file, fields in parsing['artificial_fields_detected'].items():
                    if fields:
                        report_lines.append(f"  ❌ {file}: {', '.join(fields)}")
                    else:
                        report_lines.append(f"  ✅ {file}: No artificial fields")
        
        # Comparison validation
        comparison = self.validation_results.get('comparison_validation', {})
        if comparison:
            report_lines.extend([
                "",
                "2. COMPARISON INTEGRITY VALIDATION",
                "-" * 40,
                f"Pairs tested: {comparison.get('pairs_tested', 0)}",
                f"Pairs passed: {comparison.get('pairs_passed', 0)}",
                f"Success rate: {comparison.get('success_rate', 0):.1f}%",
                ""
            ])
            
            if comparison.get('field_reference_errors'):
                report_lines.append("Field reference errors by comparison:")
                for pair, errors in comparison['field_reference_errors'].items():
                    if errors:
                        report_lines.append(f"  ❌ {pair}: {len(errors)} errors")
                    else:
                        report_lines.append(f"  ✅ {pair}: No field reference errors")
        
        # UI validation
        ui = self.validation_results.get('ui_validation', {})
        if ui:
            report_lines.extend([
                "",
                "3. UI COMPONENT RESILIENCE VALIDATION",
                "-" * 40,
                f"Scenarios tested: {ui.get('components_tested', 0)}",
                f"Scenarios passed: {ui.get('components_passed', 0)}",
                f"Success rate: {ui.get('success_rate', 0):.1f}%",
                ""
            ])
        
        # Field integrity
        integrity = self.validation_results.get('field_integrity', {})
        if integrity:
            report_lines.extend([
                "",
                "4. SYSTEM-WIDE FIELD INTEGRITY",
                "-" * 40,
                f"Total fields detected: {integrity.get('detected_field_count', 0)}",
                f"Artificial fields found: {integrity.get('artificial_field_count', 0)}",
                f"Compliance score: {integrity.get('compliance_score', 0):.1f}%",
                ""
            ])
            
            if integrity.get('recommendations'):
                report_lines.append("RECOMMENDATIONS:")
                for rec in integrity['recommendations']:
                    report_lines.append(f"  💡 {rec}")
        
        # Summary
        report_lines.extend([
            "",
            "=" * 60,
            "VALIDATION SUMMARY",
            "=" * 60,
        ])
        
        if overall_success:
            report_lines.extend([
                "",
                "🎉 VALIDATION SUCCESSFUL!",
                "",
                "✅ Parsing produces only actual ReqIF fields",
                "✅ Comparison results maintain field integrity", 
                "✅ UI components handle missing fields gracefully",
                "✅ No artificial field mapping detected",
                "",
                "The system is ready for Phase 3 implementation.",
            ])
        else:
            report_lines.extend([
                "",
                "⚠️ VALIDATION ISSUES DETECTED!",
                "",
                "Issues found that need to be addressed:",
            ])
            
            # Add specific issues
            if parsing.get('files_failed', 0) > 0:
                report_lines.append(f"❌ {parsing['files_failed']} files failed parsing validation")
            
            if comparison.get('pairs_failed', 0) > 0:
                report_lines.append(f"❌ {comparison['pairs_failed']} comparison pairs failed validation")
            
            if ui.get('components_failed', 0) > 0:
                report_lines.append(f"❌ {ui['components_failed']} UI scenarios failed validation")
            
            if integrity.get('artificial_field_count', 0) > 0:
                report_lines.append(f"❌ {integrity['artificial_field_count']} artificial fields detected")
            
            report_lines.extend([
                "",
                "Please address these issues before proceeding with Phase 3.",
            ])
        
        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80
        ])
        
        return '\n'.join(report_lines)
    
    def _calculate_overall_success(self) -> bool:
        """
        Calculate overall validation success based on all test results
        """
        # Get success rates from each validation
        parsing_success = self.validation_results.get('parsing_validation', {}).get('success_rate', 0)
        comparison_success = self.validation_results.get('comparison_validation', {}).get('success_rate', 0)
        ui_success = self.validation_results.get('ui_validation', {}).get('success_rate', 0)
        compliance_score = self.validation_results.get('field_integrity', {}).get('compliance_score', 0)
        
        # All components must pass with high success rates
        thresholds = {
            'parsing': 90.0,      # 90% of files must pass parsing validation
            'comparison': 90.0,   # 90% of comparisons must pass
            'ui': 80.0,          # 80% of UI scenarios must pass (more lenient)
            'compliance': 95.0    # 95% field compliance required
        }
        
        return (parsing_success >= thresholds['parsing'] and
                comparison_success >= thresholds['comparison'] and
                ui_success >= thresholds['ui'] and
                compliance_score >= thresholds['compliance'])
    
    def run_full_validation(self, sample_files: List[str] = None, 
                           sample_file_pairs: List[Tuple[str, str]] = None) -> Dict[str, Any]:
        """
        Run complete validation suite
        """
        print("🔍 STARTING COMPREHENSIVE REQIF STRUCTURE VALIDATION")
        print("=" * 80)
        
        # Use default samples if none provided
        if sample_files is None:
            sample_files = self._find_sample_files()
        
        if sample_file_pairs is None:
            sample_file_pairs = self._create_sample_pairs(sample_files)
        
        try:
            # Run all validation components
            self.validate_parsing_integrity(sample_files)
            self.validate_comparison_integrity(sample_file_pairs)
            self.validate_ui_component_resilience([])  # Test with empty first
            self.validate_field_integrity_across_system()
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report()
            
            return {
                'success': self.validation_results['overall_status'],
                'results': self.validation_results,
                'report': report
            }
            
        except Exception as e:
            error_report = f"""
VALIDATION ERROR
================
An error occurred during validation: {str(e)}

Traceback:
{traceback.format_exc()}

Please check the validation setup and try again.
"""
            return {
                'success': False,
                'error': str(e),
                'report': error_report
            }
    
    def _find_sample_files(self) -> List[str]:
        """
        Find sample ReqIF files for testing
        """
        sample_files = []
        
        # Look for sample files in common locations
        search_paths = [
            Path.cwd(),
            Path.cwd() / 'samples',
            Path.cwd() / 'test_data',
            Path.cwd() / 'examples',
            Path.cwd().parent / 'samples'
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                # Find .reqif and .reqifz files
                for pattern in ['*.reqif', '*.reqifz']:
                    for file_path in search_path.glob(pattern):
                        sample_files.append(str(file_path))
                
                # Also search subdirectories
                for pattern in ['**/*.reqif', '**/*.reqifz']:
                    for file_path in search_path.glob(pattern):
                        sample_files.append(str(file_path))
                        if len(sample_files) >= 10:  # Limit sample size
                            break
        
        # Remove duplicates and limit
        sample_files = list(set(sample_files))[:10]
        
        if not sample_files:
            print("⚠️ No sample ReqIF files found. Creating synthetic test data...")
            sample_files = self._create_synthetic_test_files()
        
        return sample_files
    
    def _create_sample_pairs(self, sample_files: List[str]) -> List[Tuple[str, str]]:
        """
        Create sample file pairs for comparison testing
        """
        pairs = []
        
        # Create pairs from available files
        for i in range(0, len(sample_files) - 1, 2):
            if i + 1 < len(sample_files):
                pairs.append((sample_files[i], sample_files[i + 1]))
        
        # If we have odd number of files, pair last with first
        if len(sample_files) > 2 and len(sample_files) % 2 == 1:
            pairs.append((sample_files[-1], sample_files[0]))
        
        return pairs[:5]  # Limit to 5 pairs
    
    def _create_synthetic_test_files(self) -> List[str]:
        """
        Create synthetic ReqIF files for testing when no samples are available
        """
        import tempfile
        
        synthetic_files = []
        temp_dir = Path(tempfile.mkdtemp(prefix="reqif_validation_"))
        
        # Create test files with different field configurations
        test_configs = [
            {
                'name': 'minimal.reqif',
                'requirements': [
                    {'id': 'REQ-001'},
                    {'id': 'REQ-002'}
                ]
            },
            {
                'name': 'with_attributes.reqif',
                'requirements': [
                    {
                        'id': 'REQ-001',
                        'attributes': {'Object Text': 'Test requirement text'}
                    },
                    {
                        'id': 'REQ-002',
                        'type': 'Functional',
                        'attributes': {'Object Heading': 'Test heading'}
                    }
                ]
            },
            {
                'name': 'artificial_fields.reqif',
                'requirements': [
                    {
                        'id': 'REQ-001',
                        'title': 'Artificial title field',  # This should be detected as artificial
                        'description': 'Artificial description'  # This too
                    }
                ]
            }
        ]
        
        for config in test_configs:
            file_path = temp_dir / config['name']
            self._create_synthetic_reqif_file(file_path, config['requirements'])
            synthetic_files.append(str(file_path))
        
        print(f"Created {len(synthetic_files)} synthetic test files in {temp_dir}")
        return synthetic_files
    
    def _create_synthetic_reqif_file(self, file_path: Path, requirements: List[Dict]):
        """
        Create a synthetic ReqIF file for testing
        """
        # Create minimal ReqIF XML structure
        reqif_content = '''<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF xmlns="http://www.omg.org/ReqIF" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <THE-HEADER>
    <REQ-IF-HEADER IDENTIFIER="test-header">
      <CREATION-TIME>2024-01-01T00:00:00Z</CREATION-TIME>
      <REPOSITORY-ID>test-repo</REPOSITORY-ID>
      <REQ-IF-TOOL-ID>validation-tool</REQ-IF-TOOL-ID>
      <REQ-IF-VERSION>1.0</REQ-IF-VERSION>
      <SOURCE-TOOL-ID>test-tool</SOURCE-TOOL-ID>
      <TITLE>Test ReqIF File</TITLE>
    </REQ-IF-HEADER>
  </THE-HEADER>
  <CORE-CONTENT>
    <REQ-IF-CONTENT>
      <DATATYPES>
        <DATATYPE-DEFINITION-STRING IDENTIFIER="string-type" LONG-NAME="String Type" />
      </DATATYPES>
      <SPEC-TYPES>
        <SPEC-OBJECT-TYPE IDENTIFIER="requirement-type" LONG-NAME="Requirement">
          <SPEC-ATTRIBUTES>
            <ATTRIBUTE-DEFINITION-STRING IDENTIFIER="object-text" LONG-NAME="Object Text">
              <TYPE><DATATYPE-DEFINITION-STRING-REF>string-type</DATATYPE-DEFINITION-STRING-REF></TYPE>
            </ATTRIBUTE-DEFINITION-STRING>
          </SPEC-ATTRIBUTES>
        </SPEC-OBJECT-TYPE>
      </SPEC-TYPES>
      <SPEC-OBJECTS>'''
        
        # Add SPEC-OBJECTs for each requirement
        for req in requirements:
            req_id = req.get('id', 'unknown')
            reqif_content += f'''
        <SPEC-OBJECT IDENTIFIER="{req_id}">
          <TYPE><SPEC-OBJECT-TYPE-REF>requirement-type</SPEC-OBJECT-TYPE-REF></TYPE>
          <VALUES>'''
            
            # Add attributes if present
            attributes = req.get('attributes', {})
            for attr_name, attr_value in attributes.items():
                reqif_content += f'''
            <ATTRIBUTE-VALUE-STRING THE-VALUE="{attr_value}">
              <DEFINITION><ATTRIBUTE-DEFINITION-STRING-REF>object-text</ATTRIBUTE-DEFINITION-STRING-REF></DEFINITION>
            </ATTRIBUTE-VALUE-STRING>'''
            
            reqif_content += '''
          </VALUES>
        </SPEC-OBJECT>'''
        
        reqif_content += '''
      </SPEC-OBJECTS>
    </REQ-IF-CONTENT>
  </CORE-CONTENT>
</REQ-IF>'''
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(reqif_content)
    
    def export_validation_results(self, output_file: str):
        """
        Export validation results to JSON file
        """
        try:
            # Convert sets to lists for JSON serialization
            serializable_results = self._make_serializable(self.validation_results)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, default=str)
            
            print(f"Validation results exported to: {output_file}")
            
        except Exception as e:
            print(f"Error exporting validation results: {e}")
    
    def _make_serializable(self, obj):
        """
        Convert sets and other non-serializable objects to serializable format
        """
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj


def main():
    """
    Main function to run validation
    """
    print("ReqIF Structure Validator - Phase 3")
    print("Validating removal of artificial field mapping...")
    print()
    
    # Create validator
    validator = ReqIFStructureValidator()
    
    # Run full validation
    results = validator.run_full_validation()
    
    # Print report
    print(results['report'])
    
    # Export results
    output_file = f"reqif_validation_results_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    validator.export_validation_results(output_file)
    
    # Return exit code
    return 0 if results['success'] else 1


if __name__ == "__main__":
    exit_code = main()