#!/usr/bin/env python3
"""
Debug script to analyze exactly what's happening with your ReqIF file
Run this to see step-by-step what the parser is finding and extracting
"""

import xml.etree.ElementTree as ET
import zipfile
import tempfile
import shutil
import os

def debug_reqif_file(file_path):
    """Debug a ReqIF file to see exactly what's being extracted"""
    
    print("="*80)
    print("REQIF DEBUG ANALYSIS")
    print("="*80)
    
    # Handle .reqifz extraction
    if file_path.endswith('.reqifz'):
        print(f"Extracting ReqIFZ archive: {file_path}")
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find .reqif file
            reqif_file = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.reqif'):
                        reqif_file = os.path.join(root, file)
                        break
                if reqif_file:
                    break
            
            if not reqif_file:
                print("ERROR: No .reqif file found in archive")
                return
                
            file_path = reqif_file
            print(f"Found ReqIF file: {os.path.basename(reqif_file)}")
            
        except Exception as e:
            print(f"ERROR extracting archive: {e}")
            return
    
    try:
        # Parse XML
        print(f"\nParsing XML file: {file_path}")
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        print(f"Root element: {root.tag}")
        print(f"Root attributes: {root.attrib}")
        
        # Step 1: Find SPEC-OBJECT elements
        print("\n" + "-"*60)
        print("STEP 1: FINDING SPEC-OBJECT ELEMENTS")
        print("-"*60)
        
        spec_objects = root.findall(".//SPEC-OBJECT")
        print(f"Found {len(spec_objects)} SPEC-OBJECT elements")
        
        if len(spec_objects) == 0:
            print("ERROR: No SPEC-OBJECT elements found!")
            return
        
        # Analyze first few spec objects
        for i, spec_obj in enumerate(spec_objects[:3]):
            print(f"\n--- SPEC-OBJECT {i+1} ---")
            identifier = (spec_obj.get('IDENTIFIER') or spec_obj.get('identifier') or 
                         spec_obj.get('ID') or spec_obj.get('id'))
            long_name = (spec_obj.get('LONG-NAME') or spec_obj.get('long-name') or 
                        spec_obj.get('NAME') or spec_obj.get('name'))
            
            print(f"Identifier: {identifier}")
            print(f"Long Name: {long_name}")
            
            # Find TYPE element
            type_elem = spec_obj.find(".//TYPE")
            if type_elem is not None:
                type_ref = (type_elem.get('SPEC-OBJECT-TYPE-REF') or 
                           type_elem.get('spec-object-type-ref'))
                print(f"Type Reference: {type_ref}")
            
            # Find VALUES container
            values_elem = spec_obj.find(".//VALUES")
            if values_elem is not None:
                print(f"Found VALUES container")
                
                # Find all ATTRIBUTE-VALUE elements
                attr_values = (values_elem.findall(".//ATTRIBUTE-VALUE-STRING") +
                              values_elem.findall(".//ATTRIBUTE-VALUE-XHTML") +
                              values_elem.findall(".//ATTRIBUTE-VALUE-ENUMERATION"))
                
                print(f"Found {len(attr_values)} attribute values")
                
                for j, attr_val in enumerate(attr_values[:3]):  # Show first 3
                    print(f"\n  Attribute Value {j+1}:")
                    print(f"    Tag: {attr_val.tag}")
                    
                    # Check for DEFINITION
                    def_elem = attr_val.find(".//DEFINITION")
                    if def_elem is not None:
                        print(f"    Has DEFINITION element")
                        
                        # Find reference
                        ref_elements = (def_elem.findall(".//ATTRIBUTE-DEFINITION-STRING-REF") +
                                      def_elem.findall(".//ATTRIBUTE-DEFINITION-XHTML-REF") +
                                      def_elem.findall(".//ATTRIBUTE-DEFINITION-ENUMERATION-REF"))
                        
                        for ref_elem in ref_elements:
                            print(f"    Reference: {ref_elem.text}")
                    
                    # Check for THE-VALUE
                    the_value_elem = attr_val.find(".//THE-VALUE")
                    if the_value_elem is not None:
                        print(f"    Has THE-VALUE element")
                        
                        # Get the raw content
                        raw_content = ET.tostring(the_value_elem, encoding='unicode')
                        print(f"    Raw THE-VALUE content: {raw_content[:200]}...")
                        
                        # Try to extract text
                        text_content = extract_all_text(the_value_elem)
                        print(f"    Extracted text: '{text_content}'")
                    
                    # For enumeration, check VALUES
                    if 'ENUMERATION' in attr_val.tag:
                        enum_values_elem = attr_val.find(".//VALUES")
                        if enum_values_elem is not None:
                            enum_refs = enum_values_elem.findall(".//ENUM-VALUE-REF")
                            for enum_ref in enum_refs:
                                print(f"    Enum Reference: {enum_ref.text}")
        
        # Step 2: Find ATTRIBUTE-DEFINITION elements
        print("\n" + "-"*60)
        print("STEP 2: FINDING ATTRIBUTE-DEFINITION ELEMENTS")
        print("-"*60)
        
        attr_defs = (root.findall(".//ATTRIBUTE-DEFINITION-STRING") +
                    root.findall(".//ATTRIBUTE-DEFINITION-XHTML") +
                    root.findall(".//ATTRIBUTE-DEFINITION-ENUMERATION"))
        
        print(f"Found {len(attr_defs)} attribute definitions")
        
        for i, attr_def in enumerate(attr_defs[:5]):  # Show first 5
            identifier = (attr_def.get('IDENTIFIER') or attr_def.get('identifier'))
            long_name = (attr_def.get('LONG-NAME') or attr_def.get('long-name'))
            print(f"  {i+1}. ID: {identifier}, Name: {long_name}")
        
        # Step 3: Find SPEC-OBJECT-TYPE elements
        print("\n" + "-"*60)
        print("STEP 3: FINDING SPEC-OBJECT-TYPE ELEMENTS")
        print("-"*60)
        
        spec_types = root.findall(".//SPEC-OBJECT-TYPE")
        print(f"Found {len(spec_types)} spec object types")
        
        for i, spec_type in enumerate(spec_types[:3]):  # Show first 3
            identifier = (spec_type.get('IDENTIFIER') or spec_type.get('identifier'))
            long_name = (spec_type.get('LONG-NAME') or spec_type.get('long-name'))
            print(f"  {i+1}. ID: {identifier}, Name: {long_name}")
        
        print("\n" + "="*80)
        print("DEBUG ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"ERROR during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temp directory if created
        if file_path.endswith('.reqifz') and 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)

def extract_all_text(element):
    """Helper function to extract all text from an XML element"""
    texts = []
    
    if element.text:
        texts.append(element.text.strip())
    
    for child in element:
        child_text = extract_all_text(child)
        if child_text:
            texts.append(child_text)
        
        if child.tail:
            texts.append(child.tail.strip())
    
    full_text = ' '.join(texts)
    
    # Decode HTML entities
    import html
    full_text = html.unescape(full_text)
    
    return full_text.strip()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python debug_reqif.py <path_to_reqif_file>")
        print("Example: python debug_reqif.py myfile.reqifz")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    
    debug_reqif_file(file_path)