"""
ReqIF Parser Module
==================

This module provides comprehensive parsing capabilities for ReqIF files.
Supports both .reqif and .reqifz formats with robust error handling
and namespace management.

Classes:
    ReqIFParser: Main parser class for ReqIF files
    ParsingError: Custom exception for parsing errors
    
Functions:
    validate_reqif_file: Validate ReqIF file format
    extract_metadata: Extract file metadata
"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging

# XML parsing with fallback support
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    import xml.etree.ElementTree as etree
    HAS_LXML = False

# Import project modules
from models.requirement import Requirement
from models.file_info import FileInfo
from utils.logger import get_logger

logger = get_logger(__name__)


class ParsingError(Exception):
    """Custom exception for ReqIF parsing errors"""
    
    def __init__(self, message: str, file_path: str = None, line_number: int = None):
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(self.message)
    
    def __str__(self):
        error_msg = self.message
        if self.file_path:
            error_msg += f" (File: {self.file_path}"
            if self.line_number:
                error_msg += f", Line: {self.line_number}"
            error_msg += ")"
        return error_msg


@dataclass
class ParseResult:
    """Result of parsing operation"""
    requirements: Dict[str, Requirement]
    file_info: FileInfo
    metadata: Dict[str, Any]
    parsing_stats: Dict[str, int]
    warnings: List[str]
    errors: List[str]


class ReqIFParser:
    """
    ReqIF File Parser
    
    Provides comprehensive parsing of ReqIF files with support for:
    - .reqif files (XML format)
    - .reqifz files (compressed archives)
    - Namespace handling
    - Error recovery
    - Metadata extraction
    """
    
    def __init__(self):
        """Initialize the ReqIF parser"""
        self.namespaces = {
            'reqif': 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd',
            'xhtml': 'http://www.w3.org/1999/xhtml',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        self.temp_files = []  # Track temporary files for cleanup
        logger.info("ReqIF Parser initialized (lxml support: %s)", HAS_LXML)
    
    def parse_file(self, file_path: Union[str, Path]) -> ParseResult:
        """
        Parse a ReqIF file and return structured data
        
        Args:
            file_path: Path to the ReqIF file (.reqif or .reqifz)
            
        Returns:
            ParseResult containing requirements and metadata
            
        Raises:
            ParsingError: If parsing fails
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"ReqIF file not found: {file_path}")
        
        logger.info("Starting parse of file: %s", file_path)
        
        try:
            # Determine file type and parse accordingly
            if file_path.suffix.lower() == '.reqifz':
                return self._parse_reqifz(file_path)
            elif file_path.suffix.lower() == '.reqif':
                return self._parse_reqif(file_path)
            else:
                raise ParsingError(f"Unsupported file format: {file_path.suffix}")
                
        except ParsingError:
            raise
        except Exception as e:
            logger.error("Unexpected error parsing file %s: %s", file_path, str(e))
            raise ParsingError(f"Failed to parse ReqIF file: {str(e)}", str(file_path))
    
    def _parse_reqifz(self, file_path: Path) -> ParseResult:
        """Parse a compressed ReqIF archive"""
        logger.debug("Parsing ReqIFZ file: %s", file_path)
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Find .reqif files in the archive
                reqif_files = [f for f in zip_file.namelist() if f.endswith('.reqif')]
                
                if not reqif_files:
                    raise ParsingError("No .reqif files found in archive", str(file_path))
                
                if len(reqif_files) > 1:
                    logger.warning("Multiple .reqif files found, using first: %s", reqif_files[0])
                
                # Extract and parse the ReqIF file
                reqif_filename = reqif_files[0]
                with zip_file.open(reqif_filename) as reqif_file:
                    xml_content = reqif_file.read()
                    
                return self._parse_xml_content(xml_content, file_path, reqif_filename)
                
        except zipfile.BadZipFile as e:
            raise ParsingError(f"Invalid ZIP archive: {str(e)}", str(file_path))
        except Exception as e:
            raise ParsingError(f"Error reading ReqIFZ file: {str(e)}", str(file_path))
    
    def _parse_reqif(self, file_path: Path) -> ParseResult:
        """Parse a standard ReqIF file"""
        logger.debug("Parsing ReqIF file: %s", file_path)
        
        try:
            with open(file_path, 'rb') as f:
                xml_content = f.read()
            return self._parse_xml_content(xml_content, file_path)
            
        except (IOError, OSError) as e:
            raise ParsingError(f"Error reading file: {str(e)}", str(file_path))
    
    def _parse_xml_content(self, xml_content: bytes, file_path: Path, 
                          internal_filename: str = None) -> ParseResult:
        """Parse XML content and extract requirements"""
        logger.debug("Parsing XML content (%d bytes)", len(xml_content))
        
        # Initialize result containers
        requirements = {}
        warnings = []
        errors = []
        parsing_stats = {
            'total_elements': 0,
            'spec_objects': 0,
            'spec_relations': 0,
            'spec_types': 0,
            'attributes': 0
        }
        
        try:
            # Parse XML with error recovery
            root = self._parse_xml_with_recovery(xml_content, file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(root)
            
            # Update namespaces from document
            self._update_namespaces(root)
            
            # Find and parse requirements
            spec_objects = self._find_spec_objects(root)
            parsing_stats['spec_objects'] = len(spec_objects)
            
            for spec_obj in spec_objects:
                try:
                    requirement = self._parse_spec_object(spec_obj)
                    if requirement and requirement.id:
                        requirements[requirement.id] = requirement
                        parsing_stats['attributes'] += len(requirement.attributes)
                    else:
                        warnings.append(f"Skipped spec object without valid ID")
                except Exception as e:
                    error_msg = f"Error parsing spec object: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            
            # Create file info
            file_info = FileInfo(
                path=str(file_path),
                name=file_path.name,
                size=len(xml_content),
                format='reqifz' if file_path.suffix.lower() == '.reqifz' else 'reqif',
                internal_filename=internal_filename
            )
            
            # Count total elements for statistics
            parsing_stats['total_elements'] = len(list(root.iter()))
            
            logger.info("Successfully parsed %d requirements from %s", 
                       len(requirements), file_path)
            
            return ParseResult(
                requirements=requirements,
                file_info=file_info,
                metadata=metadata,
                parsing_stats=parsing_stats,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            logger.error("XML parsing failed for %s: %s", file_path, str(e))
            raise ParsingError(f"XML parsing failed: {str(e)}", str(file_path))
    
    def _parse_xml_with_recovery(self, xml_content: bytes, file_path: Path):
        """Parse XML with error recovery options"""
        try:
            if HAS_LXML:
                # Try with lxml first (more robust)
                try:
                    return etree.fromstring(xml_content)
                except etree.XMLSyntaxError:
                    # Try with recovery parser
                    parser = etree.XMLParser(recover=True)
                    return etree.fromstring(xml_content, parser)
            else:
                # Use standard library parser
                return etree.fromstring(xml_content)
                
        except Exception as e:
            raise ParsingError(f"Invalid XML content: {str(e)}", str(file_path))
    
    def _update_namespaces(self, root):
        """Update namespaces from document"""
        try:
            # Extract namespaces from root element
            for prefix, uri in root.nsmap.items() if hasattr(root, 'nsmap') else {}:
                if prefix:  # Skip default namespace
                    self.namespaces[prefix] = uri
        except AttributeError:
            # Standard library doesn't have nsmap
            pass
    
    def _extract_metadata(self, root) -> Dict[str, Any]:
        """Extract metadata from ReqIF document"""
        metadata = {}
        
        try:
            # Extract header information
            header = self._find_element(root, './/REQ-IF-HEADER')
            if header is not None:
                metadata.update(self._extract_header_info(header))
            
            # Extract tool extensions
            tool_extensions = self._find_elements(root, './/REQ-IF-TOOL-EXTENSION')
            if tool_extensions:
                metadata['tool_extensions'] = [
                    self._extract_tool_extension_info(ext) for ext in tool_extensions
                ]
            
            # Extract creation info
            creation_time = self._find_element(root, './/CREATION-TIME')
            if creation_time is not None and creation_time.text:
                metadata['creation_time'] = creation_time.text
            
            # Extract source tool info
            source_tool = self._find_element(root, './/SOURCE-TOOL-ID')
            if source_tool is not None and source_tool.text:
                metadata['source_tool'] = source_tool.text
                
        except Exception as e:
            logger.warning("Error extracting metadata: %s", str(e))
        
        return metadata
    
    def _extract_header_info(self, header) -> Dict[str, Any]:
        """Extract information from REQ-IF-HEADER"""
        info = {}
        
        # Simple text fields
        text_fields = [
            'COMMENT', 'CREATION-TIME', 'IDENTIFIER', 'REPOSITORY-ID',
            'REQ-IF-TOOL-ID', 'REQ-IF-VERSION', 'SOURCE-TOOL-ID', 'TITLE'
        ]
        
        for field in text_fields:
            element = self._find_element(header, f'.//{field}')
            if element is not None and element.text:
                info[field.lower().replace('-', '_')] = element.text.strip()
        
        return info
    
    def _extract_tool_extension_info(self, extension) -> Dict[str, Any]:
        """Extract tool extension information"""
        info = {}
        
        # Get attributes
        for attr_name, attr_value in extension.attrib.items():
            info[attr_name] = attr_value
        
        # Get text content
        if extension.text:
            info['content'] = extension.text.strip()
        
        return info
    
    def _find_spec_objects(self, root) -> List:
        """Find all SPEC-OBJECT elements in the document"""
        if HAS_LXML:
            # Use XPath with lxml
            return root.xpath('.//SPEC-OBJECT', namespaces=self.namespaces)
        else:
            # Manual search with standard library
            return self._find_elements_by_tag(root, 'SPEC-OBJECT')
    
    def _find_elements_by_tag(self, root, tag_name: str) -> List:
        """Find elements by tag name using standard library"""
        elements = []
        for elem in root.iter():
            if elem.tag and (elem.tag.endswith(tag_name) or elem.tag == tag_name):
                elements.append(elem)
        return elements
    
    def _find_element(self, parent, xpath: str):
        """Find single element with namespace support"""
        if HAS_LXML:
            result = parent.xpath(xpath, namespaces=self.namespaces)
            return result[0] if result else None
        else:
            # Simple search for standard library
            tag = xpath.split('//')[-1]
            for elem in parent.iter():
                if elem.tag and elem.tag.endswith(tag):
                    return elem
            return None
    
    def _find_elements(self, parent, xpath: str) -> List:
        """Find multiple elements with namespace support"""
        if HAS_LXML:
            return parent.xpath(xpath, namespaces=self.namespaces)
        else:
            # Simple search for standard library
            tag = xpath.split('//')[-1]
            elements = []
            for elem in parent.iter():
                if elem.tag and elem.tag.endswith(tag):
                    elements.append(elem)
            return elements
    
    def _parse_spec_object(self, spec_obj) -> Optional[Requirement]:
        """Parse a SPEC-OBJECT element into a Requirement"""
        try:
            # Get identifier
            req_id = spec_obj.get('IDENTIFIER', spec_obj.get('identifier', ''))
            if not req_id:
                return None
            
            # Extract requirement text and attributes
            requirement = Requirement(
                id=req_id,
                text=self._extract_text_content(spec_obj),
                attributes=self._extract_attributes(spec_obj)
            )
            
            # Extract additional metadata
            requirement.last_change = spec_obj.get('LAST-CHANGE')
            requirement.long_name = spec_obj.get('LONG-NAME')
            
            return requirement
            
        except Exception as e:
            logger.warning("Error parsing spec object %s: %s", 
                          spec_obj.get('IDENTIFIER', 'unknown'), str(e))
            return None
    
    def _extract_text_content(self, element) -> str:
        """Extract text content from XML element"""
        text_parts = []
        
        if HAS_LXML:
            # Use XPath with lxml for more precise extraction
            attr_values = element.xpath(
                './/ATTRIBUTE-VALUE-STRING | .//ATTRIBUTE-VALUE-XHTML',
                namespaces=self.namespaces
            )
            
            for attr_val in attr_values:
                value_elem = attr_val.find('.//THE-VALUE', self.namespaces)
                if value_elem is not None:
                    if value_elem.text:
                        text_parts.append(value_elem.text.strip())
                    
                    # Check for XHTML content
                    xhtml_content = value_elem.xpath('.//xhtml:*', namespaces=self.namespaces)
                    for xhtml_elem in xhtml_content:
                        if xhtml_elem.text:
                            text_parts.append(xhtml_elem.text.strip())
        else:
            # Manual traversal with standard library
            for elem in element.iter():
                if (elem.tag and 
                    ('ATTRIBUTE-VALUE-STRING' in elem.tag or 'ATTRIBUTE-VALUE-XHTML' in elem.tag)):
                    for child in elem.iter():
                        if child.tag and 'THE-VALUE' in child.tag and child.text:
                            text_parts.append(child.text.strip())
        
        # Fallback: get all text content
        if not text_parts:
            all_text = []
            for elem in element.iter():
                if elem.text:
                    all_text.append(elem.text.strip())
            text_parts = all_text
        
        return ' '.join(filter(None, text_parts))
    
    def _extract_attributes(self, element) -> Dict[str, Any]:
        """Extract attributes from XML element"""
        attributes = {}
        
        # Get XML attributes
        for key, value in element.attrib.items():
            if key not in ['IDENTIFIER', 'identifier']:
                attributes[key] = value
        
        # Extract attribute values
        if HAS_LXML:
            # Use XPath for precise attribute extraction
            attr_values = element.xpath('.//VALUES/ATTRIBUTE-VALUE-*', namespaces=self.namespaces)
            
            for attr_val in attr_values:
                attr_def_ref = attr_val.get('ATTRIBUTE-DEFINITION-REF')
                if attr_def_ref:
                    value = self._extract_attribute_value(attr_val)
                    if value is not None:
                        attributes[attr_def_ref] = value
        else:
            # Manual extraction for standard library
            for child in element.iter():
                if child.tag and 'ATTRIBUTE-VALUE' in child.tag:
                    attr_def_ref = child.get('ATTRIBUTE-DEFINITION-REF')
                    if attr_def_ref:
                        value = self._extract_attribute_value(child)
                        if value is not None:
                            attributes[attr_def_ref] = value
        
        return attributes
    
    def _extract_attribute_value(self, attr_val_elem) -> Any:
        """Extract value from an attribute value element"""
        try:
            # Look for THE-VALUE element
            value_elem = self._find_element(attr_val_elem, './/THE-VALUE')
            if value_elem is not None:
                if value_elem.text:
                    return value_elem.text.strip()
                
                # Check for boolean values
                if 'true' in attr_val_elem.tag.lower() or 'false' in attr_val_elem.tag.lower():
                    return value_elem.get('value', '').lower() == 'true'
                
                # Check for numeric values
                if 'integer' in attr_val_elem.tag.lower():
                    try:
                        return int(value_elem.text or '0')
                    except ValueError:
                        return 0
                
                if 'real' in attr_val_elem.tag.lower():
                    try:
                        return float(value_elem.text or '0.0')
                    except ValueError:
                        return 0.0
            
            # Fallback to element text
            return attr_val_elem.text.strip() if attr_val_elem.text else None
            
        except Exception as e:
            logger.debug("Error extracting attribute value: %s", str(e))
            return None
    
    def validate_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a ReqIF file without full parsing
        
        Args:
            file_path: Path to the ReqIF file
            
        Returns:
            Dictionary with validation results
        """
        file_path = Path(file_path)
        result = {
            'valid': False,
            'format': None,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        try:
            if not file_path.exists():
                result['errors'].append(f"File not found: {file_path}")
                return result
            
            # Check file extension
            if file_path.suffix.lower() not in ['.reqif', '.reqifz']:
                result['warnings'].append(f"Unexpected file extension: {file_path.suffix}")
            
            # Basic format validation
            if file_path.suffix.lower() == '.reqifz':
                result['format'] = 'reqifz'
                if not zipfile.is_zipfile(file_path):
                    result['errors'].append("File is not a valid ZIP archive")
                    return result
            else:
                result['format'] = 'reqif'
            
            # Try to parse XML header
            try:
                if result['format'] == 'reqifz':
                    with zipfile.ZipFile(file_path, 'r') as zip_file:
                        reqif_files = [f for f in zip_file.namelist() if f.endswith('.reqif')]
                        if not reqif_files:
                            result['errors'].append("No .reqif files found in archive")
                            return result
                        with zip_file.open(reqif_files[0]) as reqif_file:
                            # Read just the beginning for validation
                            xml_header = reqif_file.read(1024)
                else:
                    with open(file_path, 'rb') as f:
                        xml_header = f.read(1024)
                
                # Check for XML declaration and ReqIF elements
                header_str = xml_header.decode('utf-8', errors='ignore')
                if 'REQ-IF' not in header_str and 'reqif' not in header_str.lower():
                    result['warnings'].append("File may not be a valid ReqIF file")
                
                result['valid'] = True
                
            except Exception as e:
                result['errors'].append(f"Error reading file content: {str(e)}")
        
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
        
        return result
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning("Failed to cleanup temp file %s: %s", temp_file, str(e))
        self.temp_files.clear()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


def validate_reqif_file(file_path: Union[str, Path]) -> bool:
    """
    Quick validation of ReqIF file format
    
    Args:
        file_path: Path to the ReqIF file
        
    Returns:
        True if file appears to be valid ReqIF format
    """
    parser = ReqIFParser()
    result = parser.validate_file(file_path)
    return result['valid'] and not result['errors']


def extract_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract metadata from ReqIF file without full parsing
    
    Args:
        file_path: Path to the ReqIF file
        
    Returns:
        Dictionary containing file metadata
    """
    parser = ReqIFParser()
    try:
        result = parser.parse_file(file_path)
        return result.metadata
    except Exception as e:
        logger.error("Failed to extract metadata from %s: %s", file_path, str(e))
        return {}