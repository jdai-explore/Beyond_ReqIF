#!/usr/bin/env python3
"""
Enhanced Folder Comparator Module - Updated for Content/Structural Separation
Removed hardcoded field references and added clear distinction between
content modifications and structural differences
"""

import os
import difflib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import threading as thread_module
import time

# Original imports
from reqif_comparator import ReqIFComparator
from reqif_parser import ReqIFParser

# Check for enhanced threading - use fallbacks if not available
try:
    from thread_pools.thread_manager import get_thread_manager, execute_parallel_parse, execute_parallel_compare
    from thread_pools.task_queue import get_task_scheduler, get_result_collector, TaskPriority
    from utils.config import get_threading_config, get_compatibility_config
    ENHANCED_THREADING_AVAILABLE = True
except ImportError:
    print("Enhanced threading not available, using basic threading")
    ENHANCED_THREADING_AVAILABLE = False
    
    # Fallback implementations
    def get_threading_config():
        class BasicConfig:
            def __init__(self):
                self.enabled = True
                self.parse_threads = 4
                self.compare_threads = 2
        return BasicConfig()
    
    def get_compatibility_config():
        class BasicConfig:
            def __init__(self):
                self.sequential_fallback = True
                self.legacy_progress_callbacks = True
        return BasicConfig()


class FolderComparator:
    """
    Enhanced Folder Comparator with content/structural change separation
    """
    
    def __init__(self, max_files: int = 200, similarity_threshold: float = 0.6):
        self.max_files = max_files
        self.similarity_threshold = similarity_threshold
        
        # Initialize components
        self.reqif_parser = ReqIFParser()
        self.reqif_comparator = ReqIFComparator()
        
        # Progress tracking
        self.progress_callback = None
        self.cancel_flag = thread_module.Event()
        
        # Configuration
        self.threading_config = get_threading_config()
        self.compatibility_config = get_compatibility_config()
        
        # Statistics (updated for new categorization)
        self.folder_stats = {}
        self.aggregated_req_stats = {}
        self.individual_file_stats = {}
        
        # Threading statistics
        self.threading_stats = {
            'threading_used': False,
            'fallback_to_sequential': False,
            'parallel_parse_time': 0.0,
            'parallel_compare_time': 0.0,
            'thread_efficiency': 0.0
        }
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Set progress callback function"""
        self.progress_callback = callback
    
    def set_cancel_flag(self, cancel_flag: thread_module.Event):
        """Set cancel flag for operation cancellation"""
        self.cancel_flag = cancel_flag
    
    def compare_folders(self, folder1_path: str, folder2_path: str, 
                       use_threading: bool = None, bypass_cache: bool = False) -> Dict[str, Any]:
        """
        Compare two folders containing ReqIF files with content/structural separation
        
        Args:
            folder1_path: Path to the first folder (original)
            folder2_path: Path to the second folder (modified)
            use_threading: Override threading setting (None = use config)
            bypass_cache: Bypass cache for this operation
            
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
            if should_use_threading and ENHANCED_THREADING_AVAILABLE:
                file_results = self._analyze_file_differences_threaded(file_matches, folder1_path, folder2_path)
            else:
                file_results = self._analyze_file_differences_sequential(file_matches, folder1_path, folder2_path)
            
            # Update progress
            self._update_progress(90, 100, "Compiling results...")
            
            # Calculate comprehensive statistics with new categorization
            self._calculate_enhanced_statistics(file_results)
            
            # Build final results with enhanced data
            results = {
                'folder1_path': folder1_path,
                'folder2_path': folder2_path,
                'file_results': file_results,
                'folder_statistics': self.folder_stats,
                'aggregated_statistics': self.aggregated_req_stats,
                'individual_file_statistics': self.individual_file_stats,
                'threading_statistics': self.threading_stats,
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
        Threaded analysis of file differences using thread pools
        """
        start_time = time.time()
        self.threading_stats['threading_used'] = True
        
        try:
            if not ENHANCED_THREADING_AVAILABLE:
                print("Enhanced threading not available, falling back to sequential")
                return self._analyze_file_differences_sequential(file_matches, folder1_path, folder2_path)
            
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
            self.threading_stats['fallback_to_sequential'] = True
            return self._analyze_file_differences_sequential(file_matches, folder1_path, folder2_path)
    
    def _analyze_file_differences_sequential(self, file_matches: Dict, folder1_path: str, folder2_path: str) -> Dict[str, Any]:
        """
        Sequential analysis with updated categorization
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
                
                # Store individual file statistics with new categorization
                file_key = match['file1']['relative_path']
                self.individual_file_stats['matched_files'][file_key] = {
                    'file1_info': match['file1'],
                    'file2_info': match['file2'],
                    'comparison_stats': comparison_result.get('statistics', {}),
                    'match_type': match['match_type'],
                    'similarity': match['similarity'],
                    'has_content_changes': self._file_has_content_changes(comparison_result.get('statistics', {})),
                    'has_structural_changes': self._file_has_structural_changes(comparison_result.get('statistics', {}))
                }
                
            except Exception as e:
                error_info = {
                    'file1': match['file1']['relative_path'],
                    'file2': match['file2']['relative_path'],
                    'error': str(e)
                }
                file_results['comparison_errors'].append(error_info)
                print(f"Error comparing files {match['file1']['relative_path']} and {match['file2']['relative_path']}: {e}")
        
        # Collect statistics for added/deleted files
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
                stats = file_result.get('statistics', {})
                
                self.individual_file_stats['matched_files'][file_key] = {
                    'file1_info': file_result.get('file1_info', {}),
                    'file2_info': file_result.get('file2_info', {}),
                    'comparison_stats': stats,
                    'match_type': file_result.get('match_type', 'unknown'),
                    'similarity': file_result.get('similarity', 0),
                    'has_content_changes': self._file_has_content_changes(stats),
                    'has_structural_changes': self._file_has_structural_changes(stats)
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
    
    def _file_has_content_changes(self, stats: Dict) -> bool:
        """
        Check if a file has content changes (not just structural)
        """
        try:
            return stats.get('content_modified_count', 0) > 0
        except Exception as e:
            print(f"Error checking content changes: {e}")
            return False
    
    def _file_has_structural_changes(self, stats: Dict) -> bool:
        """
        Check if a file has structural changes only
        """
        try:
            return stats.get('structural_only_count', 0) > 0
        except Exception as e:
            print(f"Error checking structural changes: {e}")
            return False
    
    def _compare_single_file_pair(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """Compare a single pair of ReqIF files"""
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
                'content_modified': [],
                'structural_only': [],
                'unchanged': [],
                'statistics': {
                    'total_file1': 0,
                    'total_file2': 0,
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
                },
                'file1_path': file1_path,
                'file2_path': file2_path,
                'comparison_error': str(e)
            }
    
    def _calculate_enhanced_statistics(self, file_results: Dict[str, Any]):
        """Calculate comprehensive folder and aggregated requirement statistics with new categorization"""
        # Folder-level statistics
        self.folder_stats = {
            'total_matched_files': len(file_results['matched_files']),
            'files_added': len(file_results['added_files']),
            'files_deleted': len(file_results['deleted_files']),
            'files_with_content_changes': 0,
            'files_with_structural_only': 0,
            'files_unchanged': 0,
            'comparison_errors': len(file_results['comparison_errors'])
        }
        
        # Aggregated requirement statistics
        self.aggregated_req_stats = {
            'total_requirements_added': 0,
            'total_requirements_deleted': 0,
            'total_requirements_content_modified': 0,
            'total_requirements_structural_only': 0,
            'total_requirements_unchanged': 0,
            'total_requirements_file1': 0,
            'total_requirements_file2': 0,
            'content_change_percentage': 0.0,
            'overall_change_percentage': 0.0,
            'common_added_fields': {},
            'common_removed_fields': {}
        }
        
        # Process matched files for detailed statistics
        for file_result in file_results['matched_files']:
            if file_result:
                stats = file_result.get('statistics', {})
                
                has_content_changes = self._file_has_content_changes(stats)
                has_structural_changes = self._file_has_structural_changes(stats)
                
                if has_content_changes:
                    self.folder_stats['files_with_content_changes'] += 1
                elif has_structural_changes:
                    self.folder_stats['files_with_structural_only'] += 1
                else:
                    self.folder_stats['files_unchanged'] += 1
                
                # Aggregate requirement counts
                self.aggregated_req_stats['total_requirements_added'] += stats.get('added_count', 0)
                self.aggregated_req_stats['total_requirements_deleted'] += stats.get('deleted_count', 0)
                self.aggregated_req_stats['total_requirements_content_modified'] += stats.get('content_modified_count', 0)
                self.aggregated_req_stats['total_requirements_structural_only'] += stats.get('structural_only_count', 0)
                self.aggregated_req_stats['total_requirements_unchanged'] += stats.get('unchanged_count', 0)
                self.aggregated_req_stats['total_requirements_file1'] += stats.get('total_file1', 0)
                self.aggregated_req_stats['total_requirements_file2'] += stats.get('total_file2', 0)
                
                # Track common field changes
                for field in stats.get('added_fields', []):
                    self.aggregated_req_stats['common_added_fields'][field] = \
                        self.aggregated_req_stats['common_added_fields'].get(field, 0) + 1
                
                for field in stats.get('removed_fields', []):
                    self.aggregated_req_stats['common_removed_fields'][field] = \
                        self.aggregated_req_stats['common_removed_fields'].get(field, 0) + 1
        
        # Add requirements from added/deleted files to aggregated stats
        for file_path, file_stats in self.individual_file_stats['added_files'].items():
            req_count = file_stats.get('requirement_count', 0)
            self.aggregated_req_stats['total_requirements_added'] += req_count
            self.aggregated_req_stats['total_requirements_file2'] += req_count
        
        for file_path, file_stats in self.individual_file_stats['deleted_files'].items():
            req_count = file_stats.get('requirement_count', 0)
            self.aggregated_req_stats['total_requirements_deleted'] += req_count
            self.aggregated_req_stats['total_requirements_file1'] += req_count
        
        # Calculate percentages
        total_requirements = (self.aggregated_req_stats['total_requirements_file1'] + 
                             self.aggregated_req_stats['total_requirements_added'])
        
        if total_requirements > 0:
            # Content change percentage (only content modifications)
            content_changes = self.aggregated_req_stats['total_requirements_content_modified']
            self.aggregated_req_stats['content_change_percentage'] = round(
                (content_changes / total_requirements) * 100, 2
            )
            
            # Overall change percentage (all changes except structural-only)
            total_changes = (self.aggregated_req_stats['total_requirements_added'] +
                           self.aggregated_req_stats['total_requirements_deleted'] +
                           self.aggregated_req_stats['total_requirements_content_modified'])
            
            self.aggregated_req_stats['overall_change_percentage'] = round(
                (total_changes / total_requirements) * 100, 2
            )
    
    def _scan_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """Recursively scan folder for ReqIF files with enhanced metadata"""
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
        """Match files between two folders using fuzzy matching"""
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
        """Calculate similarity between two files based on filename and path"""
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
    
    def export_folder_summary_enhanced(self, comparison_results: Dict[str, Any]) -> str:
        """
        Generate enhanced text summary with content/structural separation
        """
        try:
            folder_stats = comparison_results.get('folder_statistics', {})
            req_stats = comparison_results.get('aggregated_statistics', {})
            individual_stats = comparison_results.get('individual_file_statistics', {})
            threading_stats = comparison_results.get('threading_statistics', {})
            
            summary_lines = [
                "Enhanced Folder Comparison Summary - Content/Structural Analysis",
                "=" * 60,
                "",
                "Folder Paths:",
                f"- Original: {comparison_results.get('folder1_path', 'N/A')}",
                f"- Modified: {comparison_results.get('folder2_path', 'N/A')}",
                "",
                "Processing Information:",
                f"- Threading Used: {'Yes' if threading_stats.get('threading_used', False) else 'No'}",
                f"- Fallback to Sequential: {'Yes' if threading_stats.get('fallback_to_sequential', False) else 'No'}",
                f"- Parallel Processing Time: {threading_stats.get('parallel_parse_time', 0):.2f}s",
                "",
                "File-Level Changes:",
                f"- Files Added: {folder_stats.get('files_added', 0)}",
                f"- Files Deleted: {folder_stats.get('files_deleted', 0)}",
                f"- Files with Content Changes: {folder_stats.get('files_with_content_changes', 0)}",
                f"- Files with Structural Changes Only: {folder_stats.get('files_with_structural_only', 0)}",
                f"- Files Unchanged: {folder_stats.get('files_unchanged', 0)}",
                f"- Comparison Errors: {folder_stats.get('comparison_errors', 0)}",
                "",
                "Aggregated Requirement Changes:",
                f"- Requirements Added: {req_stats.get('total_requirements_added', 0)}",
                f"- Requirements Deleted: {req_stats.get('total_requirements_deleted', 0)}",
                f"- Requirements with Content Changes: {req_stats.get('total_requirements_content_modified', 0)}",
                f"- Requirements with Structural Changes Only: {req_stats.get('total_requirements_structural_only', 0)}",
                f"- Requirements Unchanged: {req_stats.get('total_requirements_unchanged', 0)}",
                "",
                f"Content Change Rate: {req_stats.get('content_change_percentage', 0)}%",
                f"Overall Change Rate: {req_stats.get('overall_change_percentage', 0)}%",
                "",
                "Common Structural Changes:",
            ]
            
            # Add common field changes
            common_added = req_stats.get('common_added_fields', {})
            common_removed = req_stats.get('common_removed_fields', {})
            
            if common_added:
                top_added = sorted(common_added.items(), key=lambda x: x[1], reverse=True)[:5]
                summary_lines.append("- Most Common Added Fields:")
                for field, count in top_added:
                    summary_lines.append(f"    {field}: {count} files")
            else:
                summary_lines.append("- No fields commonly added")
            
            if common_removed:
                top_removed = sorted(common_removed.items(), key=lambda x: x[1], reverse=True)[:5]
                summary_lines.append("- Most Common Removed Fields:")
                for field, count in top_removed:
                    summary_lines.append(f"    {field}: {count} files")
            else:
                summary_lines.append("- No fields commonly removed")
            
            summary_lines.extend([
                "",
                "=" * 60,
                "INDIVIDUAL FILE STATISTICS",
                "=" * 60,
            ])
            
            # Add individual file statistics
            if individual_stats.get('matched_files'):
                summary_lines.extend([
                    "",
                    f"Matched Files Details ({len(individual_stats['matched_files'])}):",
                    "-" * 40
                ])
                
                for file_path, file_data in individual_stats['matched_files'].items():
                    stats = file_data.get('comparison_stats', {})
                    match_type = file_data.get('match_type', 'unknown')
                    has_content_changes = file_data.get('has_content_changes', False)
                    has_structural_changes = file_data.get('has_structural_changes', False)
                    
                    if has_content_changes:
                        status_icon = "🔄"
                        status_text = "Content Changes"
                    elif has_structural_changes:
                        status_icon = "📋"
                        status_text = "Structural Only"
                    else:
                        status_icon = "✓"
                        status_text = "Unchanged"
                    
                    summary_lines.append(f"{status_icon} {file_path} ({match_type} match) - {status_text}")
                    
                    if has_content_changes:
                        content_count = stats.get('content_modified_count', 0)
                        added = stats.get('added_count', 0)
                        deleted = stats.get('deleted_count', 0)
                        change_pct = stats.get('content_change_percentage', 0)
                        summary_lines.append(f"    Content: {content_count} modified, +{added}, -{deleted} ({change_pct}%)")
                    
                    if has_structural_changes:
                        structural_count = stats.get('structural_only_count', 0)
                        added_fields = stats.get('added_fields', [])
                        removed_fields = stats.get('removed_fields', [])
                        summary_lines.append(f"    Structure: {structural_count} reqs, +{len(added_fields)} fields, -{len(removed_fields)} fields")
                        if added_fields:
                            summary_lines.append(f"      Added: {', '.join(added_fields[:3])}")
                        if removed_fields:
                            summary_lines.append(f"      Removed: {', '.join(removed_fields[:3])}")
                    
                    # File size information
                    file1_info = file_data.get('file1_info', {})
                    file2_info = file_data.get('file2_info', {})
                    if file1_info.get('size') and file2_info.get('size'):
                        file1_size = round(file1_info['size'] / (1024 * 1024), 2)
                        file2_size = round(file2_info['size'] / (1024 * 1024), 2)
                        summary_lines.append(f"    File sizes: {file1_size}MB → {file2_size}MB")
                    summary_lines.append("")
            
            # Added files section
            if individual_stats.get('added_files'):
                summary_lines.extend([
                    "",
                    f"Added Files Details ({len(individual_stats['added_files'])}):",
                    "-" * 40
                ])
                
                for file_path, file_data in individual_stats['added_files'].items():
                    req_count = file_data.get('requirement_count', 0)
                    file_size = file_data.get('file_size_mb', 0)
                    parsing_success = file_data.get('parsing_success', False)
                    
                    status_icon = "✅" if parsing_success else "❌"
                    summary_lines.append(f"{status_icon} {file_path}")
                    summary_lines.append(f"    Requirements: {req_count}")
                    summary_lines.append(f"    File Size: {file_size}MB")
                    
                    if not parsing_success:
                        error = file_data.get('error', 'Unknown error')
                        summary_lines.append(f"    Error: {error}")
                    summary_lines.append("")
            
            # Deleted files section
            if individual_stats.get('deleted_files'):
                summary_lines.extend([
                    "",
                    f"Deleted Files Details ({len(individual_stats['deleted_files'])}):",
                    "-" * 40
                ])
                
                for file_path, file_data in individual_stats['deleted_files'].items():
                    req_count = file_data.get('requirement_count', 0)
                    file_size = file_data.get('file_size_mb', 0)
                    parsing_success = file_data.get('parsing_success', False)
                    
                    status_icon = "✅" if parsing_success else "❌"
                    summary_lines.append(f"{status_icon} {file_path}")
                    summary_lines.append(f"    Requirements: {req_count}")
                    summary_lines.append(f"    File Size: {file_size}MB")
                    
                    if not parsing_success:
                        error = file_data.get('error', 'Unknown error')
                        summary_lines.append(f"    Error: {error}")
                    summary_lines.append("")
            
            return '\n'.join(summary_lines)
            
        except Exception as e:
            return f"Error generating enhanced folder summary: {str(e)}"
    
    def export_folder_summary(self, comparison_results: Dict[str, Any]) -> str:
        """Maintain compatibility - delegates to enhanced version"""
        return self.export_folder_summary_enhanced(comparison_results)
    
    def get_individual_file_statistics_summary(self, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get a structured summary of individual file statistics with new categorization"""
        individual_stats = comparison_results.get('individual_file_statistics', {})
        
        summary = {
            'matched_files_count': len(individual_stats.get('matched_files', {})),
            'added_files_count': len(individual_stats.get('added_files', {})),
            'deleted_files_count': len(individual_stats.get('deleted_files', {})),
            'files_with_content_changes': 0,
            'files_with_structural_only': 0,
            'files_without_changes': 0,
            'total_requirements_in_added_files': 0,
            'total_requirements_in_deleted_files': 0,
            'largest_content_change_file': None,
            'most_common_structural_changes': [],
            'parsing_errors': []
        }
        
        # Analyze matched files
        for file_path, file_data in individual_stats.get('matched_files', {}).items():
            if file_data.get('has_content_changes', False):
                summary['files_with_content_changes'] += 1
                
                change_pct = file_data.get('comparison_stats', {}).get('content_change_percentage', 0)
                if (summary['largest_content_change_file'] is None or 
                    change_pct > summary['largest_content_change_file']['change_percentage']):
                    summary['largest_content_change_file'] = {
                        'file_path': file_path,
                        'change_percentage': change_pct,
                        'comparison_stats': file_data.get('comparison_stats', {})
                    }
            elif file_data.get('has_structural_changes', False):
                summary['files_with_structural_only'] += 1
            else:
                summary['files_without_changes'] += 1
        
        # Analyze structural patterns
        field_change_counts = {}
        for file_path, file_data in individual_stats.get('matched_files', {}).items():
            stats = file_data.get('comparison_stats', {})
            for field in stats.get('added_fields', []):
                field_change_counts[f"+{field}"] = field_change_counts.get(f"+{field}", 0) + 1
            for field in stats.get('removed_fields', []):
                field_change_counts[f"-{field}"] = field_change_counts.get(f"-{field}", 0) + 1
        
        if field_change_counts:
            summary['most_common_structural_changes'] = sorted(
                field_change_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
        
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
        """Get threading performance summary"""
        return {
            'threading_config': {
                'enabled': self.threading_config.enabled,
                'parse_threads': getattr(self.threading_config, 'parse_threads', 4),
                'compare_threads': getattr(self.threading_config, 'compare_threads', 2)
            },
            'threading_stats': self.threading_stats.copy(),
            'compatibility_mode': {
                'legacy_callbacks': self.compatibility_config.legacy_progress_callbacks,
                'sequential_fallback': self.compatibility_config.sequential_fallback
            }
        }


# Example usage and testing
if __name__ == "__main__":
    print("Enhanced Folder Comparator - Content/Structural Separation")
    print("Features: Clear distinction between content and structural changes")
    
    # Test the enhanced folder comparator
    def test_enhanced_folder_comparator():
        comparator = FolderComparator(max_files=50)
        
        # Example progress callback
        def progress_callback(current, maximum, status):
            print(f"Progress: {current}/{maximum} - {status}")
        
        comparator.set_progress_callback(progress_callback)
        
        print(f"Threading enabled: {comparator.threading_config.enabled}")
        print(f"Parse threads: {getattr(comparator.threading_config, 'parse_threads', 4)}")
        
        # Test file change detection with new categorization
        test_stats = [
            {'content_modified_count': 5, 'structural_only_count': 0},  # Content changes only
            {'content_modified_count': 0, 'structural_only_count': 3},  # Structural only
            {'content_modified_count': 2, 'structural_only_count': 1},  # Both (counts as content)
            {'content_modified_count': 0, 'structural_only_count': 0},  # No changes
        ]
        
        print("\nTesting change detection:")
        for i, stats in enumerate(test_stats):
            has_content = comparator._file_has_content_changes(stats)
            has_structural = comparator._file_has_structural_changes(stats)
            print(f"Stats {i+1}: Content={has_content}, Structural={has_structural}")
        
        print("\nEnhanced Folder Comparator ready!")
    
    test_enhanced_folder_comparator()