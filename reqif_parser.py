import zipfile
import xml.etree.ElementTree as etree
from lxml import etree
HAS_LXML = True

class ReqIFParser:
    """Parser for ReqIF files"""
    
    def __init__(self):
        self.namespaces = {
            'reqif': 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
    
    def parse_reqif_file(self, file_path):
        """Parse a ReqIF file and extract requirements"""
        try:
            if file_path.endswith('.reqifz'):
                return self._parse_reqifz(file_path)
            else:
                return self._parse_reqif(file_path)
        except Exception as e:
            raise Exception(f"Error parsing ReqIF file {file_path}: {str(e)}")
    
    def _parse_reqifz(self, file_path):
        """Parse a zipped ReqIF file"""
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # Find the .reqif file inside the zip
            reqif_files = [f for f in zip_file.namelist() if f.endswith('.reqif')]
            if not reqif_files:
                raise Exception("No .reqif file found in the archive")
            
            # Extract and parse the first .reqif file
            with zip_file.open(reqif_files[0]) as reqif_file:
                return self._parse_xml_content(reqif_file.read())
    
    def _parse_reqif(self, file_path):
        """Parse a regular ReqIF file"""
        with open(file_path, 'rb') as f:
            return self._parse_xml_content(f.read())
    
    def _parse_xml_content(self, xml_content):
        """Parse XML content and extract requirements"""
        try:
            if HAS_LXML:
                root = etree.fromstring(xml_content)
            else:
                root = etree.fromstring(xml_content)
        except:
            # Fallback for malformed XML
            if HAS_LXML:
                root = etree.fromstring(xml_content, parser=etree.XMLParser(recover=True))
            else:
                # Standard library doesn't have recover option
                root = etree.fromstring(xml_content)
        
        requirements = {}
        
        # Find requirements using appropriate method based on available library
        if HAS_LXML:
            # Use XPath with lxml
            spec_objects = root.xpath('.//SPEC-OBJECT', namespaces=self.namespaces)
            if not spec_objects:
                # Fallback: look for elements with IDENTIFIER attribute
                spec_objects = root.xpath('.//*[@IDENTIFIER]')
        else:
            # Use manual traversal with standard library
            spec_objects = self._find_elements_by_tag(root, 'SPEC-OBJECT')
            if not spec_objects:
                # Fallback: look for elements with IDENTIFIER attribute
                spec_objects = self._find_elements_with_attribute(root, 'IDENTIFIER')
        
        for spec_obj in spec_objects:
            req_id = spec_obj.get('IDENTIFIER', '')
            if not req_id:
                continue
                
            # Extract requirement text and attributes
            req_data = {
                'id': req_id,
                'text': self._extract_text_content(spec_obj),
                'attributes': self._extract_attributes(spec_obj)
            }
            
            requirements[req_id] = req_data
        
        return requirements
    
    def _find_elements_by_tag(self, root, tag_name):
        """Find elements by tag name using standard library"""
        elements = []
        for elem in root.iter():
            if elem.tag and elem.tag.endswith(tag_name):
                elements.append(elem)
        return elements
    
    def _find_elements_with_attribute(self, root, attr_name):
        """Find elements with specific attribute using standard library"""
        elements = []
        for elem in root.iter():
            if elem.get(attr_name):
                elements.append(elem)
        return elements
    
    def _extract_text_content(self, element):
        """Extract text content from XML element"""
        text_parts = []
        
        if HAS_LXML:
            # Use XPath with lxml
            attr_values = element.xpath('.//ATTRIBUTE-VALUE-STRING | .//ATTRIBUTE-VALUE-XHTML', 
                                      namespaces=self.namespaces)
            
            for attr_val in attr_values:
                # Try to get the value
                value_elem = attr_val.find('.//THE-VALUE', self.namespaces)
                if value_elem is not None:
                    if value_elem.text:
                        text_parts.append(value_elem.text.strip())
                    # Also check for XHTML content
                    xhtml_content = value_elem.xpath('.//xhtml:*', namespaces=self.namespaces)
                    for xhtml_elem in xhtml_content:
                        if xhtml_elem.text:
                            text_parts.append(xhtml_elem.text.strip())
        else:
            # Use manual traversal with standard library
            for elem in element.iter():
                if (elem.tag and 
                    ('ATTRIBUTE-VALUE-STRING' in elem.tag or 'ATTRIBUTE-VALUE-XHTML' in elem.tag)):
                    # Look for THE-VALUE elements
                    for child in elem.iter():
                        if child.tag and 'THE-VALUE' in child.tag and child.text:
                            text_parts.append(child.text.strip())
        
        # Fallback: get all text content
        if not text_parts:
            text_parts = [element.text or '']
            for child in element.iter():
                if child.text:
                    text_parts.append(child.text.strip())
        
        return ' '.join(filter(None, text_parts))
    
    def _extract_attributes(self, element):
        """Extract attributes from XML element"""
        attributes = {}
        
        # Get XML attributes
        for key, value in element.attrib.items():
            if key != 'IDENTIFIER':
                attributes[key] = value
        
        # Get child element attributes
        for child in element:
            if child.tag and child.text:
                attributes[child.tag] = child.text.strip()
        
        return attributes
