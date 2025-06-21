#!/usr/bin/env python3
"""
Improved ReqIF Parser Module
Enhanced parsing logic with better content extraction and reference resolution.
Addresses common ReqIF parsing issues and edge cases.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Set
import os
import zipfile
import tempfile
import shutil
import re
import html


class ImprovedReqIFParser:
    """
    Improved ReqIF Parser with enhanced content extraction and error handling
    """
    
    def __init__(self):
        # Flexible namespace handling
        self.namespaces = {}
        self.root_ns = ""
        
        # Catalogs for reference resolution
        self.attribute_definitions = {}
        self.spec_object_types = {}
        self.enumeration_definitions = {}
        self.datatype_definitions = {}
        self.enum_values = {}
        
        # Debug and statistics
        self.debug_info = {
            'total_spec_objects': 0,
            'successfully_parsed': 0,
            'empty_requirements': 0,
            'parsing_errors': 0,
            'namespace_used': None,
            'file_structure': {}
        }
        
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Main parsing method with improved error handling
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ReqIF file not found: {file_path}")
        
        print(f"🔍 Parsing ReqIF file: {os.path.basename(file_path)}")
        
        # Reset state
        self._reset_state()
        
        try:
            # Handle different file types
            if file_path.lower().endswith('.reqifz'):
                return self._parse_reqifz_archive(file_path)
            else:
                return self._parse_reqif_xml(file_path)
                
        except Exception as e:
            print(f"❌ Parsing failed: {str(e)}")
            raise RuntimeError(f"Failed to parse ReqIF file: {str(e)}")
    
    def _reset_state(self):
        """Reset parser state for new file"""
        self.namespaces.clear()
        self.root_ns = ""
        self.attribute_definitions.clear()
        self.spec_object_types.clear()
        self.enumeration_definitions.clear()
        self.datatype_definitions.clear()
        self.enum_values.clear()
        
        self.debug_info = {
            'total_spec_objects': 0,
            'successfully_parsed': 0,
            'empty_requirements': 0,
            'parsing_errors': 0,
            'namespace_used': None,
            'file_structure': {}
        }
    
    def _parse_reqifz_archive(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse ReqIFZ archive file"""
        print("📦 Extracting ReqIFZ archive...")
        
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find .reqif files
            reqif_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.reqif'):
                        reqif_files.append(os.path.join(root, file))
            
            if not reqif_files:
                raise ValueError("No .reqif files found in archive")
            
            print(f"📄 Found {len(reqif_files)} ReqIF file(s) in archive")
            
            # Parse all files and combine results
            all_requirements = []
            for reqif_file in reqif_files:
                print(f"📖 Parsing {os.path.basename(reqif_file)}...")
                requirements = self._parse_reqif_xml(reqif_file)
                
                # Add source file information
                for req in requirements:
                    req['source_file'] = os.path.basename(reqif_file)
                
                all_requirements.extend(requirements)
            
            return all_requirements
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _parse_reqif_xml(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse ReqIF XML file with improved namespace handling"""
        try:
            # Parse XML with namespace detection
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Detect and register namespaces
            self._detect_namespaces(root)
            
            print(f"🔍 Detected namespace: {self.debug_info['namespace_used']}")
            print(f"🔍 Root element: {root.tag}")
            
            # Analyze file structure
            self._analyze_file_structure(root)
            
            # Build definition catalogs first
            self._build_definition_catalogs(root)
            
            # Extract and process requirements
            requirements = self._extract_requirements(root)
            
            print(f"✅ Successfully parsed {len(requirements)} requirements")
            self._print_parsing_summary()
            
            return requirements
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML structure: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"XML parsing error: {str(e)}")
    
    def _detect_namespaces(self, root):
        """Detect and register XML namespaces dynamically"""
        # Extract namespace from root tag
        if '}' in root.tag:
            self.root_ns = root.tag.split('}')[0] + '}'
            self.namespaces['reqif'] = self.root_ns[1:-1]  # Remove { }
            self.debug_info['namespace_used'] = self.root_ns[1:-1]
        else:
            self.root_ns = ""
            self.debug_info['namespace_used'] = "No namespace"
        
        # Register common namespaces
        for prefix, uri in root.attrib.items():
            if prefix.startswith('xmlns:'):
                ns_prefix = prefix[6:]  # Remove 'xmlns:'
                self.namespaces[ns_prefix] = uri
                # Register with ElementTree
                try:
                    ET.register_namespace(ns_prefix, uri)
                except:
                    pass
    
    def _analyze_file_structure(self, root):
        """Analyze file structure to understand content organization"""
        structure = {}
        
        # Count different element types
        for elem in root.iter():
            tag = self._clean_tag(elem.tag)
            structure[tag] = structure.get(tag, 0) + 1
        
        self.debug_info['file_structure'] = structure
        
        # Log key findings
        key_elements = ['SPEC-OBJECT', 'ATTRIBUTE-DEFINITION-STRING', 
                       'ATTRIBUTE-DEFINITION-XHTML', 'SPEC-OBJECT-TYPE']
        
        for elem_type in key_elements:
            count = structure.get(elem_type, 0)
            if count > 0:
                print(f"🔍 Found {count} {elem_type} elements")
    
    def _clean_tag(self, tag: str) -> str:
        """Remove namespace from tag name"""
        if '}' in tag:
            return tag.split('}')[1]
        return tag
    
    def _build_definition_catalogs(self, root):
        """Build comprehensive definition catalogs"""
        print("📚 Building definition catalogs...")
        
        # Build attribute definitions
        self._build_attribute_definitions(root)
        
        # Build enumeration definitions and values
        self._build_enumeration_catalog(root)
        
        # Build spec object types
        self._build_spec_object_types(root)
        
        print(f"📚 Catalogs built:")
        print(f"   • Attribute definitions: {len(self.attribute_definitions)}")
        print(f"   • Enumeration definitions: {len(self.enumeration_definitions)}")
        print(f"   • Enum values: {len(self.enum_values)}")
        print(f"   • Spec object types: {len(self.spec_object_types)}")
    
    def _build_attribute_definitions(self, root):
        """Build attribute definition catalog with improved searching"""
        # Search patterns for different attribute definition types
        patterns = [
            'ATTRIBUTE-DEFINITION-STRING',
            'ATTRIBUTE-DEFINITION-XHTML', 
            'ATTRIBUTE-DEFINITION-ENUMERATION',
            'ATTRIBUTE-DEFINITION-INTEGER',
            'ATTRIBUTE-DEFINITION-REAL',
            'ATTRIBUTE-DEFINITION-DATE',
            'ATTRIBUTE-DEFINITION-BOOLEAN'
        ]
        
        for pattern in patterns:
            # Try with and without namespace
            elements = root.findall(f".//{pattern}")
            if not elements and self.root_ns:
                elements = root.findall(f".//{self.root_ns}{pattern}")
            
            for elem in elements:
                self._process_attribute_definition(elem, pattern)
    
    def _process_attribute_definition(self, elem, elem_type):
        """Process individual attribute definition"""
        # Get identifier - try multiple attribute names
        identifier = (elem.get('IDENTIFIER') or 
                     elem.get('identifier') or
                     elem.get('ID') or
                     elem.get('id'))
        
        if not identifier:
            return
        
        # Get human-readable name
        long_name = (elem.get('LONG-NAME') or 
                    elem.get('long-name') or
                    elem.get('NAME') or
                    elem.get('name') or
                    identifier)
        
        # Determine data type
        data_type = elem_type.replace('ATTRIBUTE-DEFINITION-', '').lower()
        
        # Store definition
        self.attribute_definitions[identifier] = {
            'identifier': identifier,
            'long_name': long_name,
            'data_type': data_type,
            'element': elem
        }
    
    def _build_enumeration_catalog(self, root):
        """Build enumeration definitions and values"""
        # Find enumeration definitions
        enum_defs = root.findall('.//ENUM-DEFINITION')
        if not enum_defs and self.root_ns:
            enum_defs = root.findall(f'.//{self.root_ns}ENUM-DEFINITION')
        
        for enum_def in enum_defs:
            enum_id = (enum_def.get('IDENTIFIER') or 
                      enum_def.get('identifier') or
                      enum_def.get('ID') or
                      enum_def.get('id'))
            
            if not enum_id:
                continue
            
            enum_name = (enum_def.get('LONG-NAME') or 
                        enum_def.get('long-name') or
                        enum_id)
            
            self.enumeration_definitions[enum_id] = {
                'identifier': enum_id,
                'long_name': enum_name,
                'values': {}
            }
            
            # Find enum values
            enum_values = enum_def.findall('.//ENUM-VALUE')
            if not enum_values and self.root_ns:
                enum_values = enum_def.findall(f'.//{self.root_ns}ENUM-VALUE')
            
            for enum_value in enum_values:
                val_id = (enum_value.get('IDENTIFIER') or 
                         enum_value.get('identifier') or
                         enum_value.get('ID') or
                         enum_value.get('id'))
                
                val_name = (enum_value.get('LONG-NAME') or 
                           enum_value.get('long-name') or
                           val_id)
                
                if val_id:
                    self.enum_values[val_id] = val_name
                    self.enumeration_definitions[enum_id]['values'][val_id] = val_name
    
    def _build_spec_object_types(self, root):
        """Build spec object type catalog"""
        spec_types = root.findall('.//SPEC-OBJECT-TYPE')
        if not spec_types and self.root_ns:
            spec_types = root.findall(f'.//{self.root_ns}SPEC-OBJECT-TYPE')
        
        for spec_type in spec_types:
            type_id = (spec_type.get('IDENTIFIER') or 
                      spec_type.get('identifier') or
                      spec_type.get('ID') or
                      spec_type.get('id'))
            
            if not type_id:
                continue
            
            type_name = (spec_type.get('LONG-NAME') or 
                        spec_type.get('long-name') or
                        type_id)
            
            self.spec_object_types[type_id] = {
                'identifier': type_id,
                'long_name': type_name
            }
    
    def _extract_requirements(self, root) -> List[Dict[str, Any]]:
        """Extract requirements with improved content extraction"""
        print("📋 Extracting requirements...")
        
        # Find all SPEC-OBJECT elements
        spec_objects = root.findall('.//SPEC-OBJECT')
        if not spec_objects and self.root_ns:
            spec_objects = root.findall(f'.//{self.root_ns}SPEC-OBJECT')
        
        self.debug_info['total_spec_objects'] = len(spec_objects)
        print(f"🔍 Found {len(spec_objects)} SPEC-OBJECT elements")
        
        requirements = []
        
        for i, spec_obj in enumerate(spec_objects):
            try:
                req = self._extract_single_requirement(spec_obj, i)
                if req:
                    requirements.append(req)
                    self.debug_info['successfully_parsed'] += 1
                else:
                    self.debug_info['empty_requirements'] += 1
                    
            except Exception as e:
                print(f"⚠️ Error parsing requirement {i}: {str(e)}")
                self.debug_info['parsing_errors'] += 1
                continue
        
        return requirements
    
    def _extract_single_requirement(self, spec_obj, index: int) -> Optional[Dict[str, Any]]:
        """Extract single requirement with comprehensive content extraction"""
        # Get basic identifiers
        req_id = (spec_obj.get('IDENTIFIER') or 
                 spec_obj.get('identifier') or
                 spec_obj.get('ID') or
                 spec_obj.get('id') or
                 f"REQ_{index}")
        
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
            'raw_content': {}
        }
        
        # Get type reference
        type_ref = self._extract_type_reference(spec_obj)
        if type_ref and type_ref in self.spec_object_types:
            requirement['type'] = self.spec_object_types[type_ref]['long_name']
        elif type_ref:
            requirement['type'] = type_ref
        
        # Extract attribute values
        self._extract_attribute_values(spec_obj, requirement)
        
        # Smart field mapping
        self._smart_field_mapping(requirement)
        
        # Ensure we have meaningful content
        self._ensure_meaningful_content(requirement)
        
        return requirement
    
    def _extract_type_reference(self, spec_obj) -> Optional[str]:
        """Extract type reference from SPEC-OBJECT"""
        # Look for TYPE element
        type_elem = spec_obj.find('.//TYPE')
        if type_elem is None and self.root_ns:
            type_elem = spec_obj.find(f'.//{self.root_ns}TYPE')
        
        if type_elem is not None:
            # Look for SPEC-OBJECT-TYPE-REF
            type_ref = (type_elem.get('SPEC-OBJECT-TYPE-REF') or
                       type_elem.get('spec-object-type-ref'))
            return type_ref
        
        return None
    
    def _extract_attribute_values(self, spec_obj, requirement: Dict[str, Any]):
        """Extract all attribute values with improved content extraction"""
        # Find VALUES container
        values_elem = spec_obj.find('.//VALUES')
        if values_elem is None and self.root_ns:
            values_elem = spec_obj.find(f'.//{self.root_ns}VALUES')
        
        if values_elem is None:
            return
        
        # Find all attribute value elements
        attr_value_patterns = [
            'ATTRIBUTE-VALUE-STRING',
            'ATTRIBUTE-VALUE-XHTML',
            'ATTRIBUTE-VALUE-ENUMERATION',
            'ATTRIBUTE-VALUE-INTEGER',
            'ATTRIBUTE-VALUE-REAL',
            'ATTRIBUTE-VALUE-DATE',
            'ATTRIBUTE-VALUE-BOOLEAN'
        ]
        
        for pattern in attr_value_patterns:
            elements = values_elem.findall(f'.//{pattern}')
            if not elements and self.root_ns:
                elements = values_elem.findall(f'.//{self.root_ns}{pattern}')
            
            for elem in elements:
                self._process_attribute_value(elem, requirement, pattern)
    
    def _process_attribute_value(self, attr_value_elem, requirement: Dict[str, Any], value_type: str):
        """Process individual attribute value with improved content extraction"""
        # Get attribute definition reference
        attr_def_ref = self._get_attribute_definition_reference(attr_value_elem)
        
        if not attr_def_ref:
            return
        
        # Extract the actual value
        value = self._extract_value_content(attr_value_elem, value_type)
        
        if not value:
            return
        
        # Store raw content
        requirement['raw_content'][attr_def_ref] = value
        
        # Get human-readable attribute name
        attr_name = attr_def_ref
        if attr_def_ref in self.attribute_definitions:
            attr_name = self.attribute_definitions[attr_def_ref]['long_name']
        
        # Store with human-readable name
        requirement['attributes'][attr_name] = value
    
    def _get_attribute_definition_reference(self, attr_value_elem) -> Optional[str]:
        """Get attribute definition reference from attribute value element"""
        # Method 1: Direct attribute
        attr_def_ref = (attr_value_elem.get('ATTRIBUTE-DEFINITION-REF') or
                       attr_value_elem.get('attribute-definition-ref'))
        
        if attr_def_ref:
            return attr_def_ref
        
        # Method 2: DEFINITION child element
        def_elem = attr_value_elem.find('.//DEFINITION')
        if def_elem is None and self.root_ns:
            def_elem = attr_value_elem.find(f'.//{self.root_ns}DEFINITION')
        
        if def_elem is not None:
            # Look for various reference elements
            ref_patterns = [
                'ATTRIBUTE-DEFINITION-STRING-REF',
                'ATTRIBUTE-DEFINITION-XHTML-REF',
                'ATTRIBUTE-DEFINITION-ENUMERATION-REF',
                'ATTRIBUTE-DEFINITION-INTEGER-REF',
                'ATTRIBUTE-DEFINITION-REAL-REF',
                'ATTRIBUTE-DEFINITION-DATE-REF',
                'ATTRIBUTE-DEFINITION-BOOLEAN-REF'
            ]
            
            for pattern in ref_patterns:
                ref_elem = def_elem.find(f'.//{pattern}')
                if ref_elem is None and self.root_ns:
                    ref_elem = def_elem.find(f'.//{self.root_ns}{pattern}')
                
                if ref_elem is not None and ref_elem.text:
                    return ref_elem.text.strip()
        
        return None
    
    def _extract_value_content(self, attr_value_elem, value_type: str) -> str:
        """Extract actual content from attribute value element"""
        if 'STRING' in value_type:
            return self._extract_string_value(attr_value_elem)
        elif 'XHTML' in value_type:
            return self._extract_xhtml_value(attr_value_elem)
        elif 'ENUMERATION' in value_type:
            return self._extract_enumeration_value(attr_value_elem)
        elif 'INTEGER' in value_type or 'REAL' in value_type:
            return self._extract_numeric_value(attr_value_elem)
        elif 'DATE' in value_type:
            return self._extract_date_value(attr_value_elem)
        elif 'BOOLEAN' in value_type:
            return self._extract_boolean_value(attr_value_elem)
        else:
            return self._extract_generic_value(attr_value_elem)
    
    def _extract_string_value(self, elem) -> str:
        """Extract STRING value"""
        # Try attribute first
        value = elem.get('THE-VALUE') or elem.get('the-value')
        if value:
            return str(value)
        
        # Try child element
        the_value_elem = elem.find('.//THE-VALUE')
        if the_value_elem is None and self.root_ns:
            the_value_elem = elem.find(f'.//{self.root_ns}THE-VALUE')
        
        if the_value_elem is not None:
            return the_value_elem.text or ''
        
        return ''
    
    def _extract_xhtml_value(self, elem) -> str:
        """Extract XHTML value with comprehensive text extraction"""
        # Find THE-VALUE element
        the_value_elem = elem.find('.//THE-VALUE')
        if the_value_elem is None and self.root_ns:
            the_value_elem = elem.find(f'.//{self.root_ns}THE-VALUE')
        
        if the_value_elem is None:
            return ''
        
        # Extract text content recursively
        return self._extract_text_from_element(the_value_elem)
    
    def _extract_text_from_element(self, element) -> str:
        """Recursively extract all text content from XML element"""
        if element is None:
            return ''
        
        texts = []
        
        # Add element's direct text
        if element.text:
            texts.append(element.text.strip())
        
        # Process all children
        for child in element:
            child_tag = self._clean_tag(child.tag)
            
            # Handle special elements
            if child_tag in ['br', 'BR']:
                texts.append(' ')  # Convert breaks to spaces
            elif child_tag in ['p', 'P', 'div', 'DIV']:
                # Add paragraph breaks
                child_text = self._extract_text_from_element(child)
                if child_text:
                    texts.append(child_text)
                    texts.append(' ')
            elif child_tag in ['object', 'OBJECT']:
                # Handle embedded objects
                alt_text = child.get('alt', '')
                if alt_text and alt_text != 'OLE Object':
                    texts.append(alt_text)
            else:
                # Regular child element
                child_text = self._extract_text_from_element(child)
                if child_text:
                    texts.append(child_text)
            
            # Add tail text
            if child.tail:
                texts.append(child.tail.strip())
        
        # Join and clean up
        full_text = ' '.join(texts)
        
        # Clean up whitespace and decode HTML entities
        full_text = re.sub(r'\s+', ' ', full_text)
        full_text = html.unescape(full_text)
        
        return full_text.strip()
    
    def _extract_enumeration_value(self, elem) -> str:
        """Extract enumeration value with proper resolution"""
        enum_values = []
        
        # Find VALUES container
        values_container = elem.find('.//VALUES')
        if values_container is None and self.root_ns:
            values_container = elem.find(f'.//{self.root_ns}VALUES')
        
        if values_container is not None:
            # Find ENUM-VALUE-REF elements
            enum_refs = values_container.findall('.//ENUM-VALUE-REF')
            if not enum_refs and self.root_ns:
                enum_refs = values_container.findall(f'.//{self.root_ns}ENUM-VALUE-REF')
            
            for enum_ref in enum_refs:
                ref_value = enum_ref.get('REF') or enum_ref.get('ref') or enum_ref.text
                if ref_value:
                    # Resolve to human-readable name
                    human_name = self.enum_values.get(ref_value, ref_value)
                    enum_values.append(human_name)
        
        return ', '.join(enum_values) if enum_values else ''
    
    def _extract_numeric_value(self, elem) -> str:
        """Extract numeric value (integer or real)"""
        value = elem.get('THE-VALUE') or elem.get('the-value')
        if value is not None:
            return str(value)
        
        the_value_elem = elem.find('.//THE-VALUE')
        if the_value_elem is None and self.root_ns:
            the_value_elem = elem.find(f'.//{self.root_ns}THE-VALUE')
        
        if the_value_elem is not None and the_value_elem.text:
            return the_value_elem.text
        
        return ''
    
    def _extract_date_value(self, elem) -> str:
        """Extract date value"""
        return self._extract_numeric_value(elem)  # Same logic as numeric
    
    def _extract_boolean_value(self, elem) -> str:
        """Extract boolean value with human-readable conversion"""
        value = self._extract_numeric_value(elem)
        if value.lower() in ['true', '1', 'yes']:
            return 'Yes'
        elif value.lower() in ['false', '0', 'no']:
            return 'No'
        return value
    
    def _extract_generic_value(self, elem) -> str:
        """Generic value extraction as fallback"""
        # Try various methods
        value = (elem.get('THE-VALUE') or 
                elem.get('the-value') or
                elem.get('VALUE') or
                elem.get('value'))
        
        if value:
            return str(value)
        
        # Try child elements
        the_value_elem = elem.find('.//THE-VALUE')
        if the_value_elem is None and self.root_ns:
            the_value_elem = elem.find(f'.//{self.root_ns}THE-VALUE')
        
        if the_value_elem is not None:
            return self._extract_text_from_element(the_value_elem)
        
        # Last resort: extract any text content
        return self._extract_text_from_element(elem)
    
    def _smart_field_mapping(self, requirement: Dict[str, Any]):
        """Smart mapping of attributes to standard requirement fields"""
        # Common field mappings
        field_mappings = {
            'title': ['title', 'name', 'heading', 'object', 'text', 'caption', 'summary'],
            'description': ['description', 'detail', 'content', 'specification', 'rationale', 'text'],
            'priority': ['priority', 'importance', 'criticality', 'level'],
            'status': ['status', 'state', 'phase', 'condition']
        }
        
        for field, keywords in field_mappings.items():
            if requirement[field]:  # Don't override if already set
                continue
            
            # Look for matching attributes
            for attr_name, attr_value in requirement['attributes'].items():
                if not attr_value:
                    continue
                
                attr_lower = attr_name.lower()
                if any(keyword in attr_lower for keyword in keywords):
                    # Additional quality checks for title/description
                    if field == 'title' and self._is_good_title(attr_value):
                        requirement[field] = str(attr_value)
                        break
                    elif field == 'description' and self._is_good_description(attr_value):
                        requirement[field] = str(attr_value)
                        break
                    elif field in ['priority', 'status']:
                        requirement[field] = str(attr_value)
                        break
    
    def _is_good_title(self, value: str) -> bool:
        """Check if value looks like a good title"""
        if not value or len(value) < 2:
            return False
        
        # Good titles are typically:
        # - Not too long (under 200 chars)
        # - Not just numbers or IDs
        # - Have reasonable text content
        return (len(value) < 200 and 
                not value.replace('.', '').replace('-', '').isdigit() and
                any(c.isalpha() for c in value))
    
    def _is_good_description(self, value: str) -> bool:
        """Check if value looks like a good description"""
        if not value or len(value) < 10:
            return False
        
        # Good descriptions are typically:
        # - Longer than titles
        # - Have multiple words
        # - Contain meaningful text
        return (len(value) >= 10 and 
                ' ' in value and
                len(value.split()) >= 3 and
                any(c.isalpha() for c in value))
    
    def _ensure_meaningful_content(self, requirement: Dict[str, Any]):
        """Ensure requirement has meaningful content"""
        # Ensure we have a title
        if not requirement['title']:
            # Try to find the best title candidate
            candidates = []
            for attr_name, attr_value in requirement['attributes'].items():
                if attr_value and self._is_good_title(str(attr_value)):
                    candidates.append((attr_name, str(attr_value)))
            
            if candidates:
                # Choose the shortest reasonable title
                best_title = min(candidates, key=lambda x: len(x[1]))
                requirement['title'] = best_title[1]
            else:
                requirement['title'] = requirement['id']
        
        # Ensure we have a description
        if not requirement['description']:
            # Try to find the best description candidate
            candidates = []
            for attr_name, attr_value in requirement['attributes'].items():
                if attr_value and self._is_good_description(str(attr_value)):
                    candidates.append((attr_name, str(attr_value)))
            
            if candidates:
                # Choose the longest reasonable description
                best_desc = max(candidates, key=lambda x: len(x[1]))
                requirement['description'] = best_desc[1]
        
        # Clean up empty attributes
        requirement['attributes'] = {k: v for k, v in requirement['attributes'].items() if v}
    
    def _print_parsing_summary(self):
        """Print comprehensive parsing summary"""
        print("\n" + "="*60)
        print("📊 PARSING SUMMARY")
        print("="*60)
        print(f"Total SPEC-OBJECT elements found: {self.debug_info['total_spec_objects']}")
        print(f"Successfully parsed requirements: {self.debug_info['successfully_parsed']}")
        print(f"Empty/skipped requirements: {self.debug_info['empty_requirements']}")
        print(f"Parsing errors: {self.debug_info['parsing_errors']}")
        
        if self.debug_info['total_spec_objects'] > 0:
            success_rate = (self.debug_info['successfully_parsed'] / 
                          self.debug_info['total_spec_objects'] * 100)
            print(f"Success rate: {success_rate:.1f}%")
        
        print(f"\nNamespace used: {self.debug_info['namespace_used']}")
        print(f"Attribute definitions found: {len(self.attribute_definitions)}")
        print(f"Enumeration values found: {len(self.enum_values)}")
        
        # Show file structure
        print(f"\nFile structure analysis:")
        structure = self.debug_info['file_structure']
        key_elements = ['SPEC-OBJECT', 'ATTRIBUTE-DEFINITION-STRING', 
                       'ATTRIBUTE-DEFINITION-XHTML', 'ATTRIBUTE-VALUE-STRING',
                       'ATTRIBUTE-VALUE-XHTML', 'SPEC-OBJECT-TYPE']
        
        for elem in key_elements:
            count = structure.get(elem, 0)
            if count > 0:
                print(f"  • {elem}: {count}")
        
        print("="*60)
    
    def get_parsing_diagnostics(self) -> Dict[str, Any]:
        """Get detailed parsing diagnostics for troubleshooting"""
        return {
            'debug_info': self.debug_info.copy(),
            'catalogs': {
                'attribute_definitions': len(self.attribute_definitions),
                'spec_object_types': len(self.spec_object_types),
                'enumeration_definitions': len(self.enumeration_definitions),
                'enum_values': len(self.enum_values)
            },
            'namespace_info': {
                'detected_namespaces': self.namespaces.copy(),
                'root_namespace': self.root_ns
            },
            'sample_definitions': {
                'attribute_defs': list(self.attribute_definitions.keys())[:5],
                'enum_values': list(self.enum_values.keys())[:5],
                'spec_types': list(self.spec_object_types.keys())[:5]
            }
        }
    
    def validate_parsing_quality(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the quality of parsed requirements"""
        if not requirements:
            return {
                'quality_score': 0,
                'issues': ['No requirements found'],
                'recommendations': ['Check if file contains SPEC-OBJECT elements']
            }
        
        quality_metrics = {
            'total_requirements': len(requirements),
            'with_titles': 0,
            'with_descriptions': 0,
            'with_types': 0,
            'with_attributes': 0,
            'meaningful_titles': 0,
            'meaningful_descriptions': 0
        }
        
        for req in requirements:
            if req.get('title') and req['title'] != req.get('id'):
                quality_metrics['with_titles'] += 1
                if self._is_good_title(req['title']):
                    quality_metrics['meaningful_titles'] += 1
            
            if req.get('description'):
                quality_metrics['with_descriptions'] += 1
                if self._is_good_description(req['description']):
                    quality_metrics['meaningful_descriptions'] += 1
            
            if req.get('type'):
                quality_metrics['with_types'] += 1
            
            if req.get('attributes'):
                quality_metrics['with_attributes'] += 1
        
        total = len(requirements)
        quality_score = (
            (quality_metrics['meaningful_titles'] / total) * 0.3 +
            (quality_metrics['meaningful_descriptions'] / total) * 0.3 +
            (quality_metrics['with_types'] / total) * 0.2 +
            (quality_metrics['with_attributes'] / total) * 0.2
        ) * 100
        
        # Generate issues and recommendations
        issues = []
        recommendations = []
        
        if quality_metrics['meaningful_titles'] < total * 0.8:
            issues.append(f"Only {quality_metrics['meaningful_titles']} of {total} requirements have meaningful titles")
            recommendations.append("Check attribute-to-field mapping for title extraction")
        
        if quality_metrics['meaningful_descriptions'] < total * 0.6:
            issues.append(f"Only {quality_metrics['meaningful_descriptions']} of {total} requirements have good descriptions")
            recommendations.append("Verify XHTML content extraction is working properly")
        
        if quality_metrics['with_types'] < total * 0.5:
            issues.append(f"Only {quality_metrics['with_types']} of {total} requirements have type information")
            recommendations.append("Check SPEC-OBJECT-TYPE reference resolution")
        
        return {
            'quality_score': round(quality_score, 1),
            'metrics': quality_metrics,
            'issues': issues,
            'recommendations': recommendations
        }


# Enhanced debug function for testing
def debug_parsing_with_improved_parser(file_path: str):
    """Debug function using the improved parser"""
    print("🔍 DEBUGGING WITH IMPROVED PARSER")
    print("="*60)
    
    parser = ImprovedReqIFParser()
    
    try:
        # Parse the file
        requirements = parser.parse_file(file_path)
        
        # Get diagnostics
        diagnostics = parser.get_parsing_diagnostics()
        
        # Validate quality
        quality_report = parser.validate_parsing_quality(requirements)
        
        print(f"\n📊 QUALITY REPORT")
        print("-"*40)
        print(f"Quality Score: {quality_report['quality_score']}%")
        print(f"Total Requirements: {quality_report['metrics']['total_requirements']}")
        print(f"Meaningful Titles: {quality_report['metrics']['meaningful_titles']}")
        print(f"Meaningful Descriptions: {quality_report['metrics']['meaningful_descriptions']}")
        
        if quality_report['issues']:
            print(f"\n⚠️ ISSUES FOUND:")
            for issue in quality_report['issues']:
                print(f"  • {issue}")
        
        if quality_report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in quality_report['recommendations']:
                print(f"  • {rec}")
        
        # Show sample requirements
        print(f"\n📋 SAMPLE REQUIREMENTS (first 3):")
        print("-"*40)
        for i, req in enumerate(requirements[:3]):
            print(f"\nRequirement {i+1}:")
            print(f"  ID: {req.get('id', 'N/A')}")
            print(f"  Title: {req.get('title', 'N/A')}")
            print(f"  Type: {req.get('type', 'N/A')}")
            print(f"  Description: {req.get('description', 'N/A')[:100]}...")
            print(f"  Attributes: {len(req.get('attributes', {}))}")
        
        # Show namespace and structure info
        print(f"\n🔍 TECHNICAL DETAILS:")
        print("-"*40)
        print(f"Namespace: {diagnostics['namespace_info']['root_namespace']}")
        print(f"File structure elements found:")
        for elem, count in diagnostics['debug_info']['file_structure'].items():
            if count > 0:
                print(f"  • {elem}: {count}")
        
        return requirements
        
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


# Compatibility function to replace the original parser
def create_improved_parser_replacement():
    """Create a drop-in replacement for the original ReqIFParser"""
    
    class ReqIFParserReplacement:
        """Drop-in replacement for original ReqIFParser with improved logic"""
        
        def __init__(self):
            self.improved_parser = ImprovedReqIFParser()
        
        def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
            """Parse file using improved parser"""
            return self.improved_parser.parse_file(file_path)
        
        def get_file_info(self, file_path: str) -> Dict[str, Any]:
            """Get file information"""
            try:
                # Parse and get basic info
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
    
    return ReqIFParserReplacement()


if __name__ == "__main__":
    import sys
    
    print("🔧 Improved ReqIF Parser - Enhanced Content Extraction")
    print("="*60)
    print("Key improvements:")
    print("✅ Better namespace handling")
    print("✅ Enhanced XHTML content extraction") 
    print("✅ Improved reference resolution")
    print("✅ Smart field mapping")
    print("✅ Quality validation")
    print("✅ Comprehensive error handling")
    print("✅ Detailed diagnostics")
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"\n🔍 Testing with file: {file_path}")
        debug_parsing_with_improved_parser(file_path)
    else:
        print("\n💡 Usage: python reqif_parser_improved.py <path_to_reqif_file>")
        print("💡 Or import and use ImprovedReqIFParser class directly")
        
        # Example usage
        print("\n📝 Example usage:")
        print("```python")
        print("from reqif_parser_improved import ImprovedReqIFParser")
        print("parser = ImprovedReqIFParser()")
        print("requirements = parser.parse_file('your_file.reqif')")
        print("quality = parser.validate_parsing_quality(requirements)")
        print("print(f'Quality score: {quality[\"quality_score\"]}%')")
        print("```")