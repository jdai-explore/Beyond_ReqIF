#!/usr/bin/env python3
"""
ReqIF Comparator Module - Updated Version
Handles comparison logic between two sets of requirements with dynamic field detection.
Enhanced with dynamic field comparison - no hardcoded field assumptions.
"""

from typing import List, Dict, Any, Tuple, Set
import difflib
import os


class ReqIFComparator:
    """Compares two sets of ReqIF requirements with dynamic field detection"""
    
    def __init__(self):
        self.similarity_threshold = 0.8  # For fuzzy matching (future use)
        
    def compare_requirements(self, file1_reqs: List[Dict[str, Any]], 
                           file2_reqs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare two sets of requirements and categorize differences
        
        Args:
            file1_reqs: Requirements from the first file (original)
            file2_reqs: Requirements from the second file (modified)
            
        Returns:
            Dictionary with categorized results: added, deleted, modified, unchanged
        """
        print(f"Starting comparison: {len(file1_reqs)} vs {len(file2_reqs)} requirements")
        
        try:
            # Ensure we have valid lists
            if not isinstance(file1_reqs, list):
                print(f"Warning: file1_reqs is not a list, got {type(file1_reqs)}")
                file1_reqs = []
            if not isinstance(file2_reqs, list):
                print(f"Warning: file2_reqs is not a list, got {type(file2_reqs)}")
                file2_reqs = []
            
            # Create ID-based lookup dictionaries
            file1_dict = {}
            file2_dict = {}
            
            # Safely build file1_dict
            for i, req in enumerate(file1_reqs):
                try:
                    if isinstance(req, dict) and req.get('id'):
                        file1_dict[req['id']] = req
                    else:
                        print(f"Skipping invalid requirement {i} in file1: {type(req)}")
                except Exception as e:
                    print(f"Error processing file1 requirement {i}: {e}")
                    continue
            
            # Safely build file2_dict
            for i, req in enumerate(file2_reqs):
                try:
                    if isinstance(req, dict) and req.get('id'):
                        file2_dict[req['id']] = req
                    else:
                        print(f"Skipping invalid requirement {i} in file2: {type(req)}")
                except Exception as e:
                    print(f"Error processing file2 requirement {i}: {e}")
                    continue
            
            print(f"Valid requirements: {len(file1_dict)} vs {len(file2_dict)}")
            
            # Find all unique IDs
            file1_ids = set(file1_dict.keys())
            file2_ids = set(file2_dict.keys())
            
            # Categorize changes
            added_ids = file2_ids - file1_ids
            deleted_ids = file1_ids - file2_ids
            common_ids = file1_ids & file2_ids
            
            print(f"Changes: Added={len(added_ids)}, Deleted={len(deleted_ids)}, Common={len(common_ids)}")
            
            # Process each category
            added = [file2_dict[req_id] for req_id in added_ids]
            deleted = [file1_dict[req_id] for req_id in deleted_ids]
            
            modified = []
            unchanged = []
            
            for req_id in common_ids:
                try:
                    req1 = file1_dict[req_id]
                    req2 = file2_dict[req_id]
                    
                    if self._requirements_differ(req1, req2):
                        # Create a GUI-friendly modified entry
                        modified_entry = self._create_modified_entry(req_id, req1, req2)
                        if modified_entry:  # Only add if creation was successful
                            modified.append(modified_entry)
                    else:
                        unchanged.append(req2)  # Use the newer version
                        
                except Exception as e:
                    print(f"Error processing common requirement {req_id}: {e}")
                    # Add to unchanged to avoid losing the requirement
                    try:
                        unchanged.append(file2_dict.get(req_id, file1_dict.get(req_id, {})))
                    except:
                        pass
                    continue
            
            print(f"Final counts: Added={len(added)}, Deleted={len(deleted)}, Modified={len(modified)}, Unchanged={len(unchanged)}")
            
            # Calculate statistics
            total_reqs = len(file1_reqs) + len(added)
            stats = {
                'total_file1': len(file1_reqs),
                'total_file2': len(file2_reqs),
                'total_unique': total_reqs,
                'added_count': len(added),
                'deleted_count': len(deleted),
                'modified_count': len(modified),
                'unchanged_count': len(unchanged),
                'change_percentage': round((len(added) + len(deleted) + len(modified)) / max(total_reqs, 1) * 100, 2)
            }
            
            return {
                'added': added,
                'deleted': deleted,
                'modified': modified,
                'unchanged': unchanged,
                'statistics': stats
            }
            
        except Exception as e:
            print(f"Critical error in compare_requirements: {e}")
            import traceback
            traceback.print_exc()
            
            # Return safe fallback structure
            return {
                'added': [],
                'deleted': [],
                'modified': [],
                'unchanged': [],
                'statistics': {
                    'total_file1': len(file1_reqs) if isinstance(file1_reqs, list) else 0,
                    'total_file2': len(file2_reqs) if isinstance(file2_reqs, list) else 0,
                    'total_unique': 0,
                    'added_count': 0,
                    'deleted_count': 0,
                    'modified_count': 0,
                    'unchanged_count': 0,
                    'change_percentage': 0.0
                }
            }
    
    def _get_comparable_fields(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> Set[str]:
        """Dynamically detect which fields can be compared between two requirements"""
        fields1 = set(req1.keys()) if isinstance(req1, dict) else set()
        fields2 = set(req2.keys()) if isinstance(req2, dict) else set()
        
        # Get all fields present in either requirement
        all_fields = fields1 | fields2
        
        # Exclude internal/meta fields
        excluded_fields = {'content', 'raw_attributes', '_comparison_data'}
        comparable_fields = all_fields - excluded_fields
        
        return comparable_fields
    
    def _requirements_differ(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Check if two requirements are different using dynamic field detection"""
        try:
            # Ensure we have dictionaries
            if not isinstance(req1, dict) or not isinstance(req2, dict):
                return True  # Consider different if not both dicts
            
            # Get fields that can be compared
            comparable_fields = self._get_comparable_fields(req1, req2)
            
            # Compare each comparable field
            for field in comparable_fields:
                if field == 'attributes':
                    # Special handling for attributes
                    if self._attributes_differ(req1.get('attributes', {}), req2.get('attributes', {})):
                        return True
                else:
                    # Compare regular fields
                    val1 = str(req1.get(field, '') or '').strip()
                    val2 = str(req2.get(field, '') or '').strip()
                    if val1 != val2:
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error in _requirements_differ: {e}")
            return True
    
    def _attributes_differ(self, attrs1: Dict[str, Any], attrs2: Dict[str, Any]) -> bool:
        """Compare attributes dictionaries"""
        try:
            # Ensure attributes are dictionaries
            if not isinstance(attrs1, dict):
                attrs1 = {}
            if not isinstance(attrs2, dict):
                attrs2 = {}
            
            # Check if attribute sets are different
            if set(attrs1.keys()) != set(attrs2.keys()):
                return True
                
            # Check if any attribute values differ
            for key in attrs1.keys():
                try:
                    val1 = str(attrs1.get(key, '') or '').strip()
                    val2 = str(attrs2.get(key, '') or '').strip()
                    if val1 != val2:
                        return True
                except Exception as e:
                    print(f"Error comparing attribute {key}: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            print(f"Error comparing attributes: {e}")
            return True
    
    def _create_modified_entry(self, req_id: str, req1: Dict[str, Any], req2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a GUI-friendly modified entry that shows the new version with change metadata
        """
        try:
            print(f"Creating modified entry for {req_id}")
            
            # Ensure we have valid dictionaries
            if not isinstance(req1, dict):
                print(f"Warning: req1 for {req_id} is not a dict: {type(req1)}")
                req1 = {}
            if not isinstance(req2, dict):
                print(f"Warning: req2 for {req_id} is not a dict: {type(req2)}")
                req2 = {}
            
            # Identify detailed changes
            changes = self._identify_changes(req1, req2)
            print(f"Changes identified for {req_id}: {len(changes) if isinstance(changes, list) else 'ERROR'}")
            
            # Extract field names from changes LIST
            change_fields = []
            if isinstance(changes, list):
                for change in changes:
                    if isinstance(change, dict) and 'field' in change:
                        field_name = change['field']
                        if field_name and field_name not in change_fields:
                            change_fields.append(field_name)
            
            changes_summary = ', '.join(change_fields) if change_fields else 'Unknown changes'
            print(f"Change summary for {req_id}: {changes_summary}")
            
            # Safely extract values with comprehensive defaults
            def safe_get(req_dict, key, default=''):
                try:
                    if not isinstance(req_dict, dict):
                        return str(default)
                    value = req_dict.get(key, default)
                    return str(value if value is not None else default)
                except Exception as e:
                    print(f"Error getting {key}: {e}")
                    return str(default)
            
            # Create the modified entry using the NEW version as base (for tree display)
            # Start with all fields from the new requirement
            modified_entry = {}
            
            # Copy all actual fields from req2
            for field_name, field_value in req2.items():
                if field_name not in ['_comparison_data']:  # Exclude internal fields
                    modified_entry[field_name] = field_value
            
            # Ensure we have an ID
            modified_entry['id'] = req_id
            
            # Add change-specific metadata
            modified_entry.update({
                'changes_summary': changes_summary,
                'changed_fields': change_fields,
                'change_count': len(change_fields),
                
                # Comparison data for diff viewer
                '_comparison_data': {
                    'old': self._safe_copy_dict(req1),
                    'new': self._safe_copy_dict(req2),
                    'changes': changes if isinstance(changes, list) else [],
                    'detailed_changes': self._create_detailed_changes(req1, req2, changes)
                }
            })
            
            print(f"Successfully created modified entry for {req_id}")
            return modified_entry
            
        except Exception as e:
            print(f"Error creating modified entry for {req_id}: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a basic fallback entry
            return {
                'id': req_id,
                'attributes': req2.get('attributes', {}) if isinstance(req2, dict) else {},
                'changes_summary': 'Error processing changes',
                'changed_fields': [],
                'change_count': 0,
                '_comparison_data': {
                    'old': self._safe_copy_dict(req1),
                    'new': self._safe_copy_dict(req2),
                    'changes': [],
                    'detailed_changes': {}
                }
            }
    
    def _safe_copy_dict(self, source_dict):
        """Safely copy a dictionary, handling non-dict inputs"""
        try:
            if isinstance(source_dict, dict):
                return source_dict.copy()
            else:
                return {}
        except:
            return {}
    
    def _identify_changes(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify specific changes between two requirements using dynamic field detection"""
        changes = []
        
        try:
            # Ensure we have valid dictionaries
            if not isinstance(req1, dict) or not isinstance(req2, dict):
                return []
            
            # Get all comparable fields
            comparable_fields = self._get_comparable_fields(req1, req2)
            
            # Check changes in regular fields (excluding attributes)
            regular_fields = comparable_fields - {'attributes'}
            
            for field in regular_fields:
                try:
                    old_val = str(req1.get(field, '') or '').strip()
                    new_val = str(req2.get(field, '') or '').strip()
                    
                    if old_val != new_val:
                        change_type = 'modified'
                        if not old_val:
                            change_type = 'added'
                        elif not new_val:
                            change_type = 'deleted'
                        
                        changes.append({
                            'field': field,
                            'old_value': old_val,
                            'new_value': new_val,
                            'change_type': change_type
                        })
                except Exception as e:
                    print(f"Error processing field {field}: {e}")
                    continue
            
            # Check attribute changes with robust error handling
            try:
                attrs1 = req1.get('attributes', {})
                attrs2 = req2.get('attributes', {})
                
                # Ensure attributes are dictionaries
                if not isinstance(attrs1, dict):
                    attrs1 = {}
                if not isinstance(attrs2, dict):
                    attrs2 = {}
                
                all_attr_keys = set(attrs1.keys()) | set(attrs2.keys())
                
                for attr_key in all_attr_keys:
                    try:
                        val1 = str(attrs1.get(attr_key, '') or '').strip()
                        val2 = str(attrs2.get(attr_key, '') or '').strip()
                        
                        if val1 != val2:
                            change_type = 'modified'
                            if not val1:
                                change_type = 'added'
                            elif not val2:
                                change_type = 'deleted'
                            
                            changes.append({
                                'field': f'attribute.{attr_key}',
                                'old_value': val1,
                                'new_value': val2,
                                'change_type': change_type
                            })
                    except Exception as e:
                        print(f"Error processing attribute {attr_key}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error processing attributes: {e}")
        
        except Exception as e:
            print(f"Error in _identify_changes: {e}")
        
        return changes
    
    def _create_detailed_changes(self, req1: Dict[str, Any], req2: Dict[str, Any], changes: List[Dict[str, str]]) -> Dict[str, Dict]:
        """Create detailed change information for diff viewer"""
        detailed_changes = {}
        
        try:
            # Ensure we have a valid list of changes
            if not isinstance(changes, list):
                return {}
            
            for change in changes:
                try:
                    if not isinstance(change, dict):
                        continue
                    
                    field = change.get('field', '')
                    change_type = change.get('change_type', 'modified')
                    old_value = str(change.get('old_value', '') or '')
                    new_value = str(change.get('new_value', '') or '')
                    
                    if not field:
                        continue
                    
                    # Generate text diff for the field
                    diff_lines = []
                    try:
                        if old_value and new_value:
                            diff_lines = self.get_text_diff(old_value, new_value)
                    except Exception as e:
                        print(f"Error generating diff for field {field}: {e}")
                        diff_lines = []
                    
                    detailed_changes[field] = {
                        'change_type': change_type,
                        'old_value': old_value,
                        'new_value': new_value,
                        'diff_lines': diff_lines,
                        'similarity': self._calculate_field_similarity(old_value, new_value)
                    }
                    
                except Exception as e:
                    print(f"Error processing change: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in _create_detailed_changes: {e}")
        
        return detailed_changes
    
    def _calculate_field_similarity(self, old_value: str, new_value: str) -> float:
        """Calculate similarity between two field values"""
        try:
            if not old_value and not new_value:
                return 1.0
            if not old_value or not new_value:
                return 0.0
            
            matcher = difflib.SequenceMatcher(None, str(old_value), str(new_value))
            return round(matcher.ratio(), 3)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def get_text_diff(self, text1: str, text2: str) -> List[str]:
        """Get a unified diff between two text strings"""
        try:
            if not text1 and not text2:
                return []
                
            lines1 = text1.splitlines() if text1 else ['']
            lines2 = text2.splitlines() if text2 else ['']
            
            diff = list(difflib.unified_diff(
                lines1, lines2,
                fromfile='Original',
                tofile='Modified',
                lineterm=''
            ))
            
            return diff
        except Exception as e:
            print(f"Error generating text diff: {e}")
            return []
    
    def calculate_similarity(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> float:
        """Calculate similarity score between two requirements (0.0 to 1.0)"""
        try:
            if not isinstance(req1, dict) or not isinstance(req2, dict):
                return 0.0
            
            # Get all text content from both requirements
            text1_parts = []
            text2_parts = []
            
            # Get comparable fields
            comparable_fields = self._get_comparable_fields(req1, req2)
            
            for field in comparable_fields:
                if field == 'attributes':
                    # Handle attributes specially
                    attrs1 = req1.get('attributes', {})
                    attrs2 = req2.get('attributes', {})
                    if isinstance(attrs1, dict):
                        text1_parts.extend(str(v) for v in attrs1.values() if v)
                    if isinstance(attrs2, dict):
                        text2_parts.extend(str(v) for v in attrs2.values() if v)
                else:
                    # Handle regular fields
                    val1 = req1.get(field, '')
                    val2 = req2.get(field, '')
                    if val1:
                        text1_parts.append(str(val1))
                    if val2:
                        text2_parts.append(str(val2))
            
            # Combine texts
            text1 = ' '.join(text1_parts).lower().strip()
            text2 = ' '.join(text2_parts).lower().strip()
            
            if not text1 and not text2:
                return 1.0
            if not text1 or not text2:
                return 0.0
                
            # Use SequenceMatcher for similarity
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_similar_requirements(self, req: Dict[str, Any], 
                                candidates: List[Dict[str, Any]], 
                                threshold: float = 0.8) -> List[Tuple[Dict[str, Any], float]]:
        """Find requirements similar to the given requirement"""
        similar = []
        
        try:
            for candidate in candidates:
                similarity = self.calculate_similarity(req, candidate)
                if similarity >= threshold:
                    similar.append((candidate, similarity))
            
            # Sort by similarity (highest first)
            similar.sort(key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"Error finding similar requirements: {e}")
        
        return similar
    
    def calculate_filename_similarity(self, filename1: str, filename2: str) -> float:
        """
        Calculate similarity between two filenames for folder comparison
        
        Args:
            filename1: First filename
            filename2: Second filename
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Remove extensions for comparison
            name1 = os.path.splitext(filename1.lower())[0]
            name2 = os.path.splitext(filename2.lower())[0]
            
            # Use SequenceMatcher for similarity
            matcher = difflib.SequenceMatcher(None, name1, name2)
            return matcher.ratio()
        except Exception as e:
            print(f"Error calculating filename similarity: {e}")
            return 0.0
    
    def calculate_path_similarity(self, path1: str, path2: str) -> float:
        """
        Calculate similarity between two file paths for folder comparison
        
        Args:
            path1: First file path
            path2: Second file path
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Normalize paths
            norm_path1 = os.path.normpath(path1.lower())
            norm_path2 = os.path.normpath(path2.lower())
            
            # Use SequenceMatcher for similarity
            matcher = difflib.SequenceMatcher(None, norm_path1, norm_path2)
            return matcher.ratio()
        except Exception as e:
            print(f"Error calculating path similarity: {e}")
            return 0.0
    
    def export_comparison_summary(self, comparison_results: Dict[str, Any]) -> str:
        """Generate a text summary of the comparison results with dynamic field detection"""
        try:
            if not isinstance(comparison_results, dict):
                return "Error: Invalid comparison results"
            
            stats = comparison_results.get('statistics', {})
            
            # Build summary string step by step
            summary_lines = [
                "ReqIF Comparison Summary",
                "========================",
                "",
                "File Statistics:",
                f"- Original file: {stats.get('total_file1', 0)} requirements",
                f"- Modified file: {stats.get('total_file2', 0)} requirements",
                f"- Total unique requirements: {stats.get('total_unique', 0)}",
                "",
                "Changes Detected:",
                f"- Added: {stats.get('added_count', 0)} requirements",
                f"- Deleted: {stats.get('deleted_count', 0)} requirements",
                f"- Modified: {stats.get('modified_count', 0)} requirements",
                f"- Unchanged: {stats.get('unchanged_count', 0)} requirements",
                "",
                f"Overall Change Rate: {stats.get('change_percentage', 0)}%",
                "",
                "Detailed Changes:",
            ]
            
            # Add details for each category safely
            for category in ['added', 'deleted', 'modified']:
                try:
                    requirements = comparison_results.get(category, [])
                    if requirements and isinstance(requirements, list):
                        summary_lines.append("")
                        summary_lines.append(f"{category.title()} Requirements ({len(requirements)}):")
                        
                        for req in requirements[:5]:  # Show first 5
                            if isinstance(req, dict):
                                req_id = req.get('id', 'No ID')
                                
                                # Get display text dynamically
                                display_text = self._get_requirement_display_text(req)
                                
                                if category == 'modified':
                                    change_count = req.get('change_count', 0)
                                    changes_summary = req.get('changes_summary', 'Unknown changes')
                                    summary_lines.append(f"  ~ {req_id}: {display_text}")
                                    summary_lines.append(f"    Changes: {changes_summary} ({change_count} field(s))")
                                else:
                                    prefix = "+" if category == 'added' else "-"
                                    summary_lines.append(f"  {prefix} {req_id}: {display_text}")
                        
                        if len(requirements) > 5:
                            remaining = len(requirements) - 5
                            summary_lines.append(f"  ... and {remaining} more")
                except Exception as e:
                    print(f"Error processing {category} requirements: {e}")
                    continue
            
            return '\n'.join(summary_lines)
            
        except Exception as e:
            print(f"Error generating comparison summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _get_requirement_display_text(self, req: Dict[str, Any]) -> str:
        """Get appropriate display text for a requirement using dynamic field detection"""
        try:
            if not isinstance(req, dict):
                return "Invalid requirement"
            
            # Try to find the best field for display
            # Priority order: identifier, type, first attribute, id
            display_candidates = []
            
            # Check for identifier
            if req.get('identifier') and req.get('identifier') != req.get('id'):
                display_candidates.append(req['identifier'])
            
            # Check for type
            if req.get('type'):
                display_candidates.append(req['type'])
            
            # Check for attributes that might be good for display
            attributes = req.get('attributes', {})
            if isinstance(attributes, dict) and attributes:
                # Look for common display-worthy attribute names
                priority_attrs = ['Object Text', 'Object Heading', 'Title', 'Name', 'Heading', 'Text']
                
                for attr_name in priority_attrs:
                    if attr_name in attributes and attributes[attr_name]:
                        display_candidates.append(str(attributes[attr_name])[:50] + "..." if len(str(attributes[attr_name])) > 50 else str(attributes[attr_name]))
                        break
                
                # If no priority attributes found, use first attribute
                if not any(attr in attributes for attr in priority_attrs):
                    first_attr = next(iter(attributes.values()))
                    if first_attr:
                        display_candidates.append(str(first_attr)[:50] + "..." if len(str(first_attr)) > 50 else str(first_attr))
            
            # Return best candidate or fallback to ID
            return display_candidates[0] if display_candidates else req.get('id', 'Unknown')
            
        except Exception as e:
            print(f"Error getting display text: {e}")
            return req.get('id', 'Unknown')


# Example usage and testing
if __name__ == "__main__":
    print("ReqIF Comparator - Enhanced Version with Dynamic Field Detection")
    print("Features: Dynamic field comparison, no hardcoded field assumptions")
    
    comparator = ReqIFComparator()
    
    # Test filename similarity
    print("\nTesting filename similarity:")
    files = [
        ("requirements_v1.reqif", "requirements_v2.reqif"),
        ("system_specs.reqif", "system_specifications.reqif"),
        ("old_file.reqif", "completely_different.reqif")
    ]
    
    for file1, file2 in files:
        similarity = comparator.calculate_filename_similarity(file1, file2)
        print(f"'{file1}' vs '{file2}': {similarity:.2f}")
    
    # Test path similarity
    print("\nTesting path similarity:")
    paths = [
        ("folder1/subfolder/file.reqif", "folder1/subfolder/file.reqif"),
        ("folder1/subfolder/file.reqif", "folder2/subfolder/file.reqif"),
        ("project/specs/requirements.reqif", "project/requirements/specs.reqif")
    ]
    
    for path1, path2 in paths:
        similarity = comparator.calculate_path_similarity(path1, path2)
        print(f"'{path1}' vs '{path2}': {similarity:.2f}")
    
    print("\nReqIF Comparator with dynamic field detection ready!")