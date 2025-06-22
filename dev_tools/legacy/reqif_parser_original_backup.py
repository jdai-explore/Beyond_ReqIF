#!/usr/bin/env python3
"""
Targeted ReqIF Parser - Fixed Based on Diagnostic Results
This parser directly addresses the issues found in your specific ReqIF file:
1. Namespace-aware element discovery
2. Proper definition cataloging 
3. THE-VALUE element finding with full namespace
4. Enhanced reference resolution
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Set
import os
import zipfile
import tempfile
import shutil
import re
import html


class TargetedReqIFParser:
    """
    ReqIF Parser specifically designed to handle your file structure based on diagnostics
    """
    
    def __init__(self):
        # Namespace handling
        self.root_namespace = None
        self.namespace_uri = None
        self.ns_prefix = "reqif"
        
        # Comprehensive catalogs
        self.attribute_definitions = {}      # ID -> definition info
        self.spec_object_types = {}         # ID -> type info  
        self.enumeration_definitions = {}   # ID -> enum info
        self.enum_values = {}               # ID -> human readable name
        
        # Statistics and diagnostics
        self.stats = {
            'elements_found': {},
            'definitions_cataloged': 0,
            'types_cataloged': 0,
            'enums_cataloged': 0,
            'spec_objects_processed': 0,
            'successful_resolutions': 0,
            'content_extractions': 0,
            'parsing_issues': []
        }
        
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse ReqIF file with targeted fixes for your specific file structure
        """
        print(f"🎯 Targeted ReqIF Parser - Processing: {os.path.basename(file_path)}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ReqIF file not found: {file_path}")
        
        # Reset state
        self._reset_parser_state()
        
        try:
            # Handle ReqIFZ archives
            if file_path.lower().endswith('.reqifz'):
                actual_file_path = self._extract_reqifz(file_path)
            else:
                actual_file_path = file_path
            
            # Parse XML and setup namespace handling
            tree = ET.parse(actual_file_path)
            root = tree.getroot()
            
            # Critical Fix 1: Setup robust namespace handling
            self._setup_namespace_handling(root)
            
            print(f"🏷️ Namespace URI: {self.namespace_uri}")
            print(f"🏷️ Using namespace prefix: {self.ns_prefix}")
            
            # Critical Fix 2: Build comprehensive definition catalogs with namespace awareness
            print("📚 Building definition catalogs with namespace awareness...")
            self._build_comprehensive_catalogs(root)
            
            # Critical Fix 3: Extract SPEC-OBJECTs with enhanced resolution
            print("📋 Extracting SPEC-OBJECTs with enhanced resolution...")
            requirements = self._extract_spec_objects_enhanced(root)
            
            # Print final statistics
            self._print_parsing_statistics()
            
            return requirements
            
        except Exception as e:
            print(f"❌ Parsing failed: {str(e)}")
            raise RuntimeError(f"Failed to parse ReqIF file: {str(e)}")
    
    def _reset_parser_state(self):
        """Reset all parser state"""
        self.root_namespace = None
        self.namespace_uri = None
        self.attribute_definitions.clear()
        self.spec_object_types.clear()
        self.enumeration_definitions.clear()
        self.enum_values.clear()
        
        self.stats = {
            'elements_found': {},
            'definitions_cataloged': 0,
            'types_cataloged': 0,
            'enums_cataloged': 0,
            'spec_objects_processed': 0,
            'successful_resolutions': 0,
            'content_extractions': 0,
            'parsing_issues': []
        }
    
    def _extract_reqifz(self, file_path: str) -> str:
        """Extract ReqIFZ archive and return path to main ReqIF file"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find largest .reqif file
            reqif_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.reqif'):
                        full_path = os.path.join(root, file)
                        size = os.path.getsize(full_path)
                        reqif_files.append((full_path, size))
            
            if not reqif_files:
                raise ValueError("No .reqif files found in archive")
            
            # Return path to largest file
            main_reqif = max(reqif_files, key=lambda x: x[1])[0]
            print(f"📦 Extracted archive, using: {os.path.basename(main_reqif)}")
            return main_reqif
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
    
    def _setup_namespace_handling(self, root):
        """
        Critical Fix 1: Setup robust namespace handling based on diagnostic findings
        Your file uses full namespace URIs in element tags
        """
        # Extract namespace from root tag
        if '}' in root.tag:
            self.namespace_uri = root.tag.split('}')[0][1:]  # Remove { }
            self.root_namespace = f"{{{self.namespace_uri}}}"
            
            # Register namespace for XPath queries
            ET.register_namespace(self.ns_prefix, self.namespace_uri)
            
            print(f"✅ Detected namespace: {self.namespace_uri}")
        else:
            print("⚠️ No namespace detected in root element")
            self.root_namespace = ""
            self.namespace_uri = None
    
    def _build_comprehensive_catalogs(self, root):
        """
        Critical Fix 2: Build comprehensive catalogs with namespace awareness
        Based on diagnostics: should find 838 definitions, not just 13
        """
        print("  🔍 Building attribute definition catalog...")
        self._build_attribute_definition_catalog(root)
        
        print("  🔍 Building enumeration catalog...")
        self._build_enumeration_catalog(root)
        
        print("  🔍 Building spec object type catalog...")
        self._build_spec_object_type_catalog(root)
        
        # Update statistics
        self.stats['definitions_cataloged'] = len(self.attribute_definitions)
        self.stats['types_cataloged'] = len(self.spec_object_types)
        self.stats['enums_cataloged'] = len(self.enumeration_definitions)
        
        print(f"  ✅ Attribute definitions: {len(self.attribute_definitions)}")
        print(f"  ✅ Spec object types: {len(self.spec_object_types)}")
        print(f"  ✅ Enumeration definitions: {len(self.enumeration_definitions)}")
        print(f"  ✅ Enum values: {len(self.enum_values)}")
    
    def _build_attribute_definition_catalog(self, root):
        """Build attribute definition catalog with namespace awareness"""
        definition_types = [
            'ATTRIBUTE-DEFINITION-STRING',
            'ATTRIBUTE-DEFINITION-XHTML', 
            'ATTRIBUTE-DEFINITION-ENUMERATION',
            'ATTRIBUTE-DEFINITION-INTEGER',
            'ATTRIBUTE-DEFINITION-REAL',
            'ATTRIBUTE-DEFINITION-DATE',
            'ATTRIBUTE-DEFINITION-BOOLEAN'
        ]
        
        for def_type in definition_types:
            elements = self._find_elements_namespace_aware(root, def_type)
            self.stats['elements_found'][def_type] = len(elements)
            
            for elem in elements:
                identifier = self._extract_identifier(elem)
                if identifier:
                    long_name = self._extract_long_name(elem) or identifier
                    
                    self.attribute_definitions[identifier] = {
                        'identifier': identifier,
                        'long_name': long_name,
                        'data_type': def_type.replace('ATTRIBUTE-DEFINITION-', '').lower(),
                        'element': elem
                    }
    
    def _build_enumeration_catalog(self, root):
        """Build enumeration catalog with namespace awareness"""
        enum_defs = self._find_elements_namespace_aware(root, 'ENUM-DEFINITION')
        
        for enum_def in enum_defs:
            enum_id = self._extract_identifier(enum_def)
            if not enum_id:
                continue
                
            enum_name = self._extract_long_name(enum_def) or enum_id
            
            self.enumeration_definitions[enum_id] = {
                'identifier': enum_id,
                'long_name': enum_name,
                'values': {}
            }
            
            # Find enum values with namespace awareness
            enum_values = self._find_elements_namespace_aware(enum_def, 'ENUM-VALUE')
            
            for enum_value in enum_values:
                val_id = self._extract_identifier(enum_value)
                val_name = self._extract_long_name(enum_value) or val_id
                
                if val_id:
                    self.enum_values[val_id] = val_name
                    self.enumeration_definitions[enum_id]['values'][val_id] = val_name
    
    def _build_spec_object_type_catalog(self, root):
        """Build spec object type catalog with namespace awareness"""
        spec_types = self._find_elements_namespace_aware(root, 'SPEC-OBJECT-TYPE')
        
        for spec_type in spec_types:
            type_id = self._extract_identifier(spec_type)
            if not type_id:
                continue
                
            type_name = self._extract_long_name(spec_type) or type_id
            
            self.spec_object_types[type_id] = {
                'identifier': type_id,
                'long_name': type_name,
                'element': spec_type
            }
    
    def _extract_spec_objects_enhanced(self, root) -> List[Dict[str, Any]]:
        """
        Critical Fix 3: Extract SPEC-OBJECTs with enhanced resolution
        """
        spec_objects = self._find_elements_namespace_aware(root, 'SPEC-OBJECT')
        self.stats['elements_found']['SPEC-OBJECT'] = len(spec_objects)
        
        print(f"  📊 Found {len(spec_objects)} SPEC-OBJECT elements")
        
        requirements = []
        
        for i, spec_obj in enumerate(spec_objects):
            try:
                requirement = self._process_single_spec_object(spec_obj, i)
                if requirement:
                    requirements.append(requirement)
                    self.stats['successful_resolutions'] += 1
                
                self.stats['spec_objects_processed'] += 1
                
                # Progress indicator for large files
                if (i + 1) % 50 == 0:
                    print(f"    📋 Processed {i + 1}/{len(spec_objects)} SPEC-OBJECTs...")
                    
            except Exception as e:
                self.stats['parsing_issues'].append(f"SPEC-OBJECT {i}: {str(e)}")
                continue
        
        return requirements
    
    def _process_single_spec_object(self, spec_obj, index: int) -> Optional[Dict[str, Any]]:
        """Process a single SPEC-OBJECT with enhanced resolution"""
        # Extract basic info
        req_id = self._extract_identifier(spec_obj) or f"REQ_{index}"
        
        # Initialize requirement
        requirement = {
            'id': req_id,
            'identifier': req_id,
            'title': '',
            'description': '',
            'type': '',
            'priority': '',
            'status': '',
            'attributes': {},
            'raw_attributes': {},
            'raw_content': {}
        }
        
        # Resolve type reference
        type_ref = self._extract_type_reference_enhanced(spec_obj)
        if type_ref and type_ref in self.spec_object_types:
            requirement['type'] = self.spec_object_types[type_ref]['long_name']
        elif type_ref:
            requirement['type'] = type_ref
        
        # Critical Fix 4: Enhanced attribute value extraction
        self._extract_attribute_values_enhanced(spec_obj, requirement)
        
        # Smart field mapping
        self._smart_field_mapping(requirement)
        
        # Ensure meaningful content
        self._ensure_meaningful_content(requirement)
        
        return requirement
    
    def _extract_type_reference_enhanced(self, spec_obj) -> Optional[str]:
        """Extract type reference with namespace awareness"""
        type_elem = self._find_child_element_namespace_aware(spec_obj, 'TYPE')
        if type_elem is not None:
            return (type_elem.get('SPEC-OBJECT-TYPE-REF') or
                   type_elem.get('spec-object-type-ref'))
        return None
    
    def _extract_attribute_values_enhanced(self, spec_obj, requirement: Dict[str, Any]):
        """
        Critical Fix 4: Enhanced attribute value extraction with namespace awareness
        Based on diagnostics: THE-VALUE elements are missing, need namespace-aware search
        """
        # Find VALUES container with namespace awareness
        values_elem = self._find_child_element_namespace_aware(spec_obj, 'VALUES')
        if values_elem is None:
            return
        
        # Find all attribute value types
        value_types = [
            'ATTRIBUTE-VALUE-STRING',
            'ATTRIBUTE-VALUE-XHTML',
            'ATTRIBUTE-VALUE-ENUMERATION',
            'ATTRIBUTE-VALUE-INTEGER',
            'ATTRIBUTE-VALUE-REAL',
            'ATTRIBUTE-VALUE-DATE',
            'ATTRIBUTE-VALUE-BOOLEAN'
        ]
        
        for value_type in value_types:
            attr_values = self._find_elements_namespace_aware(values_elem, value_type)
            
            for attr_value_elem in attr_values:
                self._process_single_attribute_value(attr_value_elem, value_type, requirement)
    
    def _process_single_attribute_value(self, attr_value_elem, value_type: str, requirement: Dict[str, Any]):
        """Process a single attribute value with enhanced content extraction"""
        # Get attribute definition reference
        attr_def_ref = self._extract_attribute_definition_ref_enhanced(attr_value_elem)
        
        if not attr_def_ref:
            return
        
        # Extract content using multiple strategies
        content = self._extract_content_enhanced(attr_value_elem, value_type)
        
        if not content:
            return
        
        # Store raw content
        requirement['raw_content'][attr_def_ref] = content
        requirement['raw_attributes'][attr_def_ref] = content
        
        # Get human-readable attribute name
        attr_name = attr_def_ref
        if attr_def_ref in self.attribute_definitions:
            attr_name = self.attribute_definitions[attr_def_ref]['long_name']
        
        # Store with human-readable name
        requirement['attributes'][attr_name] = content
        
        self.stats['content_extractions'] += 1
    
    def _extract_attribute_definition_ref_enhanced(self, attr_value_elem) -> Optional[str]:
        """Extract attribute definition reference with enhanced methods"""
        # Method 1: Direct attribute
        attr_def_ref = (attr_value_elem.get('ATTRIBUTE-DEFINITION-REF') or
                       attr_value_elem.get('attribute-definition-ref'))
        if attr_def_ref:
            return attr_def_ref
        
        # Method 2: DEFINITION child element with namespace awareness
        def_elem = self._find_child_element_namespace_aware(attr_value_elem, 'DEFINITION')
        if def_elem is not None:
            # Look for various reference element types
            ref_types = [
                'ATTRIBUTE-DEFINITION-STRING-REF',
                'ATTRIBUTE-DEFINITION-XHTML-REF',
                'ATTRIBUTE-DEFINITION-ENUMERATION-REF',
                'ATTRIBUTE-DEFINITION-INTEGER-REF',
                'ATTRIBUTE-DEFINITION-REAL-REF',
                'ATTRIBUTE-DEFINITION-DATE-REF',
                'ATTRIBUTE-DEFINITION-BOOLEAN-REF'
            ]
            
            for ref_type in ref_types:
                ref_elem = self._find_child_element_namespace_aware(def_elem, ref_type)
                if ref_elem is not None and ref_elem.text:
                    return ref_elem.text.strip()
        
        return None
    
    def _extract_content_enhanced(self, attr_value_elem, value_type: str) -> str:
        """
        Critical Fix 3: Enhanced content extraction addressing THE-VALUE issues
        Based on diagnostics: THE-VALUE child elements not found, need namespace awareness
        """
        if 'STRING' in value_type:
            return self._extract_string_content_enhanced(attr_value_elem)
        elif 'XHTML' in value_type:
            return self._extract_xhtml_content_enhanced(attr_value_elem)
        elif 'ENUMERATION' in value_type:
            return self._extract_enumeration_content_enhanced(attr_value_elem)
        elif value_type in ['ATTRIBUTE-VALUE-INTEGER', 'ATTRIBUTE-VALUE-REAL', 'ATTRIBUTE-VALUE-DATE']:
            return self._extract_numeric_content_enhanced(attr_value_elem)
        elif 'BOOLEAN' in value_type:
            return self._extract_boolean_content_enhanced(attr_value_elem)
        else:
            return self._extract_generic_content_enhanced(attr_value_elem)
    
    def _extract_string_content_enhanced(self, elem) -> str:
        """Extract STRING content with multiple strategies"""
        # Strategy 1: THE-VALUE attribute (working per diagnostics)
        the_value = elem.get('THE-VALUE') or elem.get('the-value')
        if the_value:
            return str(the_value)
        
        # Strategy 2: THE-VALUE child element with namespace awareness
        the_value_elem = self._find_child_element_namespace_aware(elem, 'THE-VALUE')
        if the_value_elem is not None:
            return self._extract_all_text_enhanced(the_value_elem)
        
        # Strategy 3: Direct text content
        if elem.text:
            return elem.text.strip()
        
        return ''
    
    def _extract_xhtml_content_enhanced(self, elem) -> str:
        """Extract XHTML content with namespace-aware THE-VALUE finding"""
        # Strategy 1: Find THE-VALUE child with namespace awareness
        the_value_elem = self._find_child_element_namespace_aware(elem, 'THE-VALUE')
        if the_value_elem is not None:
            return self._extract_all_text_enhanced(the_value_elem)
        
        # Strategy 2: Extract all text content (working per diagnostics)
        all_text = self._extract_all_text_enhanced(elem)
        
        # Clean up - remove reference IDs that appear at the start
        if all_text.startswith('_'):
            # Remove leading reference ID
            parts = all_text.split(' ', 1)
            if len(parts) > 1:
                return parts[1]
        
        return all_text
    
    def _extract_enumeration_content_enhanced(self, elem) -> str:
        """Extract enumeration content with namespace awareness"""
        enum_values = []
        
        # Find VALUES container with namespace awareness
        values_container = self._find_child_element_namespace_aware(elem, 'VALUES')
        if values_container is not None:
            # Find ENUM-VALUE-REF elements
            enum_refs = self._find_elements_namespace_aware(values_container, 'ENUM-VALUE-REF')
            
            for enum_ref in enum_refs:
                ref_value = enum_ref.get('REF') or enum_ref.get('ref') or enum_ref.text
                if ref_value:
                    # Resolve to human-readable name
                    human_name = self.enum_values.get(ref_value, ref_value)
                    enum_values.append(human_name)
        
        return ', '.join(enum_values) if enum_values else ''
    
    def _extract_numeric_content_enhanced(self, elem) -> str:
        """Extract numeric content (integer, real, date)"""
        # THE-VALUE attribute
        the_value = elem.get('THE-VALUE') or elem.get('the-value')
        if the_value is not None:
            return str(the_value)
        
        # THE-VALUE child element
        the_value_elem = self._find_child_element_namespace_aware(elem, 'THE-VALUE')
        if the_value_elem is not None and the_value_elem.text:
            return the_value_elem.text
        
        return ''
    
    def _extract_boolean_content_enhanced(self, elem) -> str:
        """Extract boolean content with human-readable conversion"""
        value = self._extract_numeric_content_enhanced(elem)
        if value.lower() in ['true', '1', 'yes']:
            return 'Yes'
        elif value.lower() in ['false', '0', 'no']:
            return 'No'
        return value
    
    def _extract_generic_content_enhanced(self, elem) -> str:
        """Generic content extraction for unknown types"""
        return (elem.get('THE-VALUE') or 
                elem.get('the-value') or
                self._extract_all_text_enhanced(elem))
    
    def _extract_all_text_enhanced(self, element) -> str:
        """Extract all text content recursively with better cleanup"""
        if element is None:
            return ''
        
        texts = []
        
        # Add element's direct text
        if element.text:
            texts.append(element.text.strip())
        
        # Process all children recursively
        for child in element:
            child_text = self._extract_all_text_enhanced(child)
            if child_text:
                texts.append(child_text)
            
            # Add tail text
            if child.tail:
                texts.append(child.tail.strip())
        
        # Join and clean up
        full_text = ' '.join(texts)
        
        # Enhanced cleanup
        full_text = re.sub(r'\s+', ' ', full_text)  # Multiple spaces to single
        full_text = html.unescape(full_text)        # Decode HTML entities
        
        return full_text.strip()
    
    def _smart_field_mapping(self, requirement: Dict[str, Any]):
        """Smart mapping of attributes to standard requirement fields"""
        # Field mapping keywords
        field_keywords = {
            'title': ['title', 'name', 'heading', 'object', 'caption', 'summary'],
            'description': ['description', 'detail', 'content', 'specification', 'rationale', 'text'],
            'priority': ['priority', 'importance', 'criticality', 'level'],
            'status': ['status', 'state', 'phase', 'condition']
        }
        
        for field, keywords in field_keywords.items():
            if requirement[field]:  # Don't override if already set
                continue
            
            # Look for matching attributes
            for attr_name, attr_value in requirement['attributes'].items():
                if not attr_value:
                    continue
                
                attr_lower = attr_name.lower()
                if any(keyword in attr_lower for keyword in keywords):
                    if field in ['title', 'description']:
                        # Quality check for title/description
                        if self._is_quality_content(attr_value, field):
                            requirement[field] = str(attr_value)
                            break
                    else:
                        requirement[field] = str(attr_value)
                        break
    
    def _is_quality_content(self, content: str, field_type: str) -> bool:
        """Check if content is quality for the field type"""
        if not content or len(content) < 2:
            return False
        
        # Remove leading reference IDs
        clean_content = content
        if content.startswith('_') and ' ' in content:
            clean_content = content.split(' ', 1)[1]
        
        if field_type == 'title':
            return (len(clean_content) < 200 and 
                   not clean_content.replace('.', '').replace('-', '').isdigit() and
                   any(c.isalpha() for c in clean_content))
        elif field_type == 'description':
            return (len(clean_content) >= 10 and 
                   ' ' in clean_content and
                   any(c.isalpha() for c in clean_content))
        
        return True
    
    def _ensure_meaningful_content(self, requirement: Dict[str, Any]):
        """Ensure requirement has meaningful content"""
        # Ensure title
        if not requirement['title']:
            # Try to find best title from attributes
            candidates = []
            for attr_name, attr_value in requirement['attributes'].items():
                if attr_value and self._is_quality_content(str(attr_value), 'title'):
                    candidates.append(str(attr_value))
            
            if candidates:
                requirement['title'] = min(candidates, key=len)  # Shortest reasonable title
            else:
                requirement['title'] = requirement['id']
        
        # Ensure description
        if not requirement['description']:
            # Try to find best description from attributes
            candidates = []
            for attr_name, attr_value in requirement['attributes'].items():
                if attr_value and self._is_quality_content(str(attr_value), 'description'):
                    candidates.append(str(attr_value))
            
            if candidates:
                requirement['description'] = max(candidates, key=len)  # Longest reasonable description
    
    # Core utility methods with namespace awareness
    def _find_elements_namespace_aware(self, parent, element_name: str) -> List:
        """
        Find elements with robust namespace awareness - addresses core diagnostic issue
        """
        found_elements = []
        
        # Strategy 1: Namespace-aware search (should work now)
        if self.namespace_uri:
            try:
                namespaced_name = f"{{{self.namespace_uri}}}{element_name}"
                elements = parent.findall(f".//{namespaced_name}")
                if elements:
                    found_elements.extend(elements)
                    return found_elements
            except:
                pass
        
        # Strategy 2: XPath with registered namespace
        if self.namespace_uri:
            try:
                elements = parent.findall(f".//{self.ns_prefix}:{element_name}", 
                                        {self.ns_prefix: self.namespace_uri})
                if elements:
                    found_elements.extend(elements)
                    return found_elements
            except:
                pass
        
        # Strategy 3: Pattern matching (working per diagnostics)
        try:
            for elem in parent.iter():
                if element_name in elem.tag:
                    found_elements.append(elem)
            if found_elements:
                return found_elements
        except:
            pass
        
        # Strategy 4: Case insensitive search (working per diagnostics)
        try:
            for elem in parent.iter():
                if element_name.lower() in elem.tag.lower():
                    found_elements.append(elem)
        except:
            pass
        
        return found_elements
    
    def _find_child_element_namespace_aware(self, parent, element_name: str):
        """Find direct child element with namespace awareness"""
        # Strategy 1: Direct namespace-aware search
        if self.namespace_uri:
            namespaced_name = f"{{{self.namespace_uri}}}{element_name}"
            child = parent.find(namespaced_name)
            if child is not None:
                return child
        
        # Strategy 2: Pattern matching in direct children
        for child in parent:
            if element_name in child.tag:
                return child
        
        # Strategy 3: Recursive search
        found = parent.find(f".//{element_name}")
        if found is not None:
            return found
        
        # Strategy 4: Namespace-aware recursive
        if self.namespace_uri:
            namespaced_name = f"{{{self.namespace_uri}}}{element_name}"
            found = parent.find(f".//{namespaced_name}")
            if found is not None:
                return found
        
        return None
    
    def _extract_identifier(self, element) -> Optional[str]:
        """Extract identifier with multiple fallback patterns"""
        return (element.get('IDENTIFIER') or 
                element.get('identifier') or
                element.get('ID') or
                element.get('id'))
    
    def _extract_long_name(self, element) -> Optional[str]:
        """Extract long name with multiple fallback patterns"""
        return (element.get('LONG-NAME') or 
                element.get('long-name') or
                element.get('NAME') or
                element.get('name'))
    
    def _print_parsing_statistics(self):
        """Print comprehensive parsing statistics"""
        print("\n" + "="*60)
        print("🎯 TARGETED PARSER RESULTS")
        print("="*60)
        
        print(f"📊 Elements Found:")
        for element_type, count in self.stats['elements_found'].items():
            print(f"  • {element_type}: {count}")
        
        print(f"\n📚 Catalogs Built:")
        print(f"  • Attribute Definitions: {self.stats['definitions_cataloged']}")
        print(f"  • Spec Object Types: {self.stats['types_cataloged']}")
        print(f"  • Enumeration Definitions: {self.stats['enums_cataloged']}")
        print(f"  • Enum Values: {len(self.enum_values)}")
        
        print(f"\n📋 Processing Results:")
        print(f"  • SPEC-OBJECTs Processed: {self.stats['spec_objects_processed']}")
        print(f"  • Successful Resolutions: {self.stats['successful_resolutions']}")
        print(f"  • Content Extractions: {self.stats['content_extractions']}")
        
        if self.stats['parsing_issues']:
            print(f"\n⚠️ Issues Encountered:")
            for issue in self.stats['parsing_issues'][:5]:  # Show first 5
                print(f"  • {issue}")
            if len(self.stats['parsing_issues']) > 5:
                print(f"  ... and {len(self.stats['parsing_issues']) - 5} more")
        
        # Calculate success rates
        if self.stats['spec_objects_processed'] > 0:
            resolution_rate = (self.stats['successful_resolutions'] / 
                             self.stats['spec_objects_processed'] * 100)
            print(f"\n✅ Resolution Success Rate: {resolution_rate:.1f}%")
        
        print("="*60)
    
    def get_parsing_diagnostics(self) -> Dict[str, Any]:
        """Get detailed parsing diagnostics for analysis"""
        return {
            'namespace_info': {
                'namespace_uri': self.namespace_uri,
                'root_namespace': self.root_namespace,
                'namespace_prefix': self.ns_prefix
            },
            'catalog_info': {
                'attribute_definitions': len(self.attribute_definitions),
                'spec_object_types': len(self.spec_object_types),
                'enumeration_definitions': len(self.enumeration_definitions),
                'enum_values': len(self.enum_values)
            },
            'processing_stats': self.stats.copy(),
            'sample_definitions': {
                'first_5_attr_defs': list(self.attribute_definitions.keys())[:5],
                'first_5_spec_types': list(self.spec_object_types.keys())[:5],
                'first_5_enums': list(self.enumeration_definitions.keys())[:5]
            }
        }
    
    def validate_parsing_quality(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate parsing quality with enhanced metrics"""
        if not requirements:
            return {
                'quality_score': 0,
                'issues': ['No requirements parsed'],
                'recommendations': ['Check element discovery and namespace handling']
            }
        
        total = len(requirements)
        metrics = {
            'total_requirements': total,
            'with_meaningful_titles': 0,
            'with_good_descriptions': 0,
            'with_resolved_types': 0,
            'with_multiple_attributes': 0,
            'content_extraction_success': 0
        }
        
        for req in requirements:
            # Meaningful titles (not just ID)
            if (req.get('title') and req['title'] != req.get('id') and 
                len(req['title']) > 3):
                metrics['with_meaningful_titles'] += 1
            
            # Good descriptions (substantial content)
            if (req.get('description') and len(req['description']) > 20):
                metrics['with_good_descriptions'] += 1
            
            # Resolved types
            if req.get('type') and not req['type'].startswith('_'):
                metrics['with_resolved_types'] += 1
            
            # Multiple attributes (indicating successful extraction)
            if len(req.get('attributes', {})) > 2:
                metrics['with_multiple_attributes'] += 1
            
            # Content extraction success
            if (req.get('attributes') and 
                any(len(str(v)) > 10 for v in req['attributes'].values())):
                metrics['content_extraction_success'] += 1
        
        # Calculate quality score
        quality_score = (
            (metrics['with_meaningful_titles'] / total) * 0.25 +
            (metrics['with_good_descriptions'] / total) * 0.25 +
            (metrics['with_resolved_types'] / total) * 0.20 +
            (metrics['with_multiple_attributes'] / total) * 0.15 +
            (metrics['content_extraction_success'] / total) * 0.15
        ) * 100
        
        # Generate issues and recommendations
        issues = []
        recommendations = []
        
        if metrics['with_meaningful_titles'] < total * 0.7:
            issues.append(f"Only {metrics['with_meaningful_titles']}/{total} have meaningful titles")
            recommendations.append("Improve title extraction from attributes")
        
        if metrics['with_good_descriptions'] < total * 0.5:
            issues.append(f"Only {metrics['with_good_descriptions']}/{total} have substantial descriptions")
            recommendations.append("Enhance XHTML content extraction")
        
        if metrics['with_resolved_types'] < total * 0.8:
            issues.append(f"Only {metrics['with_resolved_types']}/{total} have resolved types")
            recommendations.append("Check type reference resolution")
        
        if self.stats['content_extractions'] < total * 2:  # Expect at least 2 attributes per requirement
            issues.append("Low content extraction rate")
            recommendations.append("Verify THE-VALUE element discovery")
        
        return {
            'quality_score': round(quality_score, 1),
            'metrics': metrics,
            'issues': issues,
            'recommendations': recommendations
        }


# Integration functions for existing codebase
class ReqIFParser:
    """
    Drop-in replacement for original ReqIFParser using targeted improvements
    """
    
    def __init__(self):
        self.targeted_parser = TargetedReqIFParser()
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse ReqIF file using targeted parser"""
        return self.targeted_parser.parse_file(file_path)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information with parsing quality assessment"""
        try:
            requirements = self.parse_file(file_path)
            quality = self.targeted_parser.validate_parsing_quality(requirements)
            
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_type': 'ReqIFZ' if file_path.lower().endswith('.reqifz') else 'ReqIF',
                'file_size': os.path.getsize(file_path),
                'requirement_count': len(requirements),
                'quality_score': quality['quality_score'],
                'parsing_success': True,
                'namespace_used': self.targeted_parser.namespace_uri
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'error': str(e),
                'parsing_success': False
            }
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information from targeted parser"""
        return self.targeted_parser.get_parsing_diagnostics()


# Test and comparison functions
def test_targeted_parser(file_path: str):
    """Test the targeted parser and show results"""
    print("🧪 TESTING TARGETED REQIF PARSER")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        # Parse with targeted parser
        parser = TargetedReqIFParser()
        requirements = parser.parse_file(file_path)
        
        print(f"\n📊 PARSING RESULTS:")
        print(f"  • Total requirements: {len(requirements)}")
        
        # Quality analysis
        quality = parser.validate_parsing_quality(requirements)
        print(f"  • Quality score: {quality['quality_score']}%")
        
        # Show sample requirements
        print(f"\n📋 SAMPLE REQUIREMENTS (first 3):")
        for i, req in enumerate(requirements[:3]):
            print(f"\n  Requirement {i+1}:")
            print(f"    ID: {req.get('id', 'N/A')}")
            print(f"    Title: {req.get('title', 'N/A')}")
            print(f"    Type: {req.get('type', 'N/A')}")
            print(f"    Description: {req.get('description', 'N/A')[:80]}...")
            print(f"    Attributes: {len(req.get('attributes', {}))}")
            
            # Show first few attributes
            attrs = req.get('attributes', {})
            if attrs:
                print(f"    Sample attributes:")
                for j, (attr_name, attr_value) in enumerate(list(attrs.items())[:3]):
                    print(f"      • {attr_name}: {str(attr_value)[:50]}...")
        
        # Get diagnostics
        diagnostics = parser.get_parsing_diagnostics()
        print(f"\n🔍 PARSER DIAGNOSTICS:")
        print(f"  • Namespace URI: {diagnostics['namespace_info']['namespace_uri']}")
        print(f"  • Definitions cataloged: {diagnostics['catalog_info']['attribute_definitions']}")
        print(f"  • Types cataloged: {diagnostics['catalog_info']['spec_object_types']}")
        print(f"  • Content extractions: {diagnostics['processing_stats']['content_extractions']}")
        
        # Show quality issues if any
        if quality['issues']:
            print(f"\n⚠️ QUALITY ISSUES:")
            for issue in quality['issues']:
                print(f"  • {issue}")
        
        if quality['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in quality['recommendations']:
                print(f"  • {rec}")
        
        return requirements
        
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def compare_with_original_parser(file_path: str):
    """Compare targeted parser with original parser"""
    print("⚖️ COMPARING TARGETED VS ORIGINAL PARSER")
    print("=" * 60)
    
    # Test original parser
    print("📊 Testing ORIGINAL parser...")
    try:
        # Import original parser
        import sys
        sys.path.insert(0, '.')
        
        # Try to import the original parser
        try:
            from reqif_parser_original_backup import ReqIFParser as OriginalParser
            original_parser = OriginalParser()
        except ImportError:
            # Fallback to current parser in reqif_parser.py
            from reqif_parser import ReqIFParser as OriginalParser
            original_parser = OriginalParser()
        
        original_reqs = original_parser.parse_file(file_path)
        print(f"  ✅ Original: {len(original_reqs)} requirements")
        
        # Sample from original
        if original_reqs:
            sample = original_reqs[0]
            print(f"  📝 Sample title: '{sample.get('title', 'N/A')}'")
            print(f"  📝 Sample attrs: {len(sample.get('attributes', {}))}")
        
    except Exception as e:
        print(f"  ❌ Original parser failed: {str(e)}")
        original_reqs = []
    
    print()
    
    # Test targeted parser
    print("📊 Testing TARGETED parser...")
    try:
        targeted_parser = TargetedReqIFParser()
        targeted_reqs = targeted_parser.parse_file(file_path)
        quality = targeted_parser.validate_parsing_quality(targeted_reqs)
        
        print(f"  ✅ Targeted: {len(targeted_reqs)} requirements")
        print(f"  📊 Quality score: {quality['quality_score']}%")
        
        # Sample from targeted
        if targeted_reqs:
            sample = targeted_reqs[0]
            print(f"  📝 Sample title: '{sample.get('title', 'N/A')}'")
            print(f"  📝 Sample attrs: {len(sample.get('attributes', {}))}")
        
    except Exception as e:
        print(f"  ❌ Targeted parser failed: {str(e)}")
        targeted_reqs = []
    
    # Comparison
    print(f"\n⚖️ COMPARISON SUMMARY:")
    print(f"  Original requirements: {len(original_reqs)}")
    print(f"  Targeted requirements: {len(targeted_reqs)}")
    
    if len(targeted_reqs) > len(original_reqs):
        improvement = len(targeted_reqs) - len(original_reqs)
        print(f"  ✅ Improvement: +{improvement} requirements ({improvement/max(len(original_reqs), 1)*100:.1f}% increase)")
    elif len(targeted_reqs) == len(original_reqs):
        print(f"  ℹ️ Same number of requirements found")
    else:
        print(f"  ⚠️ Fewer requirements found by targeted parser")


# Command line interface
if __name__ == "__main__":
    import sys
    
    print("🎯 Targeted ReqIF Parser - Fixed Based on Diagnostics")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python targeted_reqif_parser.py <reqif_file>           # Test parsing")
        print("  python targeted_reqif_parser.py <reqif_file> --compare # Compare with original")
        sys.exit(1)
    
    file_path = sys.argv[1]
    compare_mode = len(sys.argv) > 2 and sys.argv[2] == '--compare'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    if compare_mode:
        compare_with_original_parser(file_path)
    else:
        test_targeted_parser(file_path)
    
    print(f"\n🎉 Targeted parser test completed!")
    print(f"💡 To integrate: Replace your reqif_parser.py with this implementation")