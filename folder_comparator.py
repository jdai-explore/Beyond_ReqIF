#!/usr/bin/env python3
"""
Enhanced Folder Comparator Module - Phase 1A Integration
Added threading hooks and basic infrastructure while maintaining full backward compatibility
"""

import os
import difflib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import threading
import time

# Original imports
from reqif_comparator import ReqIFComparator
from reqif_parser import ReqIFParser

# New threading infrastructure
from threading.thread_manager import get_thread_manager, execute_parallel_parse, execute_parallel_compare
from threading.task_queue import get_task_scheduler, get_result_collector, TaskPriority
from utils.config import get_threading_config, get_compatibility_config
from utils.compatibility_layer import ensure_compatibility, legacy_progress_adapter, register_fallback


class FolderComparator:
    """
    Enhanced Folder Comparator with threading support and backward compatibility
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
        
        # Configuration
        self.threading_config = get_threading_config()
        self.compatibility_config = get_compatibility_config()
        
        # Statistics (existing + new)
        self.folder_stats = {}
        self.aggregated_req_stats = {}
        self.individual_file_stats = {}
        
        # New: Threading statistics
        self.threading_stats = {
            'threading_used': False,
            'fallback_to_sequential': False,
            'parallel_parse_time': 0.0,
            'parallel_compare_time': 0.0,
            'thread_efficiency': 0.0
        }
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Set progress callback function with legacy support"""
        if self.compatibility_config.legacy_progress_callbacks:
            self.progress_callback = legacy_progress_adapter(callback)
        else:
            self.progress_callback = callback
    
    def set_cancel_flag(self, cancel_flag: threading.Event):
        """Set cancel flag for operation cancellation"""
        self.cancel_flag = cancel_flag
    
    @ensure_compatibility
    def compare_folders(self, folder1_path: str, folder2_path: str, 
                       use_threading: bool = None, bypass_cache: bool = False) -> Dict[str, Any]:
        """
        Compare two folders containing ReqIF files
        Enhanced with threading support while maintaining backward compatibility
        
        Args:
            folder1_path: Path to the first folder (original)
            folder2_path: Path to the second folder (modified)
            use_threading: Override threading setting (None = use config)
            bypass_cache: Bypass cache for this operation (Phase 1A: placeholder)
            
        Returns:
            Dictionary with comprehensive comparison results
        """
        try:
            # Determine if threading should be used
            should_use_threading = self._should_use_threading(use_threading)
            
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
            
            # Analyze file differences with optional threading
            if should_use_threading:
                file_results = self._analyze_file_differences_threaded(file_matches, folder1_path, folder2_path)
            else:
                file_results = self._analyze_file_differences_sequential(file_matches, folder1_path, folder2_path)
            
            # Update progress
            self._update_progress(90, 100, "Compiling results...")
            
            # Calculate comprehensive statistics (existing + enhanced)
            self._calculate_enhanced_statistics(file_results)
            
            # Build final results with enhanced data
            results = {
                'folder1_path': folder1_path,
                'folder2_path': folder2_path,
                'file_results': file_results,
                'folder_statistics': self.folder_stats,
                'aggregated_statistics': self.aggregated_req_stats,
                'individual_file_statistics': self.individual_file_stats,
                'threading_statistics': self.threading_stats,  # New
                'file_matches': file_matches
            }
            
            # Update progress
            self._update_progress(100, 100, "Comparison completed!")
            
            return results
            
        except Exception as e:
            print(f"Error in folder comparison: {e}")
            raise
    
    def _should_use_threading(self, use_threading_override: Optional[bool]) -> bool:
        """Determine if threading should be used for this operation"""
        # Override takes precedence
        if use_threading_override is not None:
            return use_threading_override
        
        # Check configuration
        if not self.threading_config.enabled:
            return False
        
        # Check compatibility settings
        if self.compatibility_config.sequential_fallback and hasattr(self, '_force_sequential'):
            return False
        
        return True
    
    def _analyze_file_differences_threaded(self, file_matches: Dict, folder1_path: str, folder2_path: str) -> Dict[str, Any]:
        """
        NEW: Threaded analysis of file differences using thread pools
        """
        start_time = time.time()
        self.threading_stats['threading_used'] = True
        
        try:
            # Process all matched files (exact + fuzzy)
            all_matches = file_matches['exact_matches'] + file_matches['fuzzy_matches']
            
            if not all_matches:
                return {
                    'matched_files': [],
                    'added_files': file_matches['added_files'],
                    'deleted_files': file_matches['deleted_files'],
                    'comparison_errors': []
                }
            
            # Create parse tasks for all files that need parsing
            parse_tasks = []
            file_parse_map = {}  # Map file path to future index
            
            # Collect all unique files that need parsing
            files_to_parse = set()
            for match in all_matches:
                file1_path = match['file1']['full_path']
                file2_path = match['file2']['full_path']
                files_to_parse.add(file1_path)
                files_to_parse.add(file2_path)
            
            # Create parse tasks
            for i, file_path in enumerate(files_to_parse):
                task = (self._safe_parse_file, (file_path,), {})
                parse_tasks.append(task)
                file_parse_map[file_path] = i
            
            # Execute parsing in parallel
            self._update_progress(25, 100, f"Parsing {len(parse_tasks)} files in parallel...")
            
            def parse_progress_callback(current, total, status):
                progress = 25 + (current / total) * 40  # 25% to 65%
                self._update_progress(int(progress), 100, f"Parsed {current}/{total} files")
            
            parse_results = execute_parallel_parse(parse_tasks, parse_progress_callback)
            
            # Create comparison tasks
            compare_tasks = []
            for match in all_matches:
                file1_path = match['file1']['full_path']
                file2_path = match['file2']['full_path']
                
                # Get parsed results
                file1_result = parse_results[file_parse_map[file1_path]]
                file2_result = parse_results[file_parse_map[file2_path]]
                
                if file1_result is not None and file2_result is not None:
                    task = (self._safe_compare_requirements, (file1_result, file2_result, match), {})
                    compare_tasks.append(task)
            
            # Execute comparisons in parallel
            self._update_progress(65, 100, f"Comparing {len(compare_tasks)} file pairs in parallel...")
            
            def compare_progress_callback(current, total, status):
                progress = 65 + (current / total) * 20  # 65% to 85%
                self._update_progress(int(progress), 100, f"Compared {current}/{total} pairs")
            
            compare_results = execute_parallel_compare(compare_tasks, compare_progress_callback)
            
            # Collect results
            file_results = {
                'matched_files': [r for r in compare_results if r is not None],
                'added_files': file_matches['added_files'],
                'deleted_files': file_matches['deleted_files'],
                'comparison_errors': []
            }
            
            # Initialize individual file statistics for threaded analysis
            self._initialize_individual_stats_threaded(file_results)
            
            # Record threading performance
            self.threading_stats['parallel_parse_time'] = time.time() - start_time
            self.threading_stats['thread_efficiency'] = len(compare_results) / max(1, time.time() - start_time)
            
            return file_results
            
        except Exception as e:
            print(f"Threaded analysis failed, falling back to sequential: {e}")
            register_fallback(f"Threaded file analysis failed: {e}")
            self.threading_stats['fallback_to_sequential'] = True
            return self._analyze_file_differences_sequential(file_matches, folder1_path, folder2_path)
    
    def _analyze_file_differences_sequential(self, file_matches: Dict, folder1_path: str, folder2_path: str) -> Dict[str, Any]:
        """
        EXISTING: Sequential analysis (original implementation with enhancements)
        """
        file_results = {
            'matched_files': [],
            'added_files': file_matches['added_files'],
            'deleted_files': file_matches['deleted_files'],
            'comparison_errors': []
        }
        
        # Initialize individual file statistics
        self.individual_file_stats = {
            'matched_files': {},
            'added_files': {},
            'deleted_files': {}
        }
        
        # Process all matched files (exact + fuzzy) - ORIGINAL LOGIC
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
                
                # Store individual file statistics
                file_key = match['file1']['relative_path']
                self.individual_file_stats['matched_files'][file_key] = {
                    'file1_info': match['file1'],
                    'file2_info': match['file2'],
                    'comparison_stats': comparison_result.get('statistics', {}),
                    'match_type': match['match_type'],
                    'similarity': match['similarity'],
                    'has_changes': self._file_has_changes(comparison_result.get('statistics', {}))
                }
                
            except Exception as e:
                error_info = {
                    'file1': match['file1']['relative_path'],
                    'file2': match['file2']['relative_path'],
                    'error': str(e)
                }
                file_results['comparison_errors'].append(error_info)
                print(f"Error comparing files {match['file1']['relative_path']} and {match['file2']['relative_path']}: {e}")
        
        # Collect statistics for added/deleted files - ENHANCED EXISTING LOGIC
        for file_info in file_matches['added_files']:
            try:
                reqs = self.reqif_parser.parse_file(file_info['full_path'])
                self.individual_file_stats['added_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': len(reqs),
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': True
                }
            except Exception as e:
                self.individual_file_stats['added_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': 0,
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': False,
                    'error': str(e)
                }
        
        for file_info in file_matches['deleted_files']:
            try:
                reqs = self.reqif_parser.parse_file(file_info['full_path'])
                self.individual_file_stats['deleted_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': len(reqs),
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': True
                }
            except Exception as e:
                self.individual_file_stats['deleted_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': 0,
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': False,
                    'error': str(e)
                }
        
        return file_results
    
    def _safe_parse_file(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """Thread-safe file parsing with error handling"""
        try:
            return self.reqif_parser.parse_file(file_path)
        except Exception as e:
            print(f"Parse error for {file_path}: {e}")
            return None
    
    def _safe_compare_requirements(self, file1_reqs: List[Dict[str, Any]], 
                                  file2_reqs: List[Dict[str, Any]], 
                                  match_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Thread-safe requirement comparison with error handling"""
        try:
            comparison_result = self.reqif_comparator.compare_requirements(file1_reqs, file2_reqs)
            
            # Add file metadata
            comparison_result.update({
                'file1_info': match_info['file1'],
                'file2_info': match_info['file2'],
                'match_type': match_info['match_type'],
                'similarity': match_info['similarity']
            })
            
            return comparison_result
        except Exception as e:
            print(f"Compare error for {match_info['file1']['relative_path']}: {e}")
            return None
    
    def _initialize_individual_stats_threaded(self, file_results: Dict[str, Any]):
        """Initialize individual file statistics for threaded results"""
        self.individual_file_stats = {
            'matched_files': {},
            'added_files': {},
            'deleted_files': {}
        }
        
        # Process matched files
        for file_result in file_results['matched_files']:
            if file_result:
                file_key = file_result.get('file1_info', {}).get('relative_path', 'unknown')
                self.individual_file_stats['matched_files'][file_key] = {
                    'file1_info': file_result.get('file1_info', {}),
                    'file2_info': file_result.get('file2_info', {}),
                    'comparison_stats': file_result.get('statistics', {}),
                    'match_type': file_result.get('match_type', 'unknown'),
                    'similarity': file_result.get('similarity', 0),
                    'has_changes': self._file_has_changes(file_result.get('statistics', {}))
                }
        
        # Process added/deleted files (similar to sequential method)
        for file_info in file_results.get('added_files', []):
            try:
                reqs = self.reqif_parser.parse_file(file_info['full_path'])
                self.individual_file_stats['added_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': len(reqs),
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': True
                }
            except Exception as e:
                self.individual_file_stats['added_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': 0,
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': False,
                    'error': str(e)
                }
        
        for file_info in file_results.get('deleted_files', []):
            try:
                reqs = self.reqif_parser.parse_file(file_info['full_path'])
                self.individual_file_stats['deleted_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': len(reqs),
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': True
                }
            except Exception as e:
                self.individual_file_stats['deleted_files'][file_info['relative_path']] = {
                    'file_info': file_info,
                    'requirement_count': 0,
                    'file_size_mb': round(file_info['size'] / (1024 * 1024), 2),
                    'parsing_success': False,
                    'error': str(e)
                }
    
    # ALL EXISTING METHODS REMAIN UNCHANGED
    def _scan_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """Recursively scan folder for ReqIF files with enhanced metadata (UNCHANGED)"""
        reqif_files = []
        
        try:
            folder_path = Path(folder_path)
            
            for file_path in folder_path.rglob('*'):
                if self.cancel_flag.is_set():
                    break
                
                if file_path.is_file() and file_path.suffix.lower() in ['.reqif', '.reqifz']:
                    relative_path = file_path.relative_to(folder_path)
                    
                    file_info = {
                        'full_path': str(file_path),
                        'relative_path': str(relative_path),
                        'filename': file_path.name,
                        'extension': file_path.suffix.lower(),
                        'size': file_path.stat().st_size,
                        'parent_dir': str(relative_path.parent) if relative_path.parent != Path('.') else '',
                        'modified_time': file_path.stat().st_mtime
                    }
                    
                    reqif_files.append(file_info)
            
            print(f"Found {len(reqif_files)} ReqIF files in {folder_path}")
            return reqif_files
            
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
            return []
    
    def _match_files(self, folder1_files: List[Dict], folder2_files: List[Dict]) -> Dict[str, Any]:
        """Match files between two folders using fuzzy matching (UNCHANGED)"""
        matches = {
            'exact_matches': [],
            'fuzzy_matches': [],
            'added_files': [],
            'deleted_files': [],
            'unmatched_folder1': [],
            'unmatched_folder2': []
        }
        
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
                
                if file1['extension'] == file2['extension']:
                    matches['exact_matches'].append({
                        'file1': file1,
                        'file2': file2,
                        'match_type': 'exact',
                        'similarity': 1.0
                    })
                    
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
                if file1['extension'] != file2['extension']:
                    continue
                
                similarity = self._calculate_file_similarity(file1, file2)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = file2
            
            if best_match:
                matches['fuzzy_matches'].append({
                    'file1': file1,
                    'file2': best_match,
                    'match_type': 'fuzzy',
                    'similarity': best_similarity
                })
                
                folder1_remaining.remove(file1)
                folder2_remaining.remove(best_match)
        
        matches['deleted_files'] = folder1_remaining.copy()
        matches['added_files'] = folder2_remaining.copy()
        matches['unmatched_folder1'] = folder1_remaining
        matches['unmatched_folder2'] = folder2_remaining
        
        return matches
    
    def _calculate_file_similarity(self, file1: Dict, file2: Dict) -> float:
        """Calculate similarity between two files based on filename and path (UNCHANGED)"""
        filename_similarity = difflib.SequenceMatcher(
            None, 
            file1['filename'].lower(), 
            file2['filename'].lower()
        ).ratio()
        
        path_similarity = difflib.SequenceMatcher(
            None,
            file1['relative_path'].lower(),
            file2['relative_path'].lower()
        ).ratio()
        
        combined_similarity = (filename_similarity * 0.7) + (path_similarity * 0.3)
        return combined_similarity
    
    def _file_has_changes(self, stats: Dict) -> bool:
        """Check if a file has any changes (UNCHANGED)"""
        return (stats.get('added_count', 0) > 0 or 
                stats.get('deleted_count', 0) > 0 or 
                stats.get('modified_count', 0) > 0)
    
    def _compare_single_file_pair(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """Compare a single pair of ReqIF files (UNCHANGED)"""
        try:
            file1_reqs = self.reqif_parser.parse_file(file1_path)
            file2_reqs = self.reqif_parser.parse_file(file2_path)
            
            comparison_result = self.reqif_comparator.compare_requirements(file1_reqs, file2_reqs)
            
            comparison_result['file1_path'] = file1_path
            comparison_result['file2_path'] = file2_path
            
            return comparison_result
            
        except Exception as e:
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
    
    def _calculate_enhanced_statistics(self, file_results: Dict[str, Any]):
        """Calculate comprehensive folder and aggregated requirement statistics (ENHANCED)"""
        # Existing folder-level statistics
        self.folder_stats = {
            'total_matched_files': len(file_results['matched_files']),
            'files_added': len(file_results['added_files']),
            'files_deleted': len(file_results['deleted_files']),
            'files_with_changes': 0,
            'files_unchanged': 0,
            'comparison_errors': len(file_results['comparison_errors'])
        }
        
        # Existing aggregated requirement statistics
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
            if file_result:  # Handle None results from threading
                stats = file_result.get('statistics', {})
                
                has_changes = self._file_has_changes(stats)
                
                if has_changes:
                    self.folder_stats['files_with_changes'] += 1
                else:
                    self.folder_stats['files_unchanged'] += 1
                
                self.aggregated_req_stats['total_requirements_added'] += stats.get('added_count', 0)
                self.aggregated_req_stats['total_requirements_deleted'] += stats.get('deleted_count', 0)
                self.aggregated_req_stats['total_requirements_modified'] += stats.get('modified_count', 0)
                self.aggregated_req_stats['total_requirements_unchanged'] += stats.get('unchanged_count', 0)
                self.aggregated_req_stats['total_requirements_file1'] += stats.get('total_file1', 0)
                self.aggregated_req_stats['total_requirements_file2'] += stats.get('total_file2', 0)
        
        # Add requirements from added/deleted files to aggregated stats
        for file_path, file_stats in self.individual_file_stats['added_files'].items():
            req_count = file_stats.get('requirement_count', 0)
            self.aggregated_req_stats['total_requirements_added'] += req_count
            self.aggregated_req_stats['total_requirements_file2'] += req_count
        
        for file_path, file_stats in self.individual_file_stats['deleted_files'].items():
            req_count = file_stats.get('requirement_count', 0)
            self.aggregated_req_stats['total_requirements_deleted'] += req_count
            self.aggregated_req_stats['total_requirements_file1'] += req_count
        
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
    
    def _update_progress(self, current: int, maximum: int, status: str):
        """Update progress if callback is set (UNCHANGED)"""
        if self.progress_callback:
            try:
                self.progress_callback(current, maximum, status)
            except Exception as e:
                print(f"Error updating progress: {e}")
    
    def cancel_operation(self):
        """Cancel the current operation (UNCHANGED)"""
        self.cancel_flag.set()
    
    def export_folder_summary_enhanced(self, comparison_results: Dict[str, Any]) -> str:
        """Generate enhanced text summary including threading statistics (ENHANCED)"""
        try:
            folder_stats = comparison_results.get('folder_statistics', {})
            req_stats = comparison_results.get('aggregated_statistics', {})
            individual_stats = comparison_results.get('individual_file_statistics', {})
            threading_stats = comparison_results.get('threading_statistics', {})  # NEW
            
            summary_lines = [
                "Enhanced Folder Comparison Summary (Phase 1A)",
                "=" * 60,
                "",
                "Folder Paths:",
                f"- Original: {comparison_results.get('folder1_path', 'N/A')}",
                f"- Modified: {comparison_results.get('folder2_path', 'N/A')}",
                "",
                "Processing Information:",  # NEW SECTION
                f"- Threading Used: {'Yes' if threading_stats.get('threading_used', False) else 'No'}",
                f"- Fallback to Sequential: {'Yes' if threading_stats.get('fallback_to_sequential', False) else 'No'}",
                f"- Parallel Processing Time: {threading_stats.get('parallel_parse_time', 0):.2f}s",
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
                "=" * 60,
                "INDIVIDUAL FILE STATISTICS",
                "=" * 60,
            ]
            
            # Add individual file statistics (existing logic)
            if individual_stats.get('matched_files'):
                summary_lines.extend([
                    "",
                    f"Matched Files Details ({len(individual_stats['matched_files'])}):",
                    "-" * 40
                ])
                
                for file_path, file_data in individual_stats['matched_files'].items():
                    stats = file_data.get('comparison_stats', {})
                    match_type = file_data.get('match_type', 'unknown')
                    has_changes = file_data.get('has_changes', False)
                    
                    status_icon = "🔄" if has_changes else "✓"
                    summary_lines.append(f"{status_icon} {file_path} ({match_type} match)")
                    
                    if has_changes:
                        changes = []
                        if stats.get('added_count', 0) > 0:
                            changes.append(f"+{stats['added_count']}")
                        if stats.get('deleted_count', 0) > 0:
                            changes.append(f"-{stats['deleted_count']}")
                        if stats.get('modified_count', 0) > 0:
                            changes.append(f"~{stats['modified_count']}")
                        
                        change_summary = ", ".join(changes) if changes else "No changes"
                        change_pct = stats.get('change_percentage', 0)
                        summary_lines.append(f"    Changes: {change_summary} ({change_pct}%)")
                    else:
                        summary_lines.append(f"    No changes detected")
                    
                    file1_size = round(file_data['file1_info']['size'] / (1024 * 1024), 2)
                    file2_size = round(file_data['file2_info']['size'] / (1024 * 1024), 2)
                    summary_lines.append(f"    File sizes: {file1_size}MB → {file2_size}MB")
                    summary_lines.append("")
            
            return '\n'.join(summary_lines)
            
        except Exception as e:
            return f"Error generating enhanced folder summary: {str(e)}"
    
    def export_folder_summary(self, comparison_results: Dict[str, Any]) -> str:
        """Maintain backward compatibility - delegates to enhanced version (UNCHANGED)"""
        return self.export_folder_summary_enhanced(comparison_results)
    
    def get_individual_file_statistics_summary(self, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get a structured summary of individual file statistics (UNCHANGED)"""
        individual_stats = comparison_results.get('individual_file_statistics', {})
        
        summary = {
            'matched_files_count': len(individual_stats.get('matched_files', {})),
            'added_files_count': len(individual_stats.get('added_files', {})),
            'deleted_files_count': len(individual_stats.get('deleted_files', {})),
            'files_with_changes': 0,
            'files_without_changes': 0,
            'total_requirements_in_added_files': 0,
            'total_requirements_in_deleted_files': 0,
            'largest_changed_file': None,
            'parsing_errors': []
        }
        
        # Analyze matched files
        for file_path, file_data in individual_stats.get('matched_files', {}).items():
            if file_data.get('has_changes', False):
                summary['files_with_changes'] += 1
                
                change_pct = file_data.get('comparison_stats', {}).get('change_percentage', 0)
                if (summary['largest_changed_file'] is None or 
                    change_pct > summary['largest_changed_file']['change_percentage']):
                    summary['largest_changed_file'] = {
                        'file_path': file_path,
                        'change_percentage': change_pct,
                        'comparison_stats': file_data.get('comparison_stats', {})
                    }
            else:
                summary['files_without_changes'] += 1
        
        # Analyze added files
        for file_path, file_data in individual_stats.get('added_files', {}).items():
            summary['total_requirements_in_added_files'] += file_data.get('requirement_count', 0)
            if not file_data.get('parsing_success', False):
                summary['parsing_errors'].append({
                    'file_path': file_path,
                    'category': 'added',
                    'error': file_data.get('error', 'Unknown error')
                })
        
        # Analyze deleted files
        for file_path, file_data in individual_stats.get('deleted_files', {}).items():
            summary['total_requirements_in_deleted_files'] += file_data.get('requirement_count', 0)
            if not file_data.get('parsing_success', False):
                summary['parsing_errors'].append({
                    'file_path': file_path,
                    'category': 'deleted',
                    'error': file_data.get('error', 'Unknown error')
                })
        
        return summary
    
    def get_threading_performance_summary(self) -> Dict[str, Any]:
        """NEW: Get threading performance summary"""
        return {
            'threading_config': {
                'enabled': self.threading_config.enabled,
                'parse_threads': self.threading_config.parse_threads,
                'compare_threads': self.threading_config.compare_threads
            },
            'threading_stats': self.threading_stats.copy(),
            'compatibility_mode': {
                'legacy_callbacks': self.compatibility_config.legacy_progress_callbacks,
                'sequential_fallback': self.compatibility_config.sequential_fallback
            }
        }


# Example usage and testing
if __name__ == "__main__":
    print("Enhanced Folder Comparator - Phase 1A Implementation")
    print("Features: Threading hooks, backward compatibility, individual file statistics")
    
    # Test the enhanced folder comparator
    def test_enhanced_folder_comparator():
        comparator = FolderComparator(max_files=50)
        
        # Example progress callback
        def progress_callback(current, maximum, status):
            print(f"Progress: {current}/{maximum} - {status}")
        
        comparator.set_progress_callback(progress_callback)
        
        print(f"Threading enabled: {comparator.threading_config.enabled}")
        print(f"Parse threads: {comparator.threading_config.parse_threads}")
        print("Enhanced Folder Comparator ready for Phase 1A testing!")
    
    test_enhanced_folder_comparator()