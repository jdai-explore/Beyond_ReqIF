#!/usr/bin/env python3
"""
ReqIF Parser Module
Handles parsing of ReqIF XML files and extracting requirement information.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import os


class ReqIFParser:
    """Parser for ReqIF (Requirements Interchange Format) files"""
    
    def __init__(self):
        self.namespaces = {
            'reqif': 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
        
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a ReqIF file and extract requirements
        
        Args:
            file_path: Path to the ReqIF file
            
        Returns:
            List of requirement dictionaries
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ReqIF file not found: {file_path}")
            
        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Register namespaces for XPath queries
            for prefix, uri in self.namespaces.items():
                ET.register_namespace(prefix, uri)
            
            # Extract requirements
            requirements = self._extract_requirements(root)
            
            return requirements
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in ReqIF file: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error parsing ReqIF file: {str(e)}")
    
    def _extract_requirements(self, root) -> List[Dict[str, Any]]:
        """Extract requirement specifications from ReqIF XML"""
        requirements = []
        
        # Find all SPEC-OBJECT elements (requirements)
        spec_objects = root.findall(".//SPEC-OBJECT")
        
        if not spec_objects:
            # Try with namespace
            spec_objects = root.findall(".//reqif:SPEC-OBJECT", self.namespaces)
        
        for spec_obj in spec_objects:
            req = self._parse_spec_object(spec_obj)
            if req:
                requirements.append(req)
        
        # If no SPEC-OBJECT found, try alternative structure
        if not requirements:
            requirements = self._extract_alternative_structure(root)
            
        return requirements
    
    def _parse_spec_object(self, spec_obj) -> Dict[str, Any]:
        """Parse a single SPEC-OBJECT (requirement)"""
        req = {
            'id': '',
            'identifier': '',
            'title': '',
            'description': '',
            'type': '',
            'attributes': {},
            'content': ''  # Combined content for comparison
        }
        
        # Get identifier
        identifier = spec_obj.get('IDENTIFIER') or spec_obj.get('identifier')
        if identifier:
            req['id'] = identifier
            req['identifier'] = identifier
        
        # Get type reference
        type_ref = spec_obj.find(".//TYPE") or spec_obj.find(".//type")
        if type_ref is not None:
            type_ref_attr = type_ref.get('SPEC-OBJECT-TYPE-REF') or type_ref.get('spec-object-type-ref')
            if type_ref_attr:
                req['type'] = type_ref_attr
        
        # Parse attribute values
        values = spec_obj.findall(".//ATTRIBUTE-VALUE-STRING") + \
                spec_obj.findall(".//ATTRIBUTE-VALUE-XHTML") + \
                spec_obj.findall(".//ATTRIBUTE-VALUE-ENUMERATION")
        
        # Try without namespace if nothing found
        if not values:
            values = spec_obj.findall(".//reqif:ATTRIBUTE-VALUE-STRING", self.namespaces) + \
                    spec_obj.findall(".//reqif:ATTRIBUTE-VALUE-XHTML", self.namespaces) + \
                    spec_obj.findall(".//reqif:ATTRIBUTE-VALUE-ENUMERATION", self.namespaces)
        
        for value in values:
            attr_def_ref = value.get('ATTRIBUTE-DEFINITION-REF') or value.get('attribute-definition-ref')
            
            if not attr_def_ref:
                continue
                
            # Extract value based on type
            attr_value = self._extract_attribute_value(value)
            
            # Store in attributes
            req['attributes'][attr_def_ref] = attr_value
            
            # Map common attribute names
            attr_name_lower = attr_def_ref.lower()
            if 'title' in attr_name_lower or 'name' in attr_name_lower:
                req['title'] = attr_value
            elif 'description' in attr_name_lower or 'text' in attr_name_lower or 'content' in attr_name_lower:
                req['description'] = attr_value
        
        # Create combined content for comparison
        req['content'] = self._create_content_hash(req)
        
        # Use ID as title if no title found
        if not req['title'] and req['id']:
            req['title'] = req['id']
            
        return req
    
    def _extract_attribute_value(self, value_elem):
        """Extract the actual value from an attribute value element"""
        # For STRING attributes
        if value_elem.tag.endswith('ATTRIBUTE-VALUE-STRING'):
            the_value = value_elem.get('THE-VALUE') or value_elem.get('the-value')
            return the_value or ''
        
        # For XHTML attributes
        elif value_elem.tag.endswith('ATTRIBUTE-VALUE-XHTML'):
            xhtml_elem = value_elem.find(".//THE-VALUE") or value_elem.find(".//the-value")
            if xhtml_elem is not None:
                # Extract text content from XHTML
                return self._extract_xhtml_text(xhtml_elem)
            return ''
        
        # For ENUMERATION attributes
        elif value_elem.tag.endswith('ATTRIBUTE-VALUE-ENUMERATION'):
            enum_values = value_elem.findall(".//ENUM-VALUE-REF") or value_elem.findall(".//enum-value-ref")
            if enum_values:
                return ', '.join([ev.get('REF') or ev.get('ref') or '' for ev in enum_values])
            return ''
        
        return ''
    
    def _extract_xhtml_text(self, xhtml_elem):
        """Extract plain text from XHTML content"""
        # Simple text extraction - can be enhanced for better formatting
        text_parts = []
        
        if xhtml_elem.text:
            text_parts.append(xhtml_elem.text.strip())
            
        for child in xhtml_elem:
            if child.text:
                text_parts.append(child.text.strip())
            if child.tail:
                text_parts.append(child.tail.strip())
        
        return ' '.join(filter(None, text_parts))
    
    def _create_content_hash(self, req: Dict[str, Any]) -> str:
        """Create a content string for comparison purposes"""
        parts = []
        
        if req['title']:
            parts.append(f"TITLE:{req['title']}")
        if req['description']:
            parts.append(f"DESC:{req['description']}")
        if req['type']:
            parts.append(f"TYPE:{req['type']}")
            
        # Add key attributes
        for attr_name, attr_value in req['attributes'].items():
            if attr_value:
                parts.append(f"{attr_name}:{attr_value}")
        
        return '||'.join(parts)
    
    def _extract_alternative_structure(self, root) -> List[Dict[str, Any]]:
        """Try alternative ReqIF structures if standard parsing fails"""
        requirements = []
        
        # Look for any elements that might contain requirements
        # This is a fallback for non-standard ReqIF files
        potential_reqs = root.findall(".//*[@IDENTIFIER]") + root.findall(".//*[@identifier]")
        
        for elem in potential_reqs:
            identifier = elem.get('IDENTIFIER') or elem.get('identifier')
            if identifier:
                req = {
                    'id': identifier,
                    'identifier': identifier,
                    'title': identifier,  # Use ID as title
                    'description': elem.text or '',
                    'type': elem.tag,
                    'attributes': dict(elem.attrib),
                    'content': f"ID:{identifier}||TYPE:{elem.tag}||TEXT:{elem.text or ''}"
                }
                requirements.append(req)
        
        return requirements
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic information about a ReqIF file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Count requirements
            spec_objects = root.findall(".//SPEC-OBJECT")
            if not spec_objects:
                spec_objects = root.findall(".//reqif:SPEC-OBJECT", self.namespaces)
            
            info = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'requirement_count': len(spec_objects),
                'root_tag': root.tag,
                'namespace': root.tag.split('}')[0].strip('{') if '}' in root.tag else None
            }
            
            return info
            
        except Exception as e:
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'error': str(e)
            }


# Example usage and testing
if __name__ == "__main__":
    parser = ReqIFParser()
    
    # Example: parse a file (uncomment to test with actual file)
    # requirements = parser.parse_file("example.reqif")
    # print(f"Found {len(requirements)} requirements")
    # for req in requirements[:3]:  # Print first 3
    #     print(f"ID: {req['id']}, Title: {req['title']}")
    
    print("ReqIF Parser module loaded successfully.")