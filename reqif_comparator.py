#!/usr/bin/env python3
"""
ReqIF Comparator Module
Handles comparison logic between two sets of requirements.
COMPREHENSIVE FIX: Addresses 'list' object has no attribute 'keys' error
PHASE 1: Enhanced with comparison profile support
"""

from typing import List, Dict, Any, Tuple
import difflib


class ReqIFComparator:
    """Compares two sets of ReqIF requirements and identifies differences"""
    
    def __init__(self):
        self.similarity_threshold = 0.8  # For fuzzy matching (future use)
        self.comparison_profile = None  # Phase 1: Support for comparison profiles
        
    def set_comparison_profile(self, profile):
        """Set comparison profile for advanced comparison (Phase 1)"""
        self.comparison_profile = profile
        if profile:
            print(f"Using comparison profile: {profile.name}")
            print(f"Enabled attributes: {len(profile.get_enabled_attributes())}")
            print(f"Total weight: {profile.calculate_total_weight():.2f}")
        
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
    
    def _create_modified_entry(self, req_id: str, req1: Dict[str, Any], req2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a GUI-friendly modified entry that shows the new version with change metadata
        FIXED: Comprehensive error handling for the 'keys' attribute error
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
            
            # Identify detailed changes with comprehensive error handling
            changes = self._identify_changes(req1, req2)
            print(f"Changes identified for {req_id}: {len(changes) if isinstance(changes, list) else 'ERROR'}")
            
            # CRITICAL FIX: Extract field names from changes LIST, not calling .keys() on it
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
            modified_entry = {
                # Primary data from NEW version (for tree display)
                'id': req_id,
                'identifier': safe_get(req2, 'identifier', req_id),
                'title': safe_get(req2, 'title'),
                'description': safe_get(req2, 'description'),
                'type': safe_get(req2, 'type'),
                'priority': safe_get(req2, 'priority'),
                'status': safe_get(req2, 'status'),
                'attributes': req2.get('attributes', {}) if isinstance(req2.get('attributes'), dict) else {},
                'raw_attributes': req2.get('raw_attributes', {}) if isinstance(req2.get('raw_attributes'), dict) else {},
                'content': safe_get(req2, 'content'),
                
                # Change-specific metadata
                'changes_summary': changes_summary,
                'changed_fields': change_fields,
                'change_count': len(change_fields),
                
                # Comparison data for diff viewer (Phase 2)
                '_comparison_data': {
                    'old': self._safe_copy_dict(req1),
                    'new': self._safe_copy_dict(req2),
                    'changes': changes if isinstance(changes, list) else [],
                    'detailed_changes': self._create_detailed_changes(req1, req2, changes)
                }
            }
            
            print(f"Successfully created modified entry for {req_id}")
            return modified_entry
            
        except Exception as e:
            print(f"Error creating modified entry for {req_id}: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a basic fallback entry
            return {
                'id': req_id,
                'identifier': req_id,
                'title': str(req2.get('title', '') if isinstance(req2, dict) else ''),
                'description': str(req2.get('description', '') if isinstance(req2, dict) else ''),
                'type': str(req2.get('type', '') if isinstance(req2, dict) else ''),
                'priority': '',
                'status': '',
                'attributes': {},
                'raw_attributes': {},
                'content': '',
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
    
    def _requirements_differ(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Check if two requirements are different with robust error handling and profile support"""
        try:
            # Ensure we have dictionaries
            if not isinstance(req1, dict) or not isinstance(req2, dict):
                return True  # Consider different if not both dicts
            
            # Use comparison profile if available (Phase 1)
            if self.comparison_profile:
                return self._requirements_differ_with_profile(req1, req2)
            
            # Fallback to original comparison logic
            return self._requirements_differ_original(req1, req2)
            
        except Exception as e:
            print(f"Error in _requirements_differ: {e}")
            return True  # Consider different if comparison fails
    
    def _requirements_differ_with_profile(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Phase 1: Compare requirements using comparison profile"""
        try:
            enabled_attributes = self.comparison_profile.get_enabled_attributes()
            
            if not enabled_attributes:
                print("Warning: No enabled attributes in comparison profile")
                return self._requirements_differ_original(req1, req2)
            
            # Check each enabled attribute
            for attr_name, attr_config in enabled_attributes.items():
                if attr_config.weight <= 0:
                    continue  # Skip zero-weight attributes
                
                # Get values based on attribute type
                val1, val2 = self._get_attribute_values(req1, req2, attr_name, attr_config)
                
                # Apply comparison rules from profile
                if self._values_differ_with_rules(val1, val2):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error in profile-based comparison: {e}")
            return self._requirements_differ_original(req1, req2)
    
    def _requirements_differ_original(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Original comparison logic (fallback)"""
        try:
            # Compare key fields
            fields_to_compare = ['title', 'description', 'type', 'priority', 'status']
            
            for field in fields_to_compare:
                try:
                    val1 = str(req1.get(field, '') or '').strip()
                    val2 = str(req2.get(field, '') or '').strip()
                    if val1 != val2:
                        return True
                except Exception as e:
                    print(f"Error comparing field {field}: {e}")
                    continue
                    
            # Compare attributes
            try:
                attrs1 = req1.get('attributes', {})
                attrs2 = req2.get('attributes', {})
                
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
                        
            except Exception as e:
                print(f"Error comparing attributes: {e}")
                
            return False
            
        except Exception as e:
            print(f"Error in _requirements_differ_original: {e}")
            return True
    
    def _get_attribute_values(self, req1: Dict[str, Any], req2: Dict[str, Any], 
                            attr_name: str, attr_config) -> Tuple[str, str]:
        """Get attribute values from requirements based on attribute type"""
        try:
            if attr_config.field_type == "standard":
                # Standard field
                val1 = str(req1.get(attr_name, '') or '')
                val2 = str(req2.get(attr_name, '') or '')
            elif attr_name.startswith('attr_'):
                # Custom attribute
                clean_name = attr_name[5:]  # Remove 'attr_' prefix
                attrs1 = req1.get('attributes', {})
                attrs2 = req2.get('attributes', {})
                val1 = str(attrs1.get(clean_name, '') or '') if isinstance(attrs1, dict) else ''
                val2 = str(attrs2.get(clean_name, '') or '') if isinstance(attrs2, dict) else ''
            else:
                # Other field
                val1 = str(req1.get(attr_name, '') or '')
                val2 = str(req2.get(attr_name, '') or '')
            
            return val1.strip(), val2.strip()
            
        except Exception as e:
            print(f"Error getting values for attribute {attr_name}: {e}")
            return '', ''
    
    def _values_differ_with_rules(self, val1: str, val2: str) -> bool:
        """Compare values using comparison profile rules"""
        try:
            # Apply ignore rules from profile
            if self.comparison_profile.treat_empty_as_null:
                if not val1 and not val2:
                    return False
            
            if self.comparison_profile.ignore_case:
                val1 = val1.lower()
                val2 = val2.lower()
            
            if self.comparison_profile.ignore_whitespace:
                val1 = ' '.join(val1.split())  # Normalize whitespace
                val2 = ' '.join(val2.split())
            
            # Basic comparison
            if val1 == val2:
                return False
            
            # Fuzzy matching if enabled
            if self.comparison_profile.use_fuzzy_matching and val1 and val2:
                import difflib
                similarity = difflib.SequenceMatcher(None, val1, val2).ratio()
                return similarity < self.comparison_profile.similarity_threshold
            
            return True
            
        except Exception as e:
            print(f"Error in value comparison with rules: {e}")
            return val1 != val2
    
    def _identify_changes(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify specific changes between two requirements with robust error handling and profile support"""
        try:
            # Ensure we have valid dictionaries
            if not isinstance(req1, dict) or not isinstance(req2, dict):
                return []
            
            # Use comparison profile if available (Phase 1)
            if self.comparison_profile:
                return self._identify_changes_with_profile(req1, req2)
            
            # Fallback to original change identification
            return self._identify_changes_original(req1, req2)
        
        except Exception as e:
            print(f"Error in _identify_changes: {e}")
            return []
    
    def _identify_changes_with_profile(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> List[Dict[str, str]]:
        """Phase 1: Identify changes using comparison profile"""
        changes = []
        
        try:
            enabled_attributes = self.comparison_profile.get_enabled_attributes()
            
            if not enabled_attributes:
                return self._identify_changes_original(req1, req2)
            
            # Check each enabled attribute
            for attr_name, attr_config in enabled_attributes.items():
                try:
                    # Get values
                    val1, val2 = self._get_attribute_values(req1, req2, attr_name, attr_config)
                    
                    # Apply comparison rules and check for differences
                    if self._values_differ_with_rules(val1, val2):
                        change_type = 'modified'
                        if not val1:
                            change_type = 'added'
                        elif not val2:
                            change_type = 'deleted'
                        
                        changes.append({
                            'field': attr_name,
                            'old_value': val1,
                            'new_value': val2,
                            'change_type': change_type,
                            'weight': attr_config.weight,
                            'field_type': attr_config.field_type
                        })
                        
                except Exception as e:
                    print(f"Error processing attribute {attr_name}: {e}")
                    continue
            
            return changes
            
        except Exception as e:
            print(f"Error in profile-based change identification: {e}")
            return self._identify_changes_original(req1, req2)
    
    def _identify_changes_original(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> List[Dict[str, str]]:
        """Original change identification logic (fallback)"""
        changes = []
        
        try:
            # Check main field changes
            main_fields = ['title', 'description', 'type', 'priority', 'status']
            
            for field in main_fields:
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
            print(f"Error in _identify_changes_original: {e}")
        
        return changes
    
    def _create_detailed_changes(self, req1: Dict[str, Any], req2: Dict[str, Any], changes: List[Dict[str, str]]) -> Dict[str, Dict]:
        """
        Create detailed change information for diff viewer with robust error handling
        """
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
        """Calculate similarity between two field values with error handling"""
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
            
            # Simple similarity based on title and description
            title1 = str(req1.get('title', '') or '').lower()
            title2 = str(req2.get('title', '') or '').lower()
            desc1 = str(req1.get('description', '') or '').lower()
            desc2 = str(req2.get('description', '') or '').lower()
            
            # Combine texts
            text1 = (title1 + ' ' + desc1).strip()
            text2 = (title2 + ' ' + desc2).strip()
            
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
    
    def export_comparison_summary(self, comparison_results: Dict[str, Any]) -> str:
        """Generate a text summary of the comparison results"""
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
                                title = req.get('title', 'No title')
                                req_id = req.get('id', 'No ID')
                                if category == 'modified':
                                    change_count = req.get('change_count', 0)
                                    changes_summary = req.get('changes_summary', 'Unknown changes')
                                    summary_lines.append(f"  ~ {req_id}: {title}")
                                    summary_lines.append(f"    Changes: {changes_summary} ({change_count} field(s))")
                                else:
                                    prefix = "+" if category == 'added' else "-"
                                    summary_lines.append(f"  {prefix} {req_id}: {title}")
                        
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


# Example usage and testing
if __name__ == "__main__":
    print("ReqIF Comparator - Comprehensive Fix Version")
    print("Addresses 'list' object has no attribute 'keys' error")
    print("Enhanced with Phase 1 comparison profile support")
    
    comparator = ReqIFComparator()
    
    # Example requirements for testing
    reqs1 = [
        {
            'id': 'REQ-001', 
            'title': 'System shall start', 
            'description': 'The system shall start within 5 seconds', 
            'type': 'functional', 
            'attributes': {'priority': 'high'}
        },
        {
            'id': 'REQ-002', 
            'title': 'System shall stop', 
            'description': 'The system shall stop safely', 
            'type': 'functional', 
            'attributes': {}
        },
    ]
    
    reqs2 = [
        {
            'id': 'REQ-001', 
            'title': 'System shall start quickly', 
            'description': 'The system shall start within 3 seconds', 
            'type': 'functional', 
            'attributes': {'priority': 'critical'}
        },
        {
            'id': 'REQ-003', 
            'title': 'System shall restart', 
            'description': 'The system shall restart after failure', 
            'type': 'functional', 
            'attributes': {}
        },
    ]
    
    # Test comparison
    print("\nTesting comparison...")
    results = comparator.compare_requirements(reqs1, reqs2)
    
    print("Comparison test results:")
    print(f"Added: {len(results['added'])}")
    print(f"Deleted: {len(results['deleted'])}")
    print(f"Modified: {len(results['modified'])}")
    print(f"Unchanged: {len(results['unchanged'])}")
    
    # Test modified entry structure
    if results['modified']:
        mod_req = results['modified'][0]
        print(f"\nModified requirement structure:")
        print(f"ID: {mod_req['id']}")
        print(f"Title: {mod_req['title']}")
        print(f"Changes Summary: {mod_req['changes_summary']}")
        print(f"Change Count: {mod_req['change_count']}")
    
    # Test with comparison profile
    try:
        from comparison_profile import ComparisonProfile
        
        print("\nTesting with comparison profile...")
        profile = ComparisonProfile("Test Profile")
        profile.set_attribute_weight("title", 1.0)
        profile.set_attribute_weight("description", 0.8)
        profile.set_attribute_enabled("type", False)  # Disable type comparison
        
        comparator.set_comparison_profile(profile)
        profile_results = comparator.compare_requirements(reqs1, reqs2)
        
        print("Profile-based comparison results:")
        print(f"Modified: {len(profile_results['modified'])}")
        
        if profile_results['modified']:
            mod_req = profile_results['modified'][0]
            print(f"Changes Summary: {mod_req['changes_summary']}")
            
    except ImportError:
        print("Comparison profile not available for testing")
    
    print("\nReqIF Comparator comprehensive fix completed successfully.")