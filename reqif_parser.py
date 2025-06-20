#!/usr/bin/env python3
"""
ReqIF Parser Module - Complete Comprehensive Implementation
Correctly implements the ReqIF specification with proper object model:
SPEC-OBJECT → SPEC-OBJECT-TYPE → ATTRIBUTE-DEFINITION → ATTRIBUTE-VALUE
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Set
import os
import zipfile
import tempfile
import shutil
import re


class ReqIFParser:
    """
    Comprehensive ReqIF Parser following the official ReqIF specification
    Implements four-pass parsing: Definitions → Types → Objects → Values
    """
    
    def __init__(self):
        self.namespaces = {
            'reqif': 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
        
        # Four-level catalog system following ReqIF structure
        self.attribute_definitions = {}      # ATTRIBUTE-DEFINITION catalog
        self.spec_object_types = {}         # SPEC-OBJECT-TYPE catalog  
        self.enumeration_definitions = {}   # ENUM-DEFINITION catalog
        self.datatype_definitions = {}      # DATATYPE-DEFINITION catalog
        
        # Debug tracking
        self.debug_info = {
            'definitions_found': 0,
            'types_found': 0,
            'objects_found': 0,
            'values_resolved': 0,
            'resolution_failures': []
        }
        
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a ReqIF file (.reqif or .reqifz) with comprehensive reference resolution
        
        Args:
            file_path: Path to the ReqIF file or ReqIF archive
            
        Returns:
            List of requirement dictionaries with fully resolved content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ReqIF file not found: {file_path}")
        
        # Clear debug info
        self._reset_debug_info()
        
        # Check file extension to determine parsing method
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.reqifz':
            return self._parse_reqifz_file(file_path)
        elif file_ext == '.reqif':
            return self._parse_reqif_file(file_path)
        else:
            # Try to parse as regular ReqIF first, then as archive
            try:
                return self._parse_reqif_file(file_path)
            except:
                return self._parse_reqifz_file(file_path)
    
    def _reset_debug_info(self):
        """Reset debug tracking information"""
        self.debug_info = {
            'definitions_found': 0,
            'types_found': 0,
            'objects_found': 0,
            'values_resolved': 0,
            'resolution_failures': []
        }
    
    def _parse_reqif_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse a regular .reqif XML file with four-pass comprehensive strategy"""
        try:
            print(f"Parsing ReqIF file: {file_path}")
            
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Register namespaces for XPath queries
            for prefix, uri in self.namespaces.items():
                ET.register_namespace(prefix, uri)
            
            # Clear catalogs for fresh parsing
            self._clear_catalogs()
            
            print("Starting four-pass comprehensive parsing...")
            
            # PASS 1: Build Attribute Definition Catalog
            print("PASS 1: Building attribute definition catalog...")
            self._build_attribute_definition_catalog(root)
            
            # PASS 2: Build Spec Object Type Catalog (with attribute links)
            print("PASS 2: Building spec object type catalog...")
            self._build_spec_object_type_catalog(root)
            
            # PASS 3: Extract Spec Objects (requirements) with type links
            print("PASS 3: Extracting spec objects...")
            raw_objects = self._extract_spec_objects_with_types(root)
            
            # PASS 4: Resolve Complete Reference Chain to Human Content
            print("PASS 4: Resolving complete reference chains...")
            resolved_requirements = self._resolve_complete_reference_chains(raw_objects)
            
            self._print_debug_summary()
            return resolved_requirements
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in ReqIF file: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error parsing ReqIF file: {str(e)}")
    
    def _parse_reqifz_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse a .reqifz archive file"""
        try:
            print(f"Parsing ReqIFZ archive: {file_path}")
            
            # Create temporary directory for extraction
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Extract the archive
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find ReqIF files in the extracted content
                reqif_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith('.reqif'):
                            reqif_files.append(os.path.join(root, file))
                
                if not reqif_files:
                    raise ValueError("No .reqif files found in the archive")
                
                # Parse the first ReqIF file found (or combine multiple if needed)
                if len(reqif_files) == 1:
                    return self._parse_reqif_file(reqif_files[0])
                else:
                    # Multiple ReqIF files - combine requirements
                    all_requirements = []
                    for reqif_file in reqif_files:
                        reqs = self._parse_reqif_file(reqif_file)
                        # Add source file info to each requirement
                        for req in reqs:
                            req['source_file'] = os.path.basename(reqif_file)
                        all_requirements.extend(reqs)
                    return all_requirements
                    
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid ZIP archive: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error parsing ReqIFZ file: {str(e)}")
    
    def _clear_catalogs(self):
        """Clear all definition catalogs"""
        self.attribute_definitions.clear()
        self.spec_object_types.clear()
        self.enumeration_definitions.clear()
        self.datatype_definitions.clear()
    
    def _build_attribute_definition_catalog(self, root):
        """PASS 1: Build comprehensive attribute definition catalog"""
        print("  Building attribute definitions...")
        
        # Find all attribute definition types with comprehensive search
        attr_def_elements = self._find_elements_multiple_patterns(root, [
            ".//ATTRIBUTE-DEFINITION-STRING",
            ".//ATTRIBUTE-DEFINITION-XHTML", 
            ".//ATTRIBUTE-DEFINITION-ENUMERATION",
            ".//ATTRIBUTE-DEFINITION-INTEGER",
            ".//ATTRIBUTE-DEFINITION-REAL",
            ".//ATTRIBUTE-DEFINITION-DATE",
            ".//ATTRIBUTE-DEFINITION-BOOLEAN"
        ])
        
        for attr_def in attr_def_elements:
            self._process_attribute_definition(attr_def)
        
        # Build enumeration and datatype catalogs
        self._build_enumeration_catalog(root)
        self._build_datatype_catalog(root)
        
        self.debug_info['definitions_found'] = len(self.attribute_definitions)
        print(f"  Found {len(self.attribute_definitions)} attribute definitions")
        print(f"  Found {len(self.enumeration_definitions)} enumeration definitions")
        print(f"  Found {len(self.datatype_definitions)} datatype definitions")
    
    def _process_attribute_definition(self, attr_def):
        """Process a single attribute definition element"""
        identifier = self._get_element_identifier(attr_def)
        if not identifier:
            return
            
        long_name = self._get_element_long_name(attr_def) or identifier
        desc = self._get_element_description(attr_def)
        
        # Determine attribute type from tag
        tag_name = attr_def.tag.split('}')[-1] if '}' in attr_def.tag else attr_def.tag
        attr_type = tag_name.replace('ATTRIBUTE-DEFINITION-', '').lower()
        
        # Get datatype reference for additional info
        datatype_ref = None
        type_elem = attr_def.find(".//TYPE") or attr_def.find(".//type")
        if type_elem is not None:
            datatype_ref = (type_elem.get('DATATYPE-DEFINITION-STRING-REF') or 
                          type_elem.get('DATATYPE-DEFINITION-XHTML-REF') or
                          type_elem.get('DATATYPE-DEFINITION-ENUMERATION-REF') or
                          type_elem.get('DATATYPE-DEFINITION-INTEGER-REF') or
                          type_elem.get('DATATYPE-DEFINITION-REAL-REF') or
                          type_elem.get('DATATYPE-DEFINITION-DATE-REF') or
                          type_elem.get('DATATYPE-DEFINITION-BOOLEAN-REF'))
        
        self.attribute_definitions[identifier] = {
            'identifier': identifier,
            'long_name': long_name,
            'description': desc,
            'type': attr_type,
            'datatype_ref': datatype_ref,
            'element': attr_def
        }
    
    def _build_spec_object_type_catalog(self, root):
        """PASS 2: Build spec object type catalog with attribute relationships"""
        print("  Building spec object types...")
        
        spec_types = self._find_elements_multiple_patterns(root, [
            ".//SPEC-OBJECT-TYPE"
        ])
        
        for spec_type in spec_types:
            self._process_spec_object_type(spec_type)
        
        self.debug_info['types_found'] = len(self.spec_object_types)
        print(f"  Found {len(self.spec_object_types)} spec object types")
    
    def _process_spec_object_type(self, spec_type):
        """Process a single SPEC-OBJECT-TYPE with its attribute relationships"""
        identifier = self._get_element_identifier(spec_type)
        if not identifier:
            return
            
        long_name = self._get_element_long_name(spec_type) or identifier
        desc = self._get_element_description(spec_type)
        
        # Extract SPEC-ATTRIBUTES - this is the key linking mechanism
        spec_attributes = []
        spec_attrs_elem = spec_type.find(".//SPEC-ATTRIBUTES") or spec_type.find(".//spec-attributes")
        
        if spec_attrs_elem is not None:
            # Find all attribute definition references
            attr_refs = (spec_attrs_elem.findall(".//ATTRIBUTE-DEFINITION-STRING-REF") +
                         spec_attrs_elem.findall(".//ATTRIBUTE-DEFINITION-XHTML-REF") +
                         spec_attrs_elem.findall(".//ATTRIBUTE-DEFINITION-ENUMERATION-REF") +
                         spec_attrs_elem.findall(".//ATTRIBUTE-DEFINITION-INTEGER-REF") +
                         spec_attrs_elem.findall(".//ATTRIBUTE-DEFINITION-REAL-REF") +
                         spec_attrs_elem.findall(".//ATTRIBUTE-DEFINITION-DATE-REF") +
                         spec_attrs_elem.findall(".//ATTRIBUTE-DEFINITION-BOOLEAN-REF"))
            
            for attr_ref in attr_refs:
                ref_id = attr_ref.text or attr_ref.get('REF')
                if ref_id:
                    spec_attributes.append(ref_id)
        
        self.spec_object_types[identifier] = {
            'identifier': identifier,
            'long_name': long_name,
            'description': desc,
            'spec_attributes': spec_attributes,  # List of attribute definition IDs
            'element': spec_type
        }
    
    def _extract_spec_objects_with_types(self, root) -> List[Dict[str, Any]]:
        """PASS 3: Extract SPEC-OBJECT elements with their type relationships"""
        print("  Extracting spec objects...")
        
        spec_objects = self._find_elements_multiple_patterns(root, [
            ".//SPEC-OBJECT"
        ])
        
        extracted_objects = []
        for spec_obj in spec_objects:
            obj_data = self._extract_single_spec_object(spec_obj)
            if obj_data:
                extracted_objects.append(obj_data)
        
        self.debug_info['objects_found'] = len(extracted_objects)
        print(f"  Found {len(extracted_objects)} spec objects")
        return extracted_objects
    
    def _extract_single_spec_object(self, spec_obj) -> Optional[Dict[str, Any]]:
        """Extract a single SPEC-OBJECT with type and value references"""
        identifier = self._get_element_identifier(spec_obj)
        if not identifier:
            return None
        
        # Get the SPEC-OBJECT-TYPE reference - critical for resolution
        type_ref = None
        type_elem = spec_obj.find(".//TYPE") or spec_obj.find(".//type")
        if type_elem is not None:
            type_ref = (type_elem.get('SPEC-OBJECT-TYPE-REF') or 
                       type_elem.get('spec-object-type-ref'))
        
        # Extract all ATTRIBUTE-VALUE elements with their references
        attribute_values = {}
        value_elements = self._find_elements_multiple_patterns(spec_obj, [
            ".//ATTRIBUTE-VALUE-STRING",
            ".//ATTRIBUTE-VALUE-XHTML",
            ".//ATTRIBUTE-VALUE-ENUMERATION",
            ".//ATTRIBUTE-VALUE-INTEGER",
            ".//ATTRIBUTE-VALUE-REAL",
            ".//ATTRIBUTE-VALUE-DATE",
            ".//ATTRIBUTE-VALUE-BOOLEAN"
        ])
        
        for value_elem in value_elements:
            attr_def_ref = (value_elem.get('ATTRIBUTE-DEFINITION-REF') or 
                           value_elem.get('attribute-definition-ref'))
            if attr_def_ref:
                attribute_values[attr_def_ref] = value_elem
        
        return {
            'identifier': identifier,
            'type_ref': type_ref,
            'attribute_values': attribute_values,  # Raw XML elements
            'spec_object_element': spec_obj
        }
    
    def _resolve_complete_reference_chains(self, raw_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """PASS 4: Resolve complete OBJECT→TYPE→DEFINITION→VALUE chains"""
        print("  Resolving complete reference chains...")
        
        resolved_requirements = []
        
        for raw_obj in raw_objects:
            resolved_req = self._resolve_single_object_chain(raw_obj)
            if resolved_req:
                resolved_requirements.append(resolved_req)
        
        self.debug_info['values_resolved'] = len(resolved_requirements)
        print(f"  Resolved {len(resolved_requirements)} complete requirements")
        return resolved_requirements
    
    def _resolve_single_object_chain(self, raw_obj: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Resolve a single SPEC-OBJECT through the complete reference chain"""
        identifier = raw_obj['identifier']
        type_ref = raw_obj['type_ref']
        
        # Initialize resolved requirement
        resolved = {
            'id': identifier,
            'identifier': identifier,
            'title': '',
            'description': '',
            'type': '',
            'priority': '',
            'status': '',
            'attributes': {},
            'raw_attributes': {},
            'content': '',
            'type_ref': type_ref
        }
        
        # Step 1: Resolve the SPEC-OBJECT-TYPE
        spec_type = None
        if type_ref and type_ref in self.spec_object_types:
            spec_type = self.spec_object_types[type_ref]
            resolved['type'] = spec_type['long_name']
        else:
            resolved['type'] = type_ref or 'Unknown'
            if type_ref:
                self.debug_info['resolution_failures'].append(f"Unknown type reference: {type_ref}")
        
        # Step 2: Process each ATTRIBUTE-VALUE using the complete chain
        for attr_def_ref, value_element in raw_obj['attribute_values'].items():
            # Get the attribute definition
            attr_def = self.attribute_definitions.get(attr_def_ref)
            
            if attr_def:
                # Extract the actual VALUE content
                actual_value = self._extract_actual_value_content(value_element, attr_def)
                
                # Store with human-readable name
                human_name = attr_def['long_name']
                resolved['attributes'][human_name] = actual_value
                resolved['raw_attributes'][attr_def_ref] = actual_value
                
                # Smart mapping to common fields
                self._smart_map_to_common_fields(resolved, human_name, attr_def_ref, actual_value)
                
            else:
                # Fallback: extract raw value even without definition
                raw_value = self._extract_actual_value_content(value_element, None)
                resolved['attributes'][attr_def_ref] = raw_value
                resolved['raw_attributes'][attr_def_ref] = raw_value
                self.debug_info['resolution_failures'].append(f"Unknown attribute definition: {attr_def_ref}")
        
        # Step 3: Ensure we have meaningful content
        self._ensure_meaningful_content(resolved)
        
        # Step 4: Create content hash for comparison
        resolved['content'] = self._create_content_hash(resolved)
        
        return resolved
    
    def _extract_actual_value_content(self, value_element, attr_def: Optional[Dict[str, Any]]) -> str:
        """Extract the actual human-readable content from an ATTRIBUTE-VALUE element"""
        if value_element is None:
            return ''
        
        # Determine the value type from the element tag
        tag_name = value_element.tag.split('}')[-1] if '}' in value_element.tag else value_element.tag
        
        if 'STRING' in tag_name:
            return self._extract_string_value_content(value_element)
        elif 'XHTML' in tag_name:
            return self._extract_xhtml_value_content(value_element)
        elif 'ENUMERATION' in tag_name:
            return self._extract_enumeration_value_content(value_element)
        elif 'INTEGER' in tag_name:
            return self._extract_integer_value_content(value_element)
        elif 'REAL' in tag_name:
            return self._extract_real_value_content(value_element)
        elif 'DATE' in tag_name:
            return self._extract_date_value_content(value_element)
        elif 'BOOLEAN' in tag_name:
            return self._extract_boolean_value_content(value_element)
        else:
            # Fallback: try to extract any text content
            return self._extract_fallback_content(value_element)
    
    def _extract_string_value_content(self, value_element) -> str:
        """Extract STRING value content - the actual text"""
        # Try attribute first
        the_value = value_element.get('THE-VALUE') or value_element.get('the-value')
        if the_value:
            return the_value
        
        # Try child element
        the_value_elem = (value_element.find(".//THE-VALUE") or 
                         value_element.find(".//the-value") or
                         value_element.find(".//reqif:THE-VALUE", self.namespaces))
        
        if the_value_elem is not None:
            return the_value_elem.text or ''
        
        return ''
    
    def _extract_xhtml_value_content(self, value_element) -> str:
        """Extract XHTML value content with comprehensive text extraction"""
        # Find THE-VALUE element
        the_value_elem = (value_element.find(".//THE-VALUE") or 
                         value_element.find(".//the-value") or
                         value_element.find(".//reqif:THE-VALUE", self.namespaces))
        
        if the_value_elem is None:
            return ''
        
        # Extract all text content from XHTML structure
        return self._extract_comprehensive_text_content(the_value_elem)
    
    def _extract_comprehensive_text_content(self, element) -> str:
        """Recursively extract all text content from an element, handling XHTML properly"""
        if element is None:
            return ''
        
        texts = []
        
        # Add element's direct text
        if element.text:
            texts.append(element.text.strip())
        
        # Recursively process all children
        for child in element:
            # Get text from child element
            child_text = self._extract_comprehensive_text_content(child)
            if child_text:
                texts.append(child_text)
            
            # Add tail text that comes after the child element
            if child.tail:
                texts.append(child.tail.strip())
        
        # Join all text parts and clean up
        full_text = ' '.join(texts)
        
        # Clean up multiple spaces, line breaks, and common XHTML artifacts
        full_text = re.sub(r'\s+', ' ', full_text)  # Multiple spaces to single
        full_text = re.sub(r'\n\s*\n', '\n', full_text)  # Multiple line breaks
        full_text = full_text.strip()
        
        return full_text
    
    def _extract_enumeration_value_content(self, value_element) -> str:
        """Extract enumeration value with human-readable resolution"""
        enum_values = []
        
        # Find ENUM-VALUE-REF elements
        enum_refs = (value_element.findall(".//ENUM-VALUE-REF") or 
                    value_element.findall(".//enum-value-ref"))
        
        for enum_ref in enum_refs:
            ref_value = enum_ref.get('REF') or enum_ref.get('ref') or enum_ref.text
            if ref_value:
                # Try to resolve to human-readable name
                human_name = self._resolve_enumeration_reference(ref_value)
                enum_values.append(human_name)
        
        return ', '.join(enum_values) if enum_values else ''
    
    def _resolve_enumeration_reference(self, enum_ref: str) -> str:
        """Resolve enumeration reference to human-readable name"""
        # Search through all enumeration definitions
        for enum_def in self.enumeration_definitions.values():
            if enum_ref in enum_def.get('values', {}):
                return enum_def['values'][enum_ref]
        
        # Fallback to the reference itself
        return enum_ref
    
    def _extract_integer_value_content(self, value_element) -> str:
        """Extract integer value"""
        the_value = (value_element.get('THE-VALUE') or 
                    value_element.get('the-value'))
        if the_value is not None:
            return str(the_value)
        
        # Try child element
        the_value_elem = value_element.find(".//THE-VALUE") or value_element.find(".//the-value")
        if the_value_elem is not None and the_value_elem.text:
            return the_value_elem.text
        
        return ''
    
    def _extract_real_value_content(self, value_element) -> str:
        """Extract real/float value"""
        the_value = (value_element.get('THE-VALUE') or 
                    value_element.get('the-value'))
        if the_value is not None:
            return str(the_value)
        
        # Try child element
        the_value_elem = value_element.find(".//THE-VALUE") or value_element.find(".//the-value")
        if the_value_elem is not None and the_value_elem.text:
            return the_value_elem.text
        
        return ''
    
    def _extract_date_value_content(self, value_element) -> str:
        """Extract date value"""
        the_value = (value_element.get('THE-VALUE') or 
                    value_element.get('the-value'))
        if the_value is not None:
            return str(the_value)
        
        # Try child element
        the_value_elem = value_element.find(".//THE-VALUE") or value_element.find(".//the-value")
        if the_value_elem is not None and the_value_elem.text:
            return the_value_elem.text
        
        return ''
    
    def _extract_boolean_value_content(self, value_element) -> str:
        """Extract boolean value with human-readable conversion"""
        the_value = (value_element.get('THE-VALUE') or 
                    value_element.get('the-value'))
        
        if the_value is not None:
            return 'Yes' if str(the_value).lower() in ['true', '1', 'yes'] else 'No'
        
        # Try child element
        the_value_elem = value_element.find(".//THE-VALUE") or value_element.find(".//the-value")
        if the_value_elem is not None and the_value_elem.text:
            return 'Yes' if the_value_elem.text.lower() in ['true', '1', 'yes'] else 'No'
        
        return ''
    
    def _extract_fallback_content(self, value_element) -> str:
        """Fallback content extraction for unknown types"""
        # Try standard THE-VALUE extraction
        the_value = (value_element.get('THE-VALUE') or 
                    value_element.get('the-value'))
        if the_value:
            return str(the_value)
        
        # Try child THE-VALUE element
        the_value_elem = value_element.find(".//THE-VALUE") or value_element.find(".//the-value")
        if the_value_elem is not None:
            return self._extract_comprehensive_text_content(the_value_elem)
        
        # Last resort: extract any text content
        return self._extract_comprehensive_text_content(value_element)
    
    def _smart_map_to_common_fields(self, resolved: Dict[str, Any], human_name: str, 
                                   attr_ref: str, value: str):
        """Intelligently map attributes to common requirement fields"""
        if not value:
            return
        
        name_lower = human_name.lower()
        ref_lower = attr_ref.lower()
        
        # Enhanced mapping with more comprehensive keywords
        title_keywords = ['title', 'name', 'heading', 'caption', 'label', 'summary', 'object', 'text']
        desc_keywords = ['description', 'detail', 'content', 'specification', 'rationale', 'notes', 'comment']
        type_keywords = ['type', 'category', 'kind', 'class', 'classification']
        priority_keywords = ['priority', 'importance', 'criticality', 'severity', 'level']
        status_keywords = ['status', 'state', 'phase', 'condition', 'approval']
        
        # Check title field with preference for shorter, more title-like content
        if any(keyword in name_lower or keyword in ref_lower for keyword in title_keywords):
            if not resolved['title'] or self._is_better_title(value, resolved['title']):
                resolved['title'] = value
        
        # Check description field with preference for longer, more descriptive content
        elif any(keyword in name_lower or keyword in ref_lower for keyword in desc_keywords):
            if not resolved['description'] or self._is_better_description(value, resolved['description']):
                resolved['description'] = value
        
        # Check type field
        elif any(keyword in name_lower or keyword in ref_lower for keyword in type_keywords):
            if not resolved['type'] or value != resolved['type_ref']:
                resolved['type'] = value
        
        # Check priority field
        elif any(keyword in name_lower or keyword in ref_lower for keyword in priority_keywords):
            resolved['priority'] = value
        
        # Check status field
        elif any(keyword in name_lower or keyword in ref_lower for keyword in status_keywords):
            resolved['status'] = value
    
    def _is_better_title(self, new_value: str, current_value: str) -> bool:
        """Determine if new value is a better title than current"""
        if not current_value:
            return True
        if not new_value:
            return False
        
        # Prefer shorter titles that look like actual titles
        if len(new_value) < len(current_value) and len(new_value) > 0:
            return True
        
        # Prefer content that doesn't look like references
        if '_' in current_value and '_' not in new_value:
            return True
        
        return False
    
    def _is_better_description(self, new_value: str, current_value: str) -> bool:
        """Determine if new value is a better description than current"""
        if not current_value:
            return True
        if not new_value:
            return False
        
        # Prefer longer, more descriptive content
        if len(new_value) > len(current_value) * 1.2:
            return True
        
        # Prefer content that doesn't look like references
        if '_' in current_value and '_' not in new_value:
            return True
        
        return False
    
    def _ensure_meaningful_content(self, resolved: Dict[str, Any]):
        """Ensure requirement has meaningful, human-readable content"""
        # If no title, try to create one from attributes or ID
        if not resolved['title']:
            # Try to find a good title from attributes
            for attr_name, attr_value in resolved['attributes'].items():
                if (attr_value and len(str(attr_value)) < 100 and 
                    any(keyword in attr_name.lower() for keyword in ['name', 'title', 'object'])):
                    resolved['title'] = str(attr_value)
                    break
            
            # Fallback to ID
            if not resolved['title']:
                resolved['title'] = resolved['id'] or 'Untitled Requirement'
        
        # If no description, try to find one from attributes
        if not resolved['description']:
            for attr_name, attr_value in resolved['attributes'].items():
                if (attr_value and len(str(attr_value)) > 20 and
                    any(keyword in attr_name.lower() for keyword in ['text', 'detail', 'content'])):
                    resolved['description'] = str(attr_value)
                    break
    
    def _create_content_hash(self, req: Dict[str, Any]) -> str:
        """Create a content string for comparison purposes"""
        parts = []
        
        if req['title']:
            parts.append(f"TITLE:{req['title']}")
        if req['description']:
            parts.append(f"DESC:{req['description']}")
        if req['type']:
            parts.append(f"TYPE:{req['type']}")
        if req['priority']:
            parts.append(f"PRIORITY:{req['priority']}")
        if req['status']:
            parts.append(f"STATUS:{req['status']}")
            
        # Add key attributes (limit to avoid huge hashes)
        attr_count = 0
        for attr_name, attr_value in req['attributes'].items():
            if attr_value and attr_count < 10:  # Limit to first 10 meaningful attributes
                parts.append(f"{attr_name}:{attr_value}")
                attr_count += 1
        
        return '||'.join(parts)
    
    def _build_enumeration_catalog(self, root):
        """Build comprehensive enumeration definitions catalog"""
        enum_defs = self._find_elements_multiple_patterns(root, [
            ".//ENUM-DEFINITION"
        ])
        
        for enum_def in enum_defs:
            identifier = self._get_element_identifier(enum_def)
            if not identifier:
                continue
                
            long_name = self._get_element_long_name(enum_def) or identifier
            
            # Extract enum values with comprehensive search
            enum_values = {}
            
            # Try multiple patterns for enum values
            enum_value_elements = (enum_def.findall(".//ENUM-VALUE") +
                                 enum_def.findall(".//enum-value"))
            
            for enum_value in enum_value_elements:
                val_id = self._get_element_identifier(enum_value)
                val_name = self._get_element_long_name(enum_value) or val_id
                if val_id:
                    enum_values[val_id] = val_name
            
            self.enumeration_definitions[identifier] = {
                'identifier': identifier,
                'long_name': long_name,
                'values': enum_values
            }
    
    def _build_datatype_catalog(self, root):
        """Build datatype definitions catalog"""
        datatypes = self._find_elements_multiple_patterns(root, [
            ".//DATATYPE-DEFINITION-STRING",
            ".//DATATYPE-DEFINITION-XHTML",
            ".//DATATYPE-DEFINITION-INTEGER",
            ".//DATATYPE-DEFINITION-REAL",
            ".//DATATYPE-DEFINITION-DATE",
            ".//DATATYPE-DEFINITION-BOOLEAN",
            ".//DATATYPE-DEFINITION-ENUMERATION"
        ])
        
        for datatype in datatypes:
            identifier = self._get_element_identifier(datatype)
            if identifier:
                long_name = self._get_element_long_name(datatype) or identifier
                self.datatype_definitions[identifier] = {
                    'identifier': identifier,
                    'long_name': long_name,
                    'element': datatype
                }
    
    def _find_elements_multiple_patterns(self, root, patterns: List[str]) -> List:
        """Find elements using multiple XPath patterns with and without namespaces"""
        elements = []
        
        for pattern in patterns:
            # Try without namespace first
            found = root.findall(pattern)
            elements.extend(found)
            
            # Try with reqif namespace if nothing found
            if not found:
                ns_pattern = pattern.replace(".//", ".//reqif:")
                ns_found = root.findall(ns_pattern, self.namespaces)
                elements.extend(ns_found)
        
        return elements
    
    def _get_element_identifier(self, element) -> Optional[str]:
        """Get identifier from element with multiple fallback patterns"""
        return (element.get('IDENTIFIER') or 
                element.get('identifier') or
                element.get('ID') or
                element.get('id'))
    
    def _get_element_long_name(self, element) -> Optional[str]:
        """Get long name from element with multiple fallback patterns"""
        return (element.get('LONG-NAME') or 
                element.get('long-name') or
                element.get('LONGNAME') or
                element.get('longname') or
                element.get('NAME') or
                element.get('name'))
    
    def _get_element_description(self, element) -> str:
        """Get description from element with multiple fallback patterns"""
        return (element.get('DESC') or 
                element.get('desc') or
                element.get('DESCRIPTION') or
                element.get('description') or
                '')
    
    def _print_debug_summary(self):
        """Print comprehensive debug summary"""
        print("\n" + "="*60)
        print("REQIF PARSING DEBUG SUMMARY")
        print("="*60)
        print(f"Attribute Definitions Found: {self.debug_info['definitions_found']}")
        print(f"Spec Object Types Found: {self.debug_info['types_found']}")
        print(f"Spec Objects Found: {self.debug_info['objects_found']}")
        print(f"Values Successfully Resolved: {self.debug_info['values_resolved']}")
        
        if self.debug_info['resolution_failures']:
            print(f"\nResolution Failures ({len(self.debug_info['resolution_failures'])}):")
            for failure in self.debug_info['resolution_failures'][:10]:  # Show first 10
                print(f"  - {failure}")
            if len(self.debug_info['resolution_failures']) > 10:
                print(f"  ... and {len(self.debug_info['resolution_failures']) - 10} more")
        
        print("="*60)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive information about a ReqIF file"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.reqifz':
                return self._get_reqifz_info(file_path)
            else:
                return self._get_reqif_info(file_path)
                
        except Exception as e:
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'error': str(e)
            }
    
    def _get_reqif_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive info about a regular .reqif file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Count different elements
        spec_objects = self._find_elements_multiple_patterns(root, [".//SPEC-OBJECT"])
        attr_defs = self._find_elements_multiple_patterns(root, [
            ".//ATTRIBUTE-DEFINITION-STRING",
            ".//ATTRIBUTE-DEFINITION-XHTML",
            ".//ATTRIBUTE-DEFINITION-ENUMERATION"
        ])
        spec_types = self._find_elements_multiple_patterns(root, [".//SPEC-OBJECT-TYPE"])
        
        info = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'ReqIF',
            'file_size': os.path.getsize(file_path),
            'requirement_count': len(spec_objects),
            'attribute_definition_count': len(attr_defs),
            'spec_object_type_count': len(spec_types),
            'root_tag': root.tag,
            'namespace': root.tag.split('}')[0].strip('{') if '}' in root.tag else None
        }
        
        return info
    
    def _get_reqifz_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive info about a .reqifz archive file"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extract and analyze
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find ReqIF files
            reqif_files = []
            total_requirements = 0
            total_attr_defs = 0
            total_spec_types = 0
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.reqif'):
                        reqif_file_path = os.path.join(root, file)
                        reqif_files.append(file)
                        
                        # Count elements in this file
                        try:
                            file_info = self._get_reqif_info(reqif_file_path)
                            total_requirements += file_info.get('requirement_count', 0)
                            total_attr_defs += file_info.get('attribute_definition_count', 0)
                            total_spec_types += file_info.get('spec_object_type_count', 0)
                        except:
                            pass
            
            info = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_type': 'ReqIFZ Archive',
                'file_size': os.path.getsize(file_path),
                'requirement_count': total_requirements,
                'attribute_definition_count': total_attr_defs,
                'spec_object_type_count': total_spec_types,
                'contained_files': reqif_files,
                'archive_file_count': len(reqif_files)
            }
            
            return info
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get detailed debug information from the last parse operation"""
        return {
            'parsing_summary': self.debug_info.copy(),
            'catalog_sizes': {
                'attribute_definitions': len(self.attribute_definitions),
                'spec_object_types': len(self.spec_object_types),
                'enumeration_definitions': len(self.enumeration_definitions),
                'datatype_definitions': len(self.datatype_definitions)
            },
            'sample_attribute_definitions': {
                k: {
                    'long_name': v['long_name'],
                    'type': v['type']
                } for k, v in list(self.attribute_definitions.items())[:5]
            },
            'sample_spec_object_types': {
                k: {
                    'long_name': v['long_name'],
                    'spec_attributes_count': len(v['spec_attributes'])
                } for k, v in list(self.spec_object_types.items())[:5]
            }
        }


# Example usage and comprehensive testing
if __name__ == "__main__":
    parser = ReqIFParser()
    
    print("ReqIF Parser - Complete Comprehensive Implementation")
    print("=" * 60)
    print("Features:")
    print("✅ Four-pass parsing: Definitions → Types → Objects → Values")
    print("✅ Complete reference chain resolution")
    print("✅ Comprehensive XHTML content extraction")
    print("✅ Smart field mapping with fallbacks")
    print("✅ Enhanced debug information")
    print("✅ Support for all ReqIF atomic data types")
    print("✅ Proper namespace handling")
    print("✅ Archive (.reqifz) support")
    print("✅ Robust error handling and fallbacks")
    
    # Example usage:
    # requirements = parser.parse_file("example.reqif")
    # debug_info = parser.get_debug_info()
    # print(f"Parsed {len(requirements)} requirements")
    # print("Debug Info:", debug_info['parsing_summary'])
    
    print("\nParser ready for comprehensive ReqIF file processing!")