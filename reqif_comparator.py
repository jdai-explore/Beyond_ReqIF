#!/usr/bin/env python3
"""
ReqIF Comparator Module
Handles comparison logic between two sets of requirements.
"""

from typing import List, Dict, Any, Tuple
import difflib


class ReqIFComparator:
    """Compares two sets of ReqIF requirements and identifies differences"""
    
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
        # Create ID-based lookup dictionaries
        file1_dict = {req['id']: req for req in file1_reqs if req['id']}
        file2_dict = {req['id']: req for req in file2_reqs if req['id']}
        
        # Find all unique IDs
        file1_ids = set(file1_dict.keys())
        file2_ids = set(file2_dict.keys())
        
        # Categorize changes
        added_ids = file2_ids - file1_ids
        deleted_ids = file1_ids - file2_ids
        common_ids = file1_ids & file2_ids
        
        # Process each category
        added = [file2_dict[req_id] for req_id in added_ids]
        deleted = [file1_dict[req_id] for req_id in deleted_ids]
        
        modified = []
        unchanged = []
        
        for req_id in common_ids:
            req1 = file1_dict[req_id]
            req2 = file2_dict[req_id]
            
            if self._requirements_differ(req1, req2):
                # Create a modified entry with both old and new versions
                modified_entry = {
                    'id': req_id,
                    'old': req1,
                    'new': req2,
                    'changes': self._identify_changes(req1, req2)
                }
                modified.append(modified_entry)
            else:
                unchanged.append(req2)  # Use the newer version
        
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
    
    def _requirements_differ(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Check if two requirements are different"""
        # Compare key fields
        if req1.get('title', '') != req2.get('title', ''):
            return True
        if req1.get('description', '') != req2.get('description', ''):
            return True
        if req1.get('type', '') != req2.get('type', ''):
            return True
            
        # Compare attributes
        attrs1 = req1.get('attributes', {})
        attrs2 = req2.get('attributes', {})
        
        # Check if attribute sets are different
        if set(attrs1.keys()) != set(attrs2.keys()):
            return True
            
        # Check if any attribute values differ
        for key in attrs1.keys():
            if attrs1.get(key, '') != attrs2.get(key, ''):
                return True
                
        return False
    
    def _identify_changes(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify specific changes between two requirements"""
        changes = []
        
        # Check title changes
        if req1.get('title', '') != req2.get('title', ''):
            changes.append({
                'field': 'title',
                'old_value': req1.get('title', ''),
                'new_value': req2.get('title', ''),
                'change_type': 'modified'
            })
        
        # Check description changes
        if req1.get('description', '') != req2.get('description', ''):
            changes.append({
                'field': 'description',
                'old_value': req1.get('description', ''),
                'new_value': req2.get('description', ''),
                'change_type': 'modified'
            })
        
        # Check type changes
        if req1.get('type', '') != req2.get('type', ''):
            changes.append({
                'field': 'type',
                'old_value': req1.get('type', ''),
                'new_value': req2.get('type', ''),
                'change_type': 'modified'
            })
        
        # Check attribute changes
        attrs1 = req1.get('attributes', {})
        attrs2 = req2.get('attributes', {})
        
        all_attr_keys = set(attrs1.keys()) | set(attrs2.keys())
        
        for attr_key in all_attr_keys:
            val1 = attrs1.get(attr_key, '')
            val2 = attrs2.get(attr_key, '')
            
            if attr_key not in attrs1:
                changes.append({
                    'field': 'attribute.' + attr_key,
                    'old_value': '',
                    'new_value': val2,
                    'change_type': 'added'
                })
            elif attr_key not in attrs2:
                changes.append({
                    'field': 'attribute.' + attr_key,
                    'old_value': val1,
                    'new_value': '',
                    'change_type': 'deleted'
                })
            elif val1 != val2:
                changes.append({
                    'field': 'attribute.' + attr_key,
                    'old_value': val1,
                    'new_value': val2,
                    'change_type': 'modified'
                })
        
        return changes
    
    def get_text_diff(self, text1: str, text2: str) -> List[str]:
        """Get a unified diff between two text strings"""
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
    
    def calculate_similarity(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> float:
        """Calculate similarity score between two requirements (0.0 to 1.0)"""
        # Simple similarity based on title and description
        title1 = req1.get('title', '').lower()
        title2 = req2.get('title', '').lower()
        desc1 = req1.get('description', '').lower()
        desc2 = req2.get('description', '').lower()
        
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
    
    def find_similar_requirements(self, req: Dict[str, Any], 
                                candidates: List[Dict[str, Any]], 
                                threshold: float = 0.8) -> List[Tuple[Dict[str, Any], float]]:
        """Find requirements similar to the given requirement"""
        similar = []
        
        for candidate in candidates:
            similarity = self.calculate_similarity(req, candidate)
            if similarity >= threshold:
                similar.append((candidate, similarity))
        
        # Sort by similarity (highest first)
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar
    
    def export_comparison_summary(self, comparison_results: Dict[str, Any]) -> str:
        """Generate a text summary of the comparison results"""
        stats = comparison_results['statistics']
        
        # Build summary string step by step
        summary_lines = [
            "ReqIF Comparison Summary",
            "========================",
            "",
            "File Statistics:",
            f"- Original file: {stats['total_file1']} requirements",
            f"- Modified file: {stats['total_file2']} requirements",
            f"- Total unique requirements: {stats['total_unique']}",
            "",
            "Changes Detected:",
            f"- Added: {stats['added_count']} requirements",
            f"- Deleted: {stats['deleted_count']} requirements",
            f"- Modified: {stats['modified_count']} requirements",
            f"- Unchanged: {stats['unchanged_count']} requirements",
            "",
            f"Overall Change Rate: {stats['change_percentage']}%",
            "",
            "Detailed Changes:",
        ]
        
        # Add details for each category
        if comparison_results['added']:
            summary_lines.append("")
            summary_lines.append(f"Added Requirements ({len(comparison_results['added'])}):")
            for req in comparison_results['added'][:5]:  # Show first 5
                title = req.get('title', 'No title')
                summary_lines.append(f"  + {req['id']}: {title}")
            if len(comparison_results['added']) > 5:
                remaining = len(comparison_results['added']) - 5
                summary_lines.append(f"  ... and {remaining} more")
        
        if comparison_results['deleted']:
            summary_lines.append("")
            summary_lines.append(f"Deleted Requirements ({len(comparison_results['deleted'])}):")
            for req in comparison_results['deleted'][:5]:  # Show first 5
                title = req.get('title', 'No title')
                summary_lines.append(f"  - {req['id']}: {title}")
            if len(comparison_results['deleted']) > 5:
                remaining = len(comparison_results['deleted']) - 5
                summary_lines.append(f"  ... and {remaining} more")
        
        if comparison_results['modified']:
            summary_lines.append("")
            summary_lines.append(f"Modified Requirements ({len(comparison_results['modified'])}):")
            for mod in comparison_results['modified'][:5]:  # Show first 5
                title = mod['new'].get('title', 'No title')
                change_count = len(mod['changes'])
                summary_lines.append(f"  ~ {mod['id']}: {title}")
                summary_lines.append(f"    Changes: {change_count} field(s) modified")
            if len(comparison_results['modified']) > 5:
                remaining = len(comparison_results['modified']) - 5
                summary_lines.append(f"  ... and {remaining} more")
        
        return '\n'.join(summary_lines)


# Example usage and testing
if __name__ == "__main__":
    comparator = ReqIFComparator()
    
    # Example requirements for testing
    reqs1 = [
        {
            'id': 'REQ-001', 
            'title': 'System shall start', 
            'description': 'The system shall start within 5 seconds', 
            'type': 'functional', 
            'attributes': {}
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
            'attributes': {}
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
    results = comparator.compare_requirements(reqs1, reqs2)
    
    print("Comparison test results:")
    print(f"Added: {len(results['added'])}")
    print(f"Deleted: {len(results['deleted'])}")
    print(f"Modified: {len(results['modified'])}")
    print(f"Unchanged: {len(results['unchanged'])}")
    
    print("\nReqIF Comparator module loaded successfully.")