#!/usr/bin/env python3
"""
ReqIF Deep Diagnostics Tool
Comprehensive analysis of ReqIF file structure and parsing issues.
Run this to understand exactly what's happening with your ReqIF files.
"""

import xml.etree.ElementTree as ET
import zipfile
import tempfile
import shutil
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import re
import html


class ReqIFDiagnostics:
    """Comprehensive ReqIF file diagnostics and analysis"""
    
    def __init__(self):
        self.file_path = None
        self.root = None
        self.namespaces = {}
        self.findings = {
            'file_info': {},
            'structure': {},
            'namespaces': {},
            'elements': {},
            'spec_objects': [],
            'definitions': {},
            'parsing_attempts': {},
            'content_samples': {},
            'issues': [],
            'recommendations': []
        }
    
    def analyze_file(self, file_path: str):
        """Complete diagnostic analysis of a ReqIF file"""
        print("🔍 REQIF DEEP DIAGNOSTICS")
        print("=" * 80)
        
        self.file_path = file_path
        
        # Phase 1: File Analysis
        print("📁 Phase 1: File Structure Analysis")
        self._analyze_file_structure()
        
        # Phase 2: XML Structure Analysis
        print("\n📋 Phase 2: XML Structure Analysis")
        self._analyze_xml_structure()
        
        # Phase 3: Namespace Analysis
        print("\n🏷️ Phase 3: Namespace Analysis")
        self._analyze_namespaces()
        
        # Phase 4: Element Discovery
        print("\n🔍 Phase 4: Element Discovery Analysis")
        self._analyze_element_discovery()
        
        # Phase 5: ReqIF Object Analysis
        print("\n⚙️ Phase 5: ReqIF Object Structure Analysis")
        self._analyze_reqif_objects()
        
        # Phase 6: Content Extraction Testing
        print("\n📄 Phase 6: Content Extraction Testing")
        self._test_content_extraction()
        
        # Phase 7: Reference Resolution Analysis
        print("\n🔗 Phase 7: Reference Resolution Analysis")
        self._analyze_reference_resolution()
        
        # Phase 8: Generate Report
        print("\n📊 Phase 8: Generating Comprehensive Report")
        self._generate_diagnostic_report()
        
        return self.findings
    
    def _analyze_file_structure(self):
        """Analyze basic file structure"""
        if not os.path.exists(self.file_path):
            self.findings['issues'].append(f"File not found: {self.file_path}")
            return
        
        file_info = {
            'path': self.file_path,
            'name': os.path.basename(self.file_path),
            'size': os.path.getsize(self.file_path),
            'extension': os.path.splitext(self.file_path)[1].lower()
        }
        
        print(f"  📄 File: {file_info['name']}")
        print(f"  📏 Size: {file_info['size']:,} bytes")
        print(f"  🏷️ Extension: {file_info['extension']}")
        
        # Handle ReqIFZ archives
        if file_info['extension'] == '.reqifz':
            print(f"  📦 Archive detected - extracting...")
            file_info['is_archive'] = True
            file_info['contained_files'] = self._analyze_archive()
        else:
            file_info['is_archive'] = False
        
        self.findings['file_info'] = file_info
    
    def _analyze_archive(self):
        """Analyze ReqIFZ archive contents"""
        temp_dir = tempfile.mkdtemp()
        contained_files = []
        
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find all files in archive
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir)
                    file_size = os.path.getsize(file_path)
                    
                    contained_files.append({
                        'name': file,
                        'path': rel_path,
                        'size': file_size,
                        'is_reqif': file.lower().endswith('.reqif')
                    })
                    
                    print(f"    📄 {rel_path} ({file_size:,} bytes)")
            
            # Update file path to point to main ReqIF file
            reqif_files = [f for f in contained_files if f['is_reqif']]
            if reqif_files:
                # Use the largest ReqIF file as main
                main_reqif = max(reqif_files, key=lambda x: x['size'])
                self.file_path = os.path.join(temp_dir, main_reqif['path'])
                print(f"  ✅ Using main ReqIF: {main_reqif['name']}")
            else:
                self.findings['issues'].append("No .reqif files found in archive")
        
        except Exception as e:
            self.findings['issues'].append(f"Archive extraction failed: {str(e)}")
        
        return contained_files
    
    def _analyze_xml_structure(self):
        """Analyze XML structure and validity"""
        try:
            # Parse XML
            tree = ET.parse(self.file_path)
            self.root = tree.getroot()
            
            structure = {
                'valid_xml': True,
                'root_tag': self.root.tag,
                'root_attributes': dict(self.root.attrib),
                'total_elements': len(list(self.root.iter())),
                'max_depth': self._calculate_max_depth(self.root)
            }
            
            print(f"  ✅ Valid XML structure")
            print(f"  🏷️ Root tag: {structure['root_tag']}")
            print(f"  📊 Total elements: {structure['total_elements']:,}")
            print(f"  📏 Max depth: {structure['max_depth']}")
            print(f"  ⚙️ Root attributes: {len(structure['root_attributes'])}")
            
            # Analyze root attributes
            for key, value in structure['root_attributes'].items():
                if key.startswith('xmlns'):
                    print(f"    🏷️ {key}: {value}")
            
            self.findings['structure'] = structure
            
        except ET.ParseError as e:
            self.findings['issues'].append(f"XML parsing failed: {str(e)}")
            self.findings['structure'] = {'valid_xml': False, 'error': str(e)}
        except Exception as e:
            self.findings['issues'].append(f"File analysis failed: {str(e)}")
    
    def _calculate_max_depth(self, element, current_depth=0):
        """Calculate maximum XML depth"""
        if not element:
            return current_depth
        
        max_depth = current_depth
        for child in element:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _analyze_namespaces(self):
        """Comprehensive namespace analysis"""
        if not self.root:
            return
        
        # Extract all namespaces
        namespaces = {}
        
        # From root attributes
        for key, value in self.root.attrib.items():
            if key.startswith('xmlns'):
                if key == 'xmlns':
                    namespaces['default'] = value
                else:
                    prefix = key.split(':', 1)[1]
                    namespaces[prefix] = value
        
        # Detect namespace from root tag
        root_namespace = None
        if '}' in self.root.tag:
            root_namespace = self.root.tag.split('}')[0][1:]  # Remove { }
            if 'default' not in namespaces:
                namespaces['detected_default'] = root_namespace
        
        self.namespaces = namespaces
        
        print(f"  🏷️ Namespaces found: {len(namespaces)}")
        for prefix, uri in namespaces.items():
            print(f"    {prefix}: {uri}")
        
        if root_namespace:
            print(f"  🔍 Root element namespace: {root_namespace}")
        
        # Test namespace registration
        namespace_tests = {}
        for prefix, uri in namespaces.items():
            try:
                ET.register_namespace(prefix if prefix != 'default' else '', uri)
                namespace_tests[prefix] = 'registered'
            except Exception as e:
                namespace_tests[prefix] = f'failed: {str(e)}'
        
        self.findings['namespaces'] = {
            'found': namespaces,
            'root_namespace': root_namespace,
            'registration_tests': namespace_tests
        }
    
    def _analyze_element_discovery(self):
        """Test different element discovery methods"""
        if not self.root:
            return
        
        # Key ReqIF elements to search for
        target_elements = [
            'SPEC-OBJECT',
            'ATTRIBUTE-DEFINITION-STRING',
            'ATTRIBUTE-DEFINITION-XHTML',
            'ATTRIBUTE-DEFINITION-ENUMERATION',
            'SPEC-OBJECT-TYPE',
            'ATTRIBUTE-VALUE-STRING',
            'ATTRIBUTE-VALUE-XHTML',
            'ATTRIBUTE-VALUE-ENUMERATION'
        ]
        
        discovery_results = {}
        
        for element_name in target_elements:
            print(f"  🔍 Testing discovery for: {element_name}")
            
            methods = {}
            
            # Method 1: Direct search
            try:
                found = self.root.findall(f".//{element_name}")
                methods['direct'] = len(found)
                print(f"    Direct: {len(found)}")
            except Exception as e:
                methods['direct'] = f"failed: {str(e)}"
            
            # Method 2: With default namespace
            if 'default' in self.namespaces:
                try:
                    ns_element = f"{{{self.namespaces['default']}}}{element_name}"
                    found = self.root.findall(f".//{ns_element}")
                    methods['with_default_ns'] = len(found)
                    print(f"    With default NS: {len(found)}")
                except Exception as e:
                    methods['with_default_ns'] = f"failed: {str(e)}"
            
            # Method 3: With reqif namespace
            if 'reqif' in self.namespaces:
                try:
                    found = self.root.findall(f".//reqif:{element_name}", {'reqif': self.namespaces['reqif']})
                    methods['with_reqif_ns'] = len(found)
                    print(f"    With reqif NS: {len(found)}")
                except Exception as e:
                    methods['with_reqif_ns'] = f"failed: {str(e)}"
            
            # Method 4: Case insensitive search
            try:
                all_elements = [elem.tag for elem in self.root.iter()]
                case_insensitive_count = sum(1 for tag in all_elements 
                                           if element_name.lower() in tag.lower())
                methods['case_insensitive'] = case_insensitive_count
                print(f"    Case insensitive: {case_insensitive_count}")
            except Exception as e:
                methods['case_insensitive'] = f"failed: {str(e)}"
            
            # Method 5: Pattern matching
            try:
                pattern_count = sum(1 for elem in self.root.iter() 
                                  if element_name in elem.tag)
                methods['pattern_match'] = pattern_count
                print(f"    Pattern match: {pattern_count}")
            except Exception as e:
                methods['pattern_match'] = f"failed: {str(e)}"
            
            discovery_results[element_name] = methods
            
            # Report best method
            successful_methods = {k: v for k, v in methods.items() 
                                if isinstance(v, int) and v > 0}
            if successful_methods:
                best_method = max(successful_methods.items(), key=lambda x: x[1])
                print(f"    ✅ Best: {best_method[0]} ({best_method[1]} found)")
            else:
                print(f"    ❌ No elements found with any method")
        
        self.findings['elements'] = discovery_results
    
    def _analyze_reqif_objects(self):
        """Analyze SPEC-OBJECT structure in detail"""
        if not self.root:
            return
        
        # Find SPEC-OBJECT elements using best method
        spec_objects = self._find_elements_best_method('SPEC-OBJECT')
        
        print(f"  📊 Found {len(spec_objects)} SPEC-OBJECT elements")
        
        if not spec_objects:
            self.findings['issues'].append("No SPEC-OBJECT elements found")
            return
        
        # Analyze first few SPEC-OBJECTs in detail
        analyzed_objects = []
        
        for i, spec_obj in enumerate(spec_objects[:3]):  # Analyze first 3
            print(f"\n  📋 Analyzing SPEC-OBJECT {i+1}:")
            
            obj_analysis = {
                'index': i,
                'tag': spec_obj.tag,
                'attributes': dict(spec_obj.attrib),
                'identifier': self._extract_identifier(spec_obj),
                'children': [],
                'values_container': None,
                'attribute_values': []
            }
            
            print(f"    🆔 Identifier: {obj_analysis['identifier']}")
            print(f"    🏷️ Tag: {obj_analysis['tag']}")
            print(f"    ⚙️ Attributes: {len(obj_analysis['attributes'])}")
            
            # Analyze children
            for child in spec_obj:
                child_info = {
                    'tag': child.tag,
                    'text': (child.text or '').strip()[:50],
                    'attributes': dict(child.attrib),
                    'children_count': len(list(child))
                }
                obj_analysis['children'].append(child_info)
                print(f"    📄 Child: {child.tag} (attrs: {len(child_info['attributes'])}, children: {child_info['children_count']})")
            
            # Look for VALUES container
            values_container = self._find_child_element(spec_obj, 'VALUES')
            if values_container is not None:
                obj_analysis['values_container'] = {
                    'found': True,
                    'children_count': len(list(values_container)),
                    'children_tags': [child.tag for child in values_container]
                }
                print(f"    ✅ VALUES container found ({len(list(values_container))} children)")
                
                # Analyze attribute values
                attr_values = self._find_attribute_values(values_container)
                obj_analysis['attribute_values'] = attr_values
                print(f"    📊 Attribute values found: {len(attr_values)}")
                
                for j, attr_val in enumerate(attr_values[:3]):  # Show first 3
                    print(f"      📝 Value {j+1}: {attr_val['type']} -> {attr_val['sample_content'][:30]}...")
            else:
                obj_analysis['values_container'] = {'found': False}
                print(f"    ❌ VALUES container not found")
            
            analyzed_objects.append(obj_analysis)
        
        self.findings['spec_objects'] = analyzed_objects
    
    def _test_content_extraction(self):
        """Test various content extraction methods"""
        if not self.root:
            return
        
        print(f"  🧪 Testing content extraction methods...")
        
        # Find some attribute value elements to test
        test_elements = []
        
        # Find different types of attribute values
        value_types = ['ATTRIBUTE-VALUE-STRING', 'ATTRIBUTE-VALUE-XHTML', 'ATTRIBUTE-VALUE-ENUMERATION']
        
        for value_type in value_types:
            elements = self._find_elements_best_method(value_type)
            if elements:
                test_elements.extend(elements[:2])  # Take first 2 of each type
        
        extraction_results = []
        
        for i, element in enumerate(test_elements[:5]):  # Test max 5 elements
            print(f"\n    🔬 Testing element {i+1}: {element.tag}")
            
            extraction_test = {
                'tag': element.tag,
                'methods': {},
                'raw_xml': ET.tostring(element, encoding='unicode')[:200] + '...'
            }
            
            # Method 1: Direct text
            try:
                direct_text = (element.text or '').strip()
                extraction_test['methods']['direct_text'] = direct_text[:100]
                print(f"      Direct text: '{direct_text[:50]}'")
            except Exception as e:
                extraction_test['methods']['direct_text'] = f"failed: {str(e)}"
            
            # Method 2: THE-VALUE attribute
            try:
                the_value_attr = element.get('THE-VALUE') or element.get('the-value')
                extraction_test['methods']['the_value_attr'] = the_value_attr or 'None'
                print(f"      THE-VALUE attr: '{(the_value_attr or '')[:50]}'")
            except Exception as e:
                extraction_test['methods']['the_value_attr'] = f"failed: {str(e)}"
            
            # Method 3: THE-VALUE child element
            try:
                the_value_elem = (element.find('.//THE-VALUE') or 
                                element.find('.//the-value'))
                if the_value_elem is not None:
                    content = self._extract_all_text(the_value_elem)
                    extraction_test['methods']['the_value_child'] = content[:100]
                    print(f"      THE-VALUE child: '{content[:50]}'")
                else:
                    extraction_test['methods']['the_value_child'] = 'Not found'
                    print(f"      THE-VALUE child: Not found")
            except Exception as e:
                extraction_test['methods']['the_value_child'] = f"failed: {str(e)}"
            
            # Method 4: All text extraction
            try:
                all_text = self._extract_all_text(element)
                extraction_test['methods']['all_text'] = all_text[:100]
                print(f"      All text: '{all_text[:50]}'")
            except Exception as e:
                extraction_test['methods']['all_text'] = f"failed: {str(e)}"
            
            # Method 5: For XHTML - try XHTML-specific extraction
            if 'XHTML' in element.tag:
                try:
                    xhtml_content = self._extract_xhtml_content(element)
                    extraction_test['methods']['xhtml_specific'] = xhtml_content[:100]
                    print(f"      XHTML specific: '{xhtml_content[:50]}'")
                except Exception as e:
                    extraction_test['methods']['xhtml_specific'] = f"failed: {str(e)}"
            
            extraction_results.append(extraction_test)
        
        self.findings['content_samples'] = extraction_results
    
    def _analyze_reference_resolution(self):
        """Analyze reference resolution chains"""
        if not self.root:
            return
        
        print(f"  🔗 Analyzing reference resolution...")
        
        # Build catalogs
        print(f"    📚 Building definition catalogs...")
        
        definitions = {}
        
        # Find attribute definitions
        def_types = ['ATTRIBUTE-DEFINITION-STRING', 'ATTRIBUTE-DEFINITION-XHTML', 
                    'ATTRIBUTE-DEFINITION-ENUMERATION', 'ATTRIBUTE-DEFINITION-INTEGER',
                    'ATTRIBUTE-DEFINITION-REAL', 'ATTRIBUTE-DEFINITION-BOOLEAN']
        
        for def_type in def_types:
            elements = self._find_elements_best_method(def_type)
            print(f"      {def_type}: {len(elements)} found")
            
            for elem in elements:
                identifier = self._extract_identifier(elem)
                if identifier:
                    definitions[identifier] = {
                        'type': def_type,
                        'element': elem,
                        'long_name': self._extract_long_name(elem)
                    }
        
        print(f"    📊 Total definitions cataloged: {len(definitions)}")
        
        # Find spec object types
        spec_types = {}
        type_elements = self._find_elements_best_method('SPEC-OBJECT-TYPE')
        print(f"    🏷️ SPEC-OBJECT-TYPE elements: {len(type_elements)}")
        
        for elem in type_elements:
            identifier = self._extract_identifier(elem)
            if identifier:
                spec_types[identifier] = {
                    'element': elem,
                    'long_name': self._extract_long_name(elem)
                }
        
        # Test reference resolution
        spec_objects = self._find_elements_best_method('SPEC-OBJECT')
        resolution_tests = []
        
        for i, spec_obj in enumerate(spec_objects[:3]):  # Test first 3
            print(f"\n    🧪 Testing resolution for SPEC-OBJECT {i+1}:")
            
            test_result = {
                'spec_object_id': self._extract_identifier(spec_obj),
                'type_resolution': None,
                'attribute_resolutions': []
            }
            
            # Test type resolution
            type_ref = self._extract_type_reference(spec_obj)
            if type_ref:
                if type_ref in spec_types:
                    test_result['type_resolution'] = {
                        'reference': type_ref,
                        'resolved': True,
                        'name': spec_types[type_ref]['long_name']
                    }
                    print(f"      ✅ Type resolved: {type_ref} -> {spec_types[type_ref]['long_name']}")
                else:
                    test_result['type_resolution'] = {
                        'reference': type_ref,
                        'resolved': False
                    }
                    print(f"      ❌ Type not resolved: {type_ref}")
            else:
                print(f"      ⚠️ No type reference found")
            
            # Test attribute value resolution
            values_container = self._find_child_element(spec_obj, 'VALUES')
            if values_container:
                attr_values = self._find_attribute_values(values_container)
                
                for attr_val in attr_values[:3]:  # Test first 3
                    attr_def_ref = self._extract_attribute_definition_ref(attr_val['element'])
                    
                    resolution = {
                        'definition_ref': attr_def_ref,
                        'resolved': False,
                        'definition_name': None,
                        'content_extracted': False,
                        'content_sample': None
                    }
                    
                    if attr_def_ref and attr_def_ref in definitions:
                        resolution['resolved'] = True
                        resolution['definition_name'] = definitions[attr_def_ref]['long_name']
                        print(f"      ✅ Attribute resolved: {attr_def_ref} -> {resolution['definition_name']}")
                    else:
                        print(f"      ❌ Attribute not resolved: {attr_def_ref}")
                    
                    # Test content extraction
                    content = self._extract_all_text(attr_val['element'])
                    if content.strip():
                        resolution['content_extracted'] = True
                        resolution['content_sample'] = content[:50]
                        print(f"        📄 Content: '{content[:30]}...'")
                    else:
                        print(f"        ❌ No content extracted")
                    
                    test_result['attribute_resolutions'].append(resolution)
            
            resolution_tests.append(test_result)
        
        self.findings['parsing_attempts'] = {
            'definitions_found': len(definitions),
            'spec_types_found': len(spec_types),
            'resolution_tests': resolution_tests
        }
    
    def _generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append("REQIF DEEP DIAGNOSTICS REPORT")
        report_lines.append("=" * 80)
        
        # File Information
        report_lines.append("\n📁 FILE INFORMATION")
        report_lines.append("-" * 40)
        file_info = self.findings['file_info']
        report_lines.append(f"File: {file_info.get('name', 'Unknown')}")
        report_lines.append(f"Size: {file_info.get('size', 0):,} bytes")
        report_lines.append(f"Type: {'Archive' if file_info.get('is_archive') else 'Single ReqIF'}")
        
        # XML Structure
        if self.findings['structure'].get('valid_xml'):
            report_lines.append(f"\n📋 XML STRUCTURE")
            report_lines.append("-" * 40)
            structure = self.findings['structure']
            report_lines.append(f"Root tag: {structure['root_tag']}")
            report_lines.append(f"Total elements: {structure['total_elements']:,}")
            report_lines.append(f"Max depth: {structure['max_depth']}")
        
        # Namespace Analysis
        report_lines.append(f"\n🏷️ NAMESPACE ANALYSIS")
        report_lines.append("-" * 40)
        namespaces = self.findings['namespaces']['found']
        for prefix, uri in namespaces.items():
            report_lines.append(f"{prefix}: {uri}")
        
        # Element Discovery Results
        report_lines.append(f"\n🔍 ELEMENT DISCOVERY RESULTS")
        report_lines.append("-" * 40)
        elements = self.findings['elements']
        for element_name, methods in elements.items():
            successful = [f"{method}: {count}" for method, count in methods.items() 
                         if isinstance(count, int) and count > 0]
            if successful:
                report_lines.append(f"✅ {element_name}: {', '.join(successful)}")
            else:
                report_lines.append(f"❌ {element_name}: No elements found")
        
        # Content Extraction Results
        if self.findings['content_samples']:
            report_lines.append(f"\n📄 CONTENT EXTRACTION SAMPLES")
            report_lines.append("-" * 40)
            for i, sample in enumerate(self.findings['content_samples']):
                report_lines.append(f"\nSample {i+1} ({sample['tag']}):")
                for method, result in sample['methods'].items():
                    if result and not result.startswith('failed'):
                        report_lines.append(f"  ✅ {method}: '{result[:50]}...'")
                    else:
                        report_lines.append(f"  ❌ {method}: {result}")
        
        # Reference Resolution
        if self.findings['parsing_attempts']:
            report_lines.append(f"\n🔗 REFERENCE RESOLUTION ANALYSIS")
            report_lines.append("-" * 40)
            parsing = self.findings['parsing_attempts']
            report_lines.append(f"Attribute definitions found: {parsing['definitions_found']}")
            report_lines.append(f"Spec object types found: {parsing['spec_types_found']}")
            
            for test in parsing['resolution_tests']:
                report_lines.append(f"\nSPEC-OBJECT: {test['spec_object_id']}")
                if test['type_resolution']:
                    if test['type_resolution']['resolved']:
                        report_lines.append(f"  ✅ Type: {test['type_resolution']['name']}")
                    else:
                        report_lines.append(f"  ❌ Type: Unresolved reference")
                
                resolved_attrs = sum(1 for attr in test['attribute_resolutions'] if attr['resolved'])
                total_attrs = len(test['attribute_resolutions'])
                report_lines.append(f"  📊 Attributes: {resolved_attrs}/{total_attrs} resolved")
        
        # Issues and Recommendations
        if self.findings['issues']:
            report_lines.append(f"\n❌ ISSUES FOUND")
            report_lines.append("-" * 40)
            for issue in self.findings['issues']:
                report_lines.append(f"• {issue}")
        
        # Generate recommendations
        self._generate_recommendations()
        if self.findings['recommendations']:
            report_lines.append(f"\n💡 RECOMMENDATIONS")
            report_lines.append("-" * 40)
            for rec in self.findings['recommendations']:
                report_lines.append(f"• {rec}")
        
        # Save report
        report_content = '\n'.join(report_lines)
        
        # Print to console
        print("\n" + report_content)
        
        # Save to file
        try:
            report_file = f"reqif_diagnostics_{Path(self.file_path).stem}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\n📄 Report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
        
        return report_content
    
    def _generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        # XML issues
        if not self.findings['structure'].get('valid_xml'):
            recommendations.append("Fix XML structure issues before parsing")
        
        # Namespace issues
        namespaces = self.findings['namespaces']['found']
        if not namespaces:
            recommendations.append("Implement namespace-agnostic parsing methods")
        elif len(namespaces) > 1:
            recommendations.append("Use multiple namespace resolution strategies")
        
        # Element discovery issues
        elements = self.findings['elements']
        failed_discoveries = [name for name, methods in elements.items() 
                            if not any(isinstance(count, int) and count > 0 for count in methods.values())]
        
        if failed_discoveries:
            recommendations.append(f"Improve element discovery for: {', '.join(failed_discoveries)}")
        
        # Content extraction issues
        if self.findings['content_samples']:
            extraction_failures = 0
            for sample in self.findings['content_samples']:
                failed_methods = sum(1 for result in sample['methods'].values() 
                                   if not result or result.startswith('failed'))
                total_methods = len(sample['methods'])
                if failed_methods > total_methods * 0.7:  # More than 70% failed
                    extraction_failures += 1
            
            if extraction_failures > 0:
                recommendations.append("Implement more robust content extraction methods")
        
        # Reference resolution issues
        if self.findings['parsing_attempts']:
            parsing = self.findings['parsing_attempts']
            if parsing['definitions_found'] == 0:
                recommendations.append("Fix attribute definition discovery")
            if parsing['spec_types_found'] == 0:
                recommendations.append("Fix spec object type discovery")
            
            # Check resolution success rate
            total_tests = len(parsing['resolution_tests'])
            successful_type_resolutions = sum(1 for test in parsing['resolution_tests'] 
                                            if test['type_resolution'] and test['type_resolution']['resolved'])
            
            if total_tests > 0 and successful_type_resolutions / total_tests < 0.5:
                recommendations.append("Improve type reference resolution logic")
        
        # Spec object issues
        if not self.findings['spec_objects']:
            recommendations.append("Critical: No SPEC-OBJECT elements found - check element discovery methods")
        else:
            values_containers_found = sum(1 for obj in self.findings['spec_objects'] 
                                        if obj['values_container']['found'])
            if values_containers_found == 0:
                recommendations.append("Fix VALUES container discovery within SPEC-OBJECT elements")
        
        self.findings['recommendations'] = recommendations
    
    # Helper methods
    def _find_elements_best_method(self, element_name):
        """Find elements using the best available method"""
        if not self.root:
            return []
        
        # Try different methods in order of preference
        methods = [
            lambda: self.root.findall(f".//{element_name}"),
            lambda: self.root.findall(f".//{{{self.namespaces.get('default', '')}}}{element_name}") if 'default' in self.namespaces else [],
            lambda: self.root.findall(f".//reqif:{element_name}", {'reqif': self.namespaces['reqif']}) if 'reqif' in self.namespaces else [],
            lambda: [elem for elem in self.root.iter() if element_name in elem.tag]
        ]
        
        for method in methods:
            try:
                result = method()
                if result:
                    return result
            except:
                continue
        
        return []
    
    def _find_child_element(self, parent, element_name):
        """Find child element using multiple methods"""
        # Direct search
        for child in parent:
            if element_name in child.tag:
                return child
        
        # Recursive search
        found = parent.find(f".//{element_name}")
        if found is not None:
            return found
        
        # With namespace
        if 'default' in self.namespaces:
            ns_element = f"{{{self.namespaces['default']}}}{element_name}"
            found = parent.find(f".//{ns_element}")
            if found is not None:
                return found
        
        return None
    
    def _find_attribute_values(self, values_container):
        """Find all attribute value elements"""
        value_types = [
            'ATTRIBUTE-VALUE-STRING',
            'ATTRIBUTE-VALUE-XHTML', 
            'ATTRIBUTE-VALUE-ENUMERATION',
            'ATTRIBUTE-VALUE-INTEGER',
            'ATTRIBUTE-VALUE-REAL',
            'ATTRIBUTE-VALUE-BOOLEAN'
        ]
        
        attribute_values = []
        
        for value_type in value_types:
            elements = []
            
            # Try direct search
            for child in values_container.iter():
                if value_type in child.tag:
                    elements.append(child)
            
            for elem in elements:
                sample_content = self._extract_all_text(elem)
                attribute_values.append({
                    'type': value_type,
                    'element': elem,
                    'sample_content': sample_content[:100] if sample_content else 'No content'
                })
        
        return attribute_values
    
    def _extract_identifier(self, element):
        """Extract identifier from element"""
        return (element.get('IDENTIFIER') or 
                element.get('identifier') or
                element.get('ID') or
                element.get('id') or
                '')
    
    def _extract_long_name(self, element):
        """Extract long name from element"""
        return (element.get('LONG-NAME') or 
                element.get('long-name') or
                element.get('NAME') or
                element.get('name') or
                '')
    
    def _extract_type_reference(self, spec_obj):
        """Extract type reference from SPEC-OBJECT"""
        type_elem = self._find_child_element(spec_obj, 'TYPE')
        if type_elem is not None:
            return (type_elem.get('SPEC-OBJECT-TYPE-REF') or
                   type_elem.get('spec-object-type-ref') or
                   '')
        return ''
    
    def _extract_attribute_definition_ref(self, attr_value_elem):
        """Extract attribute definition reference"""
        # Method 1: Direct attribute
        ref = (attr_value_elem.get('ATTRIBUTE-DEFINITION-REF') or
               attr_value_elem.get('attribute-definition-ref'))
        if ref:
            return ref
        
        # Method 2: DEFINITION child
        def_elem = self._find_child_element(attr_value_elem, 'DEFINITION')
        if def_elem is not None:
            # Look for reference elements
            for child in def_elem.iter():
                if 'ATTRIBUTE-DEFINITION' in child.tag and child.tag.endswith('-REF'):
                    if child.text:
                        return child.text.strip()
        
        return ''
    
    def _extract_all_text(self, element):
        """Extract all text content from element recursively"""
        if element is None:
            return ''
        
        texts = []
        
        if element.text:
            texts.append(element.text.strip())
        
        for child in element:
            child_text = self._extract_all_text(child)
            if child_text:
                texts.append(child_text)
            
            if child.tail:
                texts.append(child.tail.strip())
        
        full_text = ' '.join(texts)
        
        # Clean up
        full_text = re.sub(r'\s+', ' ', full_text)
        full_text = html.unescape(full_text)
        
        return full_text.strip()
    
    def _extract_xhtml_content(self, element):
        """Extract XHTML content specifically"""
        the_value_elem = self._find_child_element(element, 'THE-VALUE')
        if the_value_elem is not None:
            return self._extract_all_text(the_value_elem)
        return self._extract_all_text(element)


def run_diagnostics(file_path: str):
    """Run comprehensive diagnostics on a ReqIF file"""
    if not file_path:
        print("❌ Please provide a ReqIF file path")
        return
    
    diagnostics = ReqIFDiagnostics()
    
    try:
        findings = diagnostics.analyze_file(file_path)
        
        print("\n🎯 DIAGNOSTIC SUMMARY")
        print("=" * 50)
        
        # Quick summary
        issues_count = len(findings['issues'])
        recommendations_count = len(findings['recommendations'])
        
        if issues_count == 0:
            print("✅ No critical issues found")
        else:
            print(f"❌ {issues_count} issues found")
        
        print(f"💡 {recommendations_count} recommendations generated")
        
        # Key metrics
        if findings['structure'].get('valid_xml'):
            total_elements = findings['structure']['total_elements']
            print(f"📊 {total_elements:,} XML elements analyzed")
        
        if findings['spec_objects']:
            spec_obj_count = len(findings['spec_objects'])
            print(f"📋 {spec_obj_count} SPEC-OBJECT elements found for detailed analysis")
        
        return findings
        
    except Exception as e:
        print(f"❌ Diagnostics failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# Command line interface
if __name__ == "__main__":
    import sys
    
    print("🔬 ReqIF Deep Diagnostics Tool")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("Usage: python reqif_diagnostics.py <path_to_reqif_file>")
        print("\nExample:")
        print("  python reqif_diagnostics.py myfile.reqif")
        print("  python reqif_diagnostics.py myfile.reqifz")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print(f"🎯 Analyzing: {os.path.basename(file_path)}")
    print()
    
    # Run diagnostics
    findings = run_diagnostics(file_path)
    
    if findings:
        print("\n🎉 Diagnostics completed successfully!")
        print("📄 Check the generated report file for full details")
    else:
        print("\n❌ Diagnostics failed")
        sys.exit(1)