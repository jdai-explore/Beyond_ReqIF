#!/usr/bin/env python3
"""
Folder Comparator Module
Handles folder-to-folder comparison with file matching and aggregated statistics
"""

import os
import difflib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import threading
from reqif_comparator import ReqIFComparator
from reqif_parser import ReqIFParser


class FolderComparator:
    """
    Compares two folders containing ReqIF files and provides comprehensive analysis
    """
    
    def __init__(self, max_files: int = 200, similarity_threshold: float = 0.6):
        self.max_files = max_files
        self.similarity_threshold = similarity_threshold
        
        # Initialize components
        self.reqif_parser = ReqIFParser()
        self.reqif_comparator = ReqIFComparator()
        
        # Progress tracking
        self.progress_callback = None
        self.cancel_flag = threading.Event()
        
        # Statistics
        self.folder_stats = {}
        self.aggregated_req_stats = {}
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Set progress callback function"""
        self.progress_callback = callback
    
    def set_cancel_flag(self, cancel_flag: threading.Event):
        """Set cancel flag for operation cancellation"""
        self.cancel_flag = cancel_flag
    
    def compare_folders(self, folder1_path: str, folder2_path: str) -> Dict[str, Any]:
        """
        Compare two folders containing ReqIF files
        
        Args:
            folder1_path: Path to the first folder (original)
            folder2_path: Path to the second folder (modified)
            
        Returns:
            Dictionary with comprehensive comparison results
        """
        try:
            # Validate folders
            if not os.path.exists(folder1_path) or not os.path.isdir(folder1_path):
                raise ValueError(f"Folder 1 does not exist or is not a directory: {folder1_path}")
            
            if not os.path.exists(folder2_path) or not os.path.isdir(folder2_path):
                raise ValueError(f"Folder 2 does not exist or is not a directory: {folder2_path}")
            
            # Update progress
            self._update_progress(0, 100, "Scanning folders...")
            
            # Scan both folders
            folder1_files = self._scan_folder(folder1_path)
            folder2_files = self._scan_folder(folder2_path)
            
            # Check file limit
            total_files = len(folder1_files) + len(folder2_files)
            if total_files > self.max_files:
                raise ValueError(f"Too many files to process: {total_files}. Maximum allowed: {self.max_files}")
            
            # Update progress
            self._update_progress(10, 100, "Matching files...")
            
            # Match files between folders
            file_matches = self._match_files(folder1_files, folder2_files)
            
            # Update progress
            self._update_progress(20, 100, "Analyzing file differences...")
            
            # Analyze file differences
            file_results = self._analyze_file_differences(file_matches, folder1_path, folder2_path)
            
            # Update progress
            self._update_progress(90, 100, "Compiling results...")
            
            # Calculate comprehensive statistics
            self._calculate_folder_statistics(file_results)
            
            # Build final results
            results = {
                'folder1_path': folder1_path,
                'folder2_path': folder2_path,
                'file_results': file_results,
                'folder_statistics': self.folder_stats,
                'aggregated_statistics': self.aggregated_req_stats,
                'file_matches': file_matches
            }
            
            # Update progress
            self._update_progress(100, 100, "Comparison completed!")
            
            return results
            
        except Exception as e:
            print(f"Error in folder comparison: {e}")
            raise
    
    def _scan_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Recursively scan folder for ReqIF files
        
        Args:
            folder_path: Path to folder to scan
            
        Returns:
            List of file information dictionaries
        """
        reqif_files = []
        
        try:
            folder_path = Path(folder_path)
            
            # Recursively find ReqIF files
            for file_path in folder_path.rglob('*'):
                if self.cancel_flag.is_set():
                    break
                
                if file_path.is_file() and file_path.suffix.lower() in ['.reqif', '.reqifz']:
                    # Calculate relative path from base folder
                    relative_path = file_path.relative_to(folder_path)
                    
                    file_info = {
                        'full_path': str(file_path),
                        'relative_path': str(relative_path),
                        'filename': file_path.name,
                        'extension': file_path.suffix.lower(),
                        'size': file_path.stat().st_size,
                        'parent_dir': str(relative_path.parent) if relative_path.parent != Path('.') else ''
                    }
                    
                    reqif_files.append(file_info)
            
            print(f"Found {len(reqif_files)} ReqIF files in {folder_path}")
            return reqif_files
            
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
            return []
    
    def _match_files(self, folder1_files: List[Dict], folder2_files: List[Dict]) -> Dict[str, Any]:
        """
        Match files between two folders using fuzzy matching
        
        Args:
            folder1_files: Files from folder 1
            folder2_files: Files from folder 2
            
        Returns:
            Dictionary containing file matches and categorization
        """
        matches = {
            'exact_matches': [],      # Files with same relative path
            'fuzzy_matches': [],      # Files matched by similarity
            'added_files': [],        # Files only in folder 2
            'deleted_files': [],      # Files only in folder 1
            'unmatched_folder1': [],  # Unmatched files from folder 1
            'unmatched_folder2': []   # Unmatched files from folder 2
        }
        
        # Create lookup dictionaries
        folder1_by_path = {f['relative_path']: f for f in folder1_files}
        folder2_by_path = {f['relative_path']: f for f in folder2_files}
        
        folder1_remaining = folder1_files.copy()
        folder2_remaining = folder2_files.copy()
        
        # First pass: Exact path matches
        for file1 in folder1_files:
            if self.cancel_flag.is_set():
                break
                
            rel_path = file1['relative_path']
            if rel_path in folder2_by_path:
                file2 = folder2_by_path[rel_path]
                
                # Verify same extension
                if file1['extension'] == file2['extension']:
                    matches['exact_matches'].append({
                        'file1': file1,
                        'file2': file2,
                        'match_type': 'exact',
                        'similarity': 1.0
                    })
                    
                    # Remove from remaining
                    if file1 in folder1_remaining:
                        folder1_remaining.remove(file1)
                    if file2 in folder2_remaining:
                        folder2_remaining.remove(file2)
        
        # Second pass: Fuzzy matching for remaining files
        for file1 in folder1_remaining.copy():
            if self.cancel_flag.is_set():
                break
                
            best_match = None
            best_similarity = 0
            
            for file2 in folder2_remaining:
                # Only match files with same extension
                if file1['extension'] != file2['extension']:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_file_similarity(file1, file2)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = file2
            
            # If good match found, add to fuzzy matches
            if best_match:
                matches['fuzzy_matches'].append({
                    'file1': file1,
                    'file2': best_match,
                    'match_type': 'fuzzy',
                    'similarity': best_similarity
                })
                
                # Remove from remaining
                folder1_remaining.remove(file1)
                folder2_remaining.remove(best_match)
        
        # Remaining files are added/deleted
        matches['deleted_files'] = folder1_remaining.copy()
        matches['added_files'] = folder2_remaining.copy()
        matches['unmatched_folder1'] = folder1_remaining
        matches['unmatched_folder2'] = folder2_remaining
        
        return matches
    
    def _calculate_file_similarity(self, file1: Dict, file2: Dict) -> float:
        """
        Calculate similarity between two files based on filename and path
        
        Args:
            file1: First file info
            file2: Second file info
            
        Returns:
            Similarity score between 0 and 1
        """
        # Compare filenames
        filename_similarity = difflib.SequenceMatcher(
            None, 
            file1['filename'].lower(), 
            file2['filename'].lower()
        ).ratio()
        
        # Compare relative paths
        path_similarity = difflib.SequenceMatcher(
            None,
            file1['relative_path'].lower(),
            file2['relative_path'].lower()
        ).ratio()
        
        # Weighted combination (filename is more important)
        combined_similarity = (filename_similarity * 0.7) + (path_similarity * 0.3)
        
        return combined_similarity
    
    def _analyze_file_differences(self, file_matches: Dict, folder1_path: str, folder2_path: str) -> Dict[str, Any]:
        """
        Analyze differences for matched files
        
        Args:
            file_matches: File matching results
            folder1_path: Base path of folder 1
            folder2_path: Base path of folder 2
            
        Returns:
            Dictionary with file comparison results
        """
        file_results = {
            'matched_files': [],
            'added_files': file_matches['added_files'],
            'deleted_files': file_matches['deleted_files'],
            'comparison_errors': []
        }
        
        # Process all matched files (exact + fuzzy)
        all_matches = file_matches['exact_matches'] + file_matches['fuzzy_matches']
        total_matches = len(all_matches)
        
        for i, match in enumerate(all_matches):
            if self.cancel_flag.is_set():
                break
            
            # Update progress
            progress = 20 + (i / max(total_matches, 1)) * 70  # 20% to 90%
            file1_name = match['file1']['filename']
            self._update_progress(int(progress), 100, f"Comparing {file1_name}...")
            
            try:
                # Compare the two files
                comparison_result = self._compare_single_file_pair(
                    match['file1']['full_path'],
                    match['file2']['full_path']
                )
                
                # Add file metadata
                comparison_result.update({
                    'file1_info': match['file1'],
                    'file2_info': match['file2'],
                    'match_type': match['match_type'],
                    'similarity': match['similarity']
                })
                
                file_results['matched_files'].append(comparison_result)
                
            except Exception as e:
                error_info = {
                    'file1': match['file1']['relative_path'],
                    'file2': match['file2']['relative_path'],
                    'error': str(e)
                }
                file_results['comparison_errors'].append(error_info)
                print(f"Error comparing files {match['file1']['relative_path']} and {match['file2']['relative_path']}: {e}")
        
        return file_results
    
    def _compare_single_file_pair(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """
        Compare a single pair of ReqIF files
        
        Args:
            file1_path: Path to first file
            file2_path: Path to second file
            
        Returns:
            Comparison results dictionary
        """
        try:
            # Parse both files
            file1_reqs = self.reqif_parser.parse_file(file1_path)
            file2_reqs = self.reqif_parser.parse_file(file2_path)
            
            # Compare requirements
            comparison_result = self.reqif_comparator.compare_requirements(file1_reqs, file2_reqs)
            
            # Add file paths to result
            comparison_result['file1_path'] = file1_path
            comparison_result['file2_path'] = file2_path
            
            return comparison_result
            
        except Exception as e:
            # Return empty comparison result for failed comparisons
            return {
                'added': [],
                'deleted': [],
                'modified': [],
                'unchanged': [],
                'statistics': {
                    'total_file1': 0,
                    'total_file2': 0,
                    'total_unique': 0,
                    'added_count': 0,
                    'deleted_count': 0,
                    'modified_count': 0,
                    'unchanged_count': 0,
                    'change_percentage': 0.0
                },
                'file1_path': file1_path,
                'file2_path': file2_path,
                'comparison_error': str(e)
            }
    
    def _calculate_folder_statistics(self, file_results: Dict[str, Any]):
        """
        Calculate comprehensive folder and aggregated requirement statistics
        
        Args:
            file_results: File comparison results
        """
        # Folder-level statistics
        self.folder_stats = {
            'total_matched_files': len(file_results['matched_files']),
            'files_added': len(file_results['added_files']),
            'files_deleted': len(file_results['deleted_files']),
            'files_with_changes': 0,
            'files_unchanged': 0,
            'comparison_errors': len(file_results['comparison_errors'])
        }
        
        # Aggregated requirement statistics
        self.aggregated_req_stats = {
            'total_requirements_added': 0,
            'total_requirements_deleted': 0,
            'total_requirements_modified': 0,
            'total_requirements_unchanged': 0,
            'total_requirements_file1': 0,
            'total_requirements_file2': 0,
            'overall_change_percentage': 0.0
        }
        
        # Process matched files for detailed statistics
        for file_result in file_results['matched_files']:
            stats = file_result.get('statistics', {})
            
            # Check if file has changes
            has_changes = (stats.get('added_count', 0) > 0 or 
                          stats.get('deleted_count', 0) > 0 or 
                          stats.get('modified_count', 0) > 0)
            
            if has_changes:
                self.folder_stats['files_with_changes'] += 1
            else:
                self.folder_stats['files_unchanged'] += 1
            
            # Aggregate requirement statistics
            self.aggregated_req_stats['total_requirements_added'] += stats.get('added_count', 0)
            self.aggregated_req_stats['total_requirements_deleted'] += stats.get('deleted_count', 0)
            self.aggregated_req_stats['total_requirements_modified'] += stats.get('modified_count', 0)
            self.aggregated_req_stats['total_requirements_unchanged'] += stats.get('unchanged_count', 0)
            self.aggregated_req_stats['total_requirements_file1'] += stats.get('total_file1', 0)
            self.aggregated_req_stats['total_requirements_file2'] += stats.get('total_file2', 0)
        
        # Calculate overall change percentage
        total_requirements = (self.aggregated_req_stats['total_requirements_file1'] + 
                             self.aggregated_req_stats['total_requirements_added'])
        
        if total_requirements > 0:
            total_changes = (self.aggregated_req_stats['total_requirements_added'] +
                           self.aggregated_req_stats['total_requirements_deleted'] +
                           self.aggregated_req_stats['total_requirements_modified'])
            
            self.aggregated_req_stats['overall_change_percentage'] = round(
                (total_changes / total_requirements) * 100, 2
            )
        
        # Add files from added/deleted to folder stats
        # Note: Added/deleted files contribute to requirement counts
        for added_file in file_results['added_files']:
            try:
                # Parse added file to get requirement count
                reqs = self.reqif_parser.parse_file(added_file['full_path'])
                self.aggregated_req_stats['total_requirements_added'] += len(reqs)
                self.aggregated_req_stats['total_requirements_file2'] += len(reqs)
            except:
                pass  # Skip files that can't be parsed
        
        for deleted_file in file_results['deleted_files']:
            try:
                # Parse deleted file to get requirement count
                reqs = self.reqif_parser.parse_file(deleted_file['full_path'])
                self.aggregated_req_stats['total_requirements_deleted'] += len(reqs)
                self.aggregated_req_stats['total_requirements_file1'] += len(reqs)
            except:
                pass  # Skip files that can't be parsed
        
        # Recalculate overall change percentage with file additions/deletions
        total_requirements = (self.aggregated_req_stats['total_requirements_file1'] + 
                             len(file_results['added_files']))
        
        if total_requirements > 0:
            total_changes = (self.aggregated_req_stats['total_requirements_added'] +
                           self.aggregated_req_stats['total_requirements_deleted'] +
                           self.aggregated_req_stats['total_requirements_modified'])
            
            self.aggregated_req_stats['overall_change_percentage'] = round(
                (total_changes / total_requirements) * 100, 2
            )
    
    def _update_progress(self, current: int, maximum: int, status: str):
        """Update progress if callback is set"""
        if self.progress_callback:
            try:
                self.progress_callback(current, maximum, status)
            except Exception as e:
                print(f"Error updating progress: {e}")
    
    def cancel_operation(self):
        """Cancel the current operation"""
        self.cancel_flag.set()
    
    def export_folder_summary(self, comparison_results: Dict[str, Any]) -> str:
        """
        Generate a text summary of folder comparison results
        
        Args:
            comparison_results: Folder comparison results
            
        Returns:
            Text summary string
        """
        try:
            folder_stats = comparison_results.get('folder_statistics', {})
            req_stats = comparison_results.get('aggregated_statistics', {})
            
            summary_lines = [
                "Folder Comparison Summary",
                "=" * 50,
                "",
                "Folder Paths:",
                f"- Original: {comparison_results.get('folder1_path', 'N/A')}",
                f"- Modified: {comparison_results.get('folder2_path', 'N/A')}",
                "",
                "File-Level Changes:",
                f"- Files Added: {folder_stats.get('files_added', 0)}",
                f"- Files Deleted: {folder_stats.get('files_deleted', 0)}",
                f"- Files Modified: {folder_stats.get('files_with_changes', 0)}",
                f"- Files Unchanged: {folder_stats.get('files_unchanged', 0)}",
                f"- Comparison Errors: {folder_stats.get('comparison_errors', 0)}",
                "",
                "Aggregated Requirement Changes:",
                f"- Requirements Added: {req_stats.get('total_requirements_added', 0)}",
                f"- Requirements Deleted: {req_stats.get('total_requirements_deleted', 0)}",
                f"- Requirements Modified: {req_stats.get('total_requirements_modified', 0)}",
                f"- Requirements Unchanged: {req_stats.get('total_requirements_unchanged', 0)}",
                "",
                f"Overall Change Rate: {req_stats.get('overall_change_percentage', 0)}%",
                "",
                "File Details:",
            ]
            
            # Add file-level details
            file_results = comparison_results.get('file_results', {})
            
            # Added files
            added_files = file_results.get('added_files', [])
            if added_files:
                summary_lines.extend([
                    "",
                    f"Added Files ({len(added_files)}):"
                ])
                for file_info in added_files[:10]:  # Show first 10
                    summary_lines.append(f"  + {file_info['relative_path']}")
                if len(added_files) > 10:
                    summary_lines.append(f"  ... and {len(added_files) - 10} more")
            
            # Deleted files
            deleted_files = file_results.get('deleted_files', [])
            if deleted_files:
                summary_lines.extend([
                    "",
                    f"Deleted Files ({len(deleted_files)}):"
                ])
                for file_info in deleted_files[:10]:  # Show first 10
                    summary_lines.append(f"  - {file_info['relative_path']}")
                if len(deleted_files) > 10:
                    summary_lines.append(f"  ... and {len(deleted_files) - 10} more")
            
            # Modified files
            matched_files = file_results.get('matched_files', [])
            modified_files = [f for f in matched_files if f.get('statistics', {}).get('change_percentage', 0) > 0]
            if modified_files:
                summary_lines.extend([
                    "",
                    f"Modified Files ({len(modified_files)}):"
                ])
                for file_result in modified_files[:10]:  # Show first 10
                    file1_info = file_result.get('file1_info', {})
                    stats = file_result.get('statistics', {})
                    change_pct = stats.get('change_percentage', 0)
                    summary_lines.append(f"  ~ {file1_info.get('relative_path', 'Unknown')} ({change_pct}% changed)")
                if len(modified_files) > 10:
                    summary_lines.append(f"  ... and {len(modified_files) - 10} more")
            
            return '\n'.join(summary_lines)
            
        except Exception as e:
            return f"Error generating folder summary: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    print("Folder Comparator - Testing Module")
    
    # Test the folder comparator
    def test_folder_comparator():
        comparator = FolderComparator(max_files=50)
        
        # Example progress callback
        def progress_callback(current, maximum, status):
            print(f"Progress: {current}/{maximum} - {status}")
        
        comparator.set_progress_callback(progress_callback)
        
        # Note: In real usage, you would provide actual folder paths
        # results = comparator.compare_folders("folder1_path", "folder2_path")
        # print("Comparison completed!")
        
    print("Folder Comparator initialized successfully!")