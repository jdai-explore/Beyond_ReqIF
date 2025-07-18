#!/usr/bin/env python3
"""
ReqIF Comparator Module - Updated Version
Handles comparison logic between two sets of requirements with clear separation
between content modifications and structural differences.
"""

from typing import List, Dict, Any, Tuple, Set
import difflib
import os


class ReqIFComparator:
    """Compares two sets of ReqIF requirements with content/structural separation"""
    
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
            Dictionary with categorized results: added, deleted, content_modified, 
            structural_only, unchanged
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
            
            content_modified = []
            structural_only = []
            unchanged = []
            
            # Track structural changes across all files
            all_added_fields = set()
            all_removed_fields = set()
            
            for req_id in common_ids:
                try:
                    req1 = file1_dict[req_id]
                    req2 = file2_dict[req_id]
                    
                    # Analyze changes
                    comparison_result = self._analyze_requirement_changes(req1, req2)
                    
                    if comparison_result['has_content_changes']:
                        # Create entry for content modifications
                        modified_entry = self._create_content_modified_entry(req_id, req1, req2, comparison_result)
                        content_modified.append(modified_entry)
                    elif comparison_result['has_structural_changes']:
                        # Create entry for structural-only changes
                        structural_entry = self._create_structural_entry(req_id, req1, req2, comparison_result)
                        structural_only.append(structural_entry)
                    else:
                        # Completely identical
                        unchanged.append(req2)
                    
                    # Track field changes for statistics
                    all_added_fields.update(comparison_result['added_fields'])
                    all_removed_fields.update(comparison_result['removed_fields'])
                        
                except Exception as e:
                    print(f"Error processing common requirement {req_id}: {e}")
                    # Add to unchanged to avoid losing the requirement
                    try:
                        unchanged.append(file2_dict.get(req_id, file1_dict.get(req_id, {})))
                    except:
                        pass
                    continue
            
            print(f"Final counts: Added={len(added)}, Deleted={len(deleted)}, "
                  f"Content Modified={len(content_modified)}, Structural Only={len(structural_only)}, "
                  f"Unchanged={len(unchanged)}")
            
            # Calculate statistics
            total_reqs = len(file1_reqs) + len(added)
            stats = {
                'total_file1': len(file1_reqs),
                'total_file2': len(file2_reqs),
                'total_unique': total_reqs,
                'added_count': len(added),
                'deleted_count': len(deleted),
                'content_modified_count': len(content_modified),
                'structural_only_count': len(structural_only),
                'unchanged_count': len(unchanged),
                'content_change_percentage': round((len(content_modified)) / max(total_reqs, 1) * 100, 2),
                'total_change_percentage': round((len(added) + len(deleted) + len(content_modified)) / max(total_reqs, 1) * 100, 2),
                'added_fields': sorted(list(all_added_fields)),
                'removed_fields': sorted(list(all_removed_fields))
            }
            
            return {
                'added': added,
                'deleted': deleted,
                'content_modified': content_modified,
                'structural_only': structural_only,
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
                'content_modified': [],
                'structural_only': [],
                'unchanged': [],
                'statistics': {
                    'total_file1': len(file1_reqs) if isinstance(file1_reqs, list) else 0,
                    'total_file2': len(file2_reqs) if isinstance(file2_reqs, list) else 0,
                    'total_unique': 0,
                    'added_count': 0,
                    'deleted_count': 0,
                    'content_modified_count': 0,
                    'structural_only_count': 0,
                    'unchanged_count': 0,
                    'content_change_percentage': 0.0,
                    'total_change_percentage': 0.0,
                    'added_fields': [],
                    'removed_fields': []
                }
            }
    
    def _analyze_requirement_changes(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze changes between two requirements, separating content and structural changes
        
        Returns:
            Dict with analysis results including:
            - has_content_changes: bool
            - has_structural_changes: bool
            - content_changes: list of changes in common fields
            - added_fields: set of fields only in req2
            - removed_fields: set of fields only in req1
            - common_fields: set of fields in both
        """
        # Get fields from both requirements
        fields1 = self._get_requirement_fields(req1)
        fields2 = self._get_requirement_fields(req2)
        
        # Categorize fields
        common_fields = fields1 & fields2
        added_fields = fields2 - fields1
        removed_fields = fields1 - fields2
        
        # Check for content changes in common fields
        content_changes = []
        for field in common_fields:
            value1 = self._get_field_value(req1, field)
            value2 = self._get_field_value(req2, field)
            
            # Normalize and compare values
            norm_value1 = str(value1).strip() if value1 is not None else ''
            norm_value2 = str(value2).strip() if value2 is not None else ''
            
            if norm_value1 != norm_value2:
                content_changes.append({
                    'field': field,
                    'old_value': norm_value1,
                    'new_value': norm_value2,
                    'change_type': 'modified'
                })
        
        return {
            'has_content_changes': len(content_changes) > 0,
            'has_structural_changes': len(added_fields) > 0 or len(removed_fields) > 0,
            'content_changes': content_changes,
            'added_fields': added_fields,
            'removed_fields': removed_fields,
            'common_fields': common_fields
        }
    
    def _get_requirement_fields(self, req: Dict[str, Any]) -> Set[str]:
        """Get all comparable fields from a requirement"""
        fields = set()
        
        if not isinstance(req, dict):
            return fields
        
        # Add regular fields (excluding internal ones)
        excluded_fields = {'content', 'raw_attributes', '_comparison_data'}
        for field in req.keys():
            if field not in excluded_fields and not field.startswith('_'):
                fields.add(field)
        
        # Add attribute fields with special prefix
        attributes = req.get('attributes', {})
        if isinstance(attributes, dict):
            for attr_name in attributes.keys():
                fields.add(f'attribute.{attr_name}')
        
        return fields
    
    def _get_field_value(self, req: Dict[str, Any], field: str) -> Any:
        """Get value for a field, handling both regular and attribute fields"""
        if field.startswith('attribute.'):
            # Extract attribute name and get from attributes dict
            attr_name = field[10:]  # Remove 'attribute.' prefix
            attributes = req.get('attributes', {})
            if isinstance(attributes, dict):
                return attributes.get(attr_name, None)
            return None
        else:
            # Regular field
            return req.get(field, None)
    
    def _create_content_modified_entry(self, req_id: str, req1: Dict[str, Any], 
                                     req2: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create entry for content-modified requirement"""
        try:
            # Get changed field names for summary
            changed_fields = [change['field'] for change in analysis['content_changes']]
            changes_summary = ', '.join(changed_fields) if changed_fields else 'Unknown changes'
            
            # Create the modified entry using the NEW version as base
            modified_entry = {}
            
            # Copy all actual fields from req2
            for field_name, field_value in req2.items():
                if field_name not in ['_comparison_data']:
                    modified_entry[field_name] = field_value
            
            # Ensure we have an ID
            modified_entry['id'] = req_id
            
            # Add change metadata
            modified_entry.update({
                'changes_summary': changes_summary,
                'changed_fields': changed_fields,
                'change_count': len(changed_fields),
                
                # Comparison data for diff viewer
                '_comparison_data': {
                    'old': self._safe_copy_dict(req1),
                    'new': self._safe_copy_dict(req2),
                    'changes': analysis['content_changes'],
                    'detailed_changes': self._create_detailed_changes(req1, req2, analysis['content_changes'])
                }
            })
            
            return modified_entry
            
        except Exception as e:
            print(f"Error creating content modified entry for {req_id}: {e}")
            # Return basic fallback
            return {
                'id': req_id,
                'attributes': req2.get('attributes', {}) if isinstance(req2, dict) else {},
                'changes_summary': 'Error processing changes',
                'changed_fields': [],
                'change_count': 0
            }
    
    def _create_structural_entry(self, req_id: str, req1: Dict[str, Any], 
                               req2: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create entry for structural-only changes"""
        try:
            # Create entry using req2 as base
            structural_entry = {}
            
            # Copy all fields from req2
            for field_name, field_value in req2.items():
                if field_name not in ['_comparison_data']:
                    structural_entry[field_name] = field_value
            
            # Ensure we have an ID
            structural_entry['id'] = req_id
            
            # Add structural change metadata
            structural_entry.update({
                'added_fields': sorted(list(analysis['added_fields'])),
                'removed_fields': sorted(list(analysis['removed_fields'])),
                'structural_changes_only': True,
                
                # Include comparison data for viewing
                '_comparison_data': {
                    'old': self._safe_copy_dict(req1),
                    'new': self._safe_copy_dict(req2),
                    'added_fields': analysis['added_fields'],
                    'removed_fields': analysis['removed_fields']
                }
            })
            
            return structural_entry
            
        except Exception as e:
            print(f"Error creating structural entry for {req_id}: {e}")
            return req2  # Return req2 as fallback
    
    def _safe_copy_dict(self, source_dict):
        """Safely copy a dictionary, handling non-dict inputs"""
        try:
            if isinstance(source_dict, dict):
                return source_dict.copy()
            else:
                return {}
        except:
            return {}
    
    def _create_detailed_changes(self, req1: Dict[str, Any], req2: Dict[str, Any], 
                               changes: List[Dict[str, str]]) -> Dict[str, Dict]:
        """Create detailed change information for diff viewer"""
        detailed_changes = {}
        
        try:
            for change in changes:
                try:
                    field = change.get('field', '')
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
                        'change_type': 'modified',
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
            
            # Get common fields only for similarity calculation
            fields1 = self._get_requirement_fields(req1)
            fields2 = self._get_requirement_fields(req2)
            common_fields = fields1 & fields2
            
            for field in common_fields:
                val1 = self._get_field_value(req1, field)
                val2 = self._get_field_value(req2, field)
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
        """Generate a text summary of the comparison results"""
        try:
            if not isinstance(comparison_results, dict):
                return "Error: Invalid comparison results"
            
            stats = comparison_results.get('statistics', {})
            
            # Build summary string
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
                f"- Content Modified: {stats.get('content_modified_count', 0)} requirements",
                f"- Structure Only Changes: {stats.get('structural_only_count', 0)} requirements",
                f"- Unchanged: {stats.get('unchanged_count', 0)} requirements",
                "",
                f"Content Change Rate: {stats.get('content_change_percentage', 0)}%",
                f"Overall Change Rate: {stats.get('total_change_percentage', 0)}%",
                "",
                "Structural Changes:"
            ]
            
            # Add field changes
            added_fields = stats.get('added_fields', [])
            removed_fields = stats.get('removed_fields', [])
            
            if added_fields:
                summary_lines.append(f"- Added Fields: {', '.join(added_fields[:5])}")
                if len(added_fields) > 5:
                    summary_lines.append(f"  ... and {len(added_fields) - 5} more")
            else:
                summary_lines.append("- No fields added")
                
            if removed_fields:
                summary_lines.append(f"- Removed Fields: {', '.join(removed_fields[:5])}")
                if len(removed_fields) > 5:
                    summary_lines.append(f"  ... and {len(removed_fields) - 5} more")
            else:
                summary_lines.append("- No fields removed")
            
            summary_lines.append("")
            summary_lines.append("Detailed Changes:")
            
            # Add details for each category
            for category in ['added', 'deleted', 'content_modified', 'structural_only']:
                try:
                    requirements = comparison_results.get(category, [])
                    if requirements and isinstance(requirements, list):
                        summary_lines.append("")
                        summary_lines.append(f"{category.replace('_', ' ').title()} Requirements ({len(requirements)}):")
                        
                        for req in requirements[:5]:  # Show first 5
                            if isinstance(req, dict):
                                req_id = req.get('id', 'No ID')
                                
                                if category == 'content_modified':
                                    change_count = req.get('change_count', 0)
                                    changes_summary = req.get('changes_summary', 'Unknown changes')
                                    summary_lines.append(f"  ~ {req_id}: {changes_summary} ({change_count} field(s))")
                                elif category == 'structural_only':
                                    added = len(req.get('added_fields', []))
                                    removed = len(req.get('removed_fields', []))
                                    summary_lines.append(f"  ~ {req_id}: +{added} fields, -{removed} fields")
                                else:
                                    prefix = "+" if category == 'added' else "-"
                                    display_text = self._get_requirement_display_text(req)
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
        """Get appropriate display text for a requirement"""
        try:
            if not isinstance(req, dict):
                return "Invalid requirement"
            
            # Try to find the best field for display
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
                        display_text = str(attributes[attr_name])
                        if len(display_text) > 50:
                            display_text = display_text[:50] + "..."
                        display_candidates.append(display_text)
                        break
                
                # If no priority attributes found, use first attribute
                if not any(attr in attributes for attr in priority_attrs) and attributes:
                    first_attr = next(iter(attributes.values()))
                    if first_attr:
                        display_text = str(first_attr)
                        if len(display_text) > 50:
                            display_text = display_text[:50] + "..."
                        display_candidates.append(display_text)
            
            # Return best candidate or fallback to ID
            return display_candidates[0] if display_candidates else req.get('id', 'Unknown')
            
        except Exception as e:
            print(f"Error getting display text: {e}")
            return req.get('id', 'Unknown')


# Example usage and testing
if __name__ == "__main__":
    print("ReqIF Comparator - Updated Version with Content/Structural Separation")
    print("Features: Clear distinction between content changes and structural differences")
    
    comparator = ReqIFComparator()
    
    # Test with sample requirements
    req1_list = [
        {
            'id': 'REQ-001',
            'type': 'Functional',
            'attributes': {
                'Title': 'Login Feature',
                'Description': 'User authentication',
                'Priority': 'High'
            }
        }
    ]
    
    req2_list = [
        {
            'id': 'REQ-001',
            'type': 'Functional',
            'attributes': {
                'Title': 'Login Feature',
                'Description': 'User authentication with SSO',  # Content change
                'Priority': 'High',
                'Status': 'Approved'  # New field (structural change)
            }
        }
    ]
    
    results = comparator.compare_requirements(req1_list, req2_list)
    print(f"\nContent Modified: {results['statistics']['content_modified_count']}")
    print(f"Structural Only: {results['statistics']['structural_only_count']}")
    print(f"Added Fields: {results['statistics']['added_fields']}")
    
    print("\nReqIF Comparator ready!")