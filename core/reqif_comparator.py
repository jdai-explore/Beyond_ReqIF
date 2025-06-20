"""
ReqIF Comparator Module
======================

This module provides comprehensive comparison capabilities for ReqIF files.
Supports file-to-file and folder-to-folder comparisons with intelligent
matching algorithms and detailed difference analysis.

Classes:
    ReqIFComparator: Main comparison engine
    ComparisonStrategy: Strategy pattern for different comparison approaches
    MatchingAlgorithm: Algorithm for matching requirements between files
    
Functions:
    quick_compare: Fast comparison for basic differences
    deep_compare: Detailed comparison with attribute analysis
"""

import os
import difflib
import filecmp
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# Import project modules
from .reqif_parser import ReqIFParser, ParsingError
from models.requirement import Requirement
from models.comparison_result import ComparisonResult, ChangeType, RequirementDifference
from utils.logger import get_logger
from utils.helpers import calculate_text_similarity, normalize_text

logger = get_logger(__name__)


class ComparisonMode(Enum):
    """Comparison mode enumeration"""
    BASIC = "basic"
    DETAILED = "detailed"
    FUZZY = "fuzzy"
    STRUCTURAL = "structural"


class MatchingStrategy(Enum):
    """Strategy for matching requirements between files"""
    ID_ONLY = "id_only"
    ID_AND_TEXT = "id_and_text"
    FUZZY_MATCHING = "fuzzy_matching"
    CONTENT_BASED = "content_based"


@dataclass
class ComparisonOptions:
    """Configuration options for comparison"""
    mode: ComparisonMode = ComparisonMode.DETAILED
    matching_strategy: MatchingStrategy = MatchingStrategy.ID_ONLY
    ignore_whitespace: bool = False
    case_sensitive: bool = True
    similarity_threshold: float = 0.8
    include_attributes: bool = True
    include_metadata: bool = False
    max_diff_lines: int = 1000


@dataclass
class ComparisonStats:
    """Statistics from comparison operation"""
    total_requirements_file1: int
    total_requirements_file2: int
    added_count: int
    modified_count: int
    deleted_count: int
    unchanged_count: int
    comparison_time: float
    files_compared: int
    errors_encountered: int


class RequirementMatcher:
    """Handles matching of requirements between files"""
    
    def __init__(self, strategy: MatchingStrategy, options: ComparisonOptions):
        self.strategy = strategy
        self.options = options
        
    def match_requirements(self, reqs1: Dict[str, Requirement], 
                          reqs2: Dict[str, Requirement]) -> Dict[str, Tuple[Optional[Requirement], Optional[Requirement]]]:
        """
        Match requirements between two sets
        
        Returns:
            Dictionary mapping requirement IDs to (req1, req2) tuples
        """
        matches = {}
        
        if self.strategy == MatchingStrategy.ID_ONLY:
            matches = self._match_by_id(reqs1, reqs2)
        elif self.strategy == MatchingStrategy.ID_AND_TEXT:
            matches = self._match_by_id_and_text(reqs1, reqs2)
        elif self.strategy == MatchingStrategy.FUZZY_MATCHING:
            matches = self._match_fuzzy(reqs1, reqs2)
        elif self.strategy == MatchingStrategy.CONTENT_BASED:
            matches = self._match_by_content(reqs1, reqs2)
        
        return matches
    
    def _match_by_id(self, reqs1: Dict[str, Requirement], 
                    reqs2: Dict[str, Requirement]) -> Dict[str, Tuple[Optional[Requirement], Optional[Requirement]]]:
        """Match requirements by ID only"""
        matches = {}
        all_ids = set(reqs1.keys()) | set(reqs2.keys())
        
        for req_id in all_ids:
            req1 = reqs1.get(req_id)
            req2 = reqs2.get(req_id)
            matches[req_id] = (req1, req2)
        
        return matches
    
    def _match_by_id_and_text(self, reqs1: Dict[str, Requirement], 
                             reqs2: Dict[str, Requirement]) -> Dict[str, Tuple[Optional[Requirement], Optional[Requirement]]]:
        """Match requirements by ID first, then by text similarity"""
        matches = {}
        matched_ids = set()
        
        # First pass: exact ID matches
        for req_id in set(reqs1.keys()) & set(reqs2.keys()):
            matches[req_id] = (reqs1[req_id], reqs2[req_id])
            matched_ids.add(req_id)
        
        # Second pass: try to match unmatched requirements by text similarity
        unmatched_1 = {k: v for k, v in reqs1.items() if k not in matched_ids}
        unmatched_2 = {k: v for k, v in reqs2.items() if k not in matched_ids}
        
        for req_id1, req1 in unmatched_1.items():
            best_match = None
            best_similarity = 0
            
            for req_id2, req2 in unmatched_2.items():
                similarity = calculate_text_similarity(req1.text, req2.text)
                if similarity > best_similarity and similarity >= self.options.similarity_threshold:
                    best_similarity = similarity
                    best_match = req_id2
            
            if best_match:
                # Create a combined ID for the match
                combined_id = f"{req_id1}↔{best_match}"
                matches[combined_id] = (req1, unmatched_2[best_match])
                del unmatched_2[best_match]
            else:
                matches[req_id1] = (req1, None)
        
        # Add remaining unmatched from file 2
        for req_id2, req2 in unmatched_2.items():
            matches[req_id2] = (None, req2)
        
        return matches
    
    def _match_fuzzy(self, reqs1: Dict[str, Requirement], 
                    reqs2: Dict[str, Requirement]) -> Dict[str, Tuple[Optional[Requirement], Optional[Requirement]]]:
        """Fuzzy matching based on text similarity"""
        matches = {}
        used_req2_ids = set()
        
        # Calculate similarity matrix
        similarity_matrix = {}
        for req_id1, req1 in reqs1.items():
            for req_id2, req2 in reqs2.items():
                similarity = calculate_text_similarity(req1.text, req2.text)
                similarity_matrix[(req_id1, req_id2)] = similarity
        
        # Find best matches using greedy approach
        sorted_similarities = sorted(similarity_matrix.items(), key=lambda x: x[1], reverse=True)
        
        for (req_id1, req_id2), similarity in sorted_similarities:
            if (req_id1 not in matches and req_id2 not in used_req2_ids and 
                similarity >= self.options.similarity_threshold):
                matches[req_id1] = (reqs1[req_id1], reqs2[req_id2])
                used_req2_ids.add(req_id2)
        
        # Add unmatched requirements
        for req_id1, req1 in reqs1.items():
            if req_id1 not in matches:
                matches[req_id1] = (req1, None)
        
        for req_id2, req2 in reqs2.items():
            if req_id2 not in used_req2_ids:
                matches[req_id2] = (None, req2)
        
        return matches
    
    def _match_by_content(self, reqs1: Dict[str, Requirement], 
                         reqs2: Dict[str, Requirement]) -> Dict[str, Tuple[Optional[Requirement], Optional[Requirement]]]:
        """Match by content hash and attributes"""
        matches = {}
        content_hash_1 = {}
        content_hash_2 = {}
        
        # Create content hashes
        for req_id, req in reqs1.items():
            content_hash = self._create_content_hash(req)
            content_hash_1[content_hash] = req_id
        
        for req_id, req in reqs2.items():
            content_hash = self._create_content_hash(req)
            content_hash_2[content_hash] = req_id
        
        # Match by content hash
        matched_hashes = set()
        for content_hash in set(content_hash_1.keys()) & set(content_hash_2.keys()):
            req_id1 = content_hash_1[content_hash]
            req_id2 = content_hash_2[content_hash]
            matches[req_id1] = (reqs1[req_id1], reqs2[req_id2])
            matched_hashes.add(content_hash)
        
        # Add unmatched requirements
        for content_hash, req_id in content_hash_1.items():
            if content_hash not in matched_hashes:
                matches[req_id] = (reqs1[req_id], None)
        
        for content_hash, req_id in content_hash_2.items():
            if content_hash not in matched_hashes:
                matches[req_id] = (None, reqs2[req_id])
        
        return matches
    
    def _create_content_hash(self, requirement: Requirement) -> str:
        """Create a content hash for a requirement"""
        text = normalize_text(requirement.text) if not self.options.case_sensitive else requirement.text
        if self.options.ignore_whitespace:
            text = ' '.join(text.split())
        
        # Include key attributes in hash
        attr_str = ""
        if self.options.include_attributes:
            sorted_attrs = sorted(requirement.attributes.items())
            attr_str = str(sorted_attrs)
        
        return f"{text}|{attr_str}"


class ReqIFComparator:
    """
    ReqIF File Comparator
    
    Provides comprehensive comparison of ReqIF files with support for:
    - File-to-file comparison
    - Folder-to-folder comparison
    - Multiple matching strategies
    - Detailed difference analysis
    - Performance optimization
    """
    
    def __init__(self, options: ComparisonOptions = None):
        """Initialize the comparator with options"""
        self.options = options or ComparisonOptions()
        self.parser = ReqIFParser()
        logger.info("ReqIF Comparator initialized with mode: %s", self.options.mode.value)
    
    def compare_files(self, file1_path: Union[str, Path], 
                     file2_path: Union[str, Path]) -> ComparisonResult:
        """
        Compare two ReqIF files
        
        Args:
            file1_path: Path to the first ReqIF file
            file2_path: Path to the second ReqIF file
            
        Returns:
            ComparisonResult containing detailed differences
            
        Raises:
            ParsingError: If files cannot be parsed
            FileNotFoundError: If files don't exist
        """
        start_time = datetime.now()
        logger.info("Starting file comparison: %s vs %s", file1_path, file2_path)
        
        try:
            # Parse both files
            result1 = self.parser.parse_file(file1_path)
            result2 = self.parser.parse_file(file2_path)
            
            # Perform comparison
            comparison_result = self._compare_requirements(
                result1.requirements, result2.requirements,
                str(file1_path), str(file2_path)
            )
            
            # Add file information
            comparison_result.file1_info = result1.file_info
            comparison_result.file2_info = result2.file_info
            
            # Calculate statistics
            end_time = datetime.now()
            comparison_result.stats = ComparisonStats(
                total_requirements_file1=len(result1.requirements),
                total_requirements_file2=len(result2.requirements),
                added_count=len(comparison_result.added),
                modified_count=len(comparison_result.modified),
                deleted_count=len(comparison_result.deleted),
                unchanged_count=len(comparison_result.unchanged),
                comparison_time=(end_time - start_time).total_seconds(),
                files_compared=1,
                errors_encountered=len(result1.errors) + len(result2.errors)
            )
            
            logger.info("File comparison completed in %.2f seconds", comparison_result.stats.comparison_time)
            return comparison_result
            
        except Exception as e:
            logger.error("File comparison failed: %s", str(e))
            raise
    
    def compare_folders(self, folder1_path: Union[str, Path], 
                       folder2_path: Union[str, Path]) -> Dict[str, ComparisonResult]:
        """
        Compare two folders containing ReqIF files
        
        Args:
            folder1_path: Path to the first folder
            folder2_path: Path to the second folder
            
        Returns:
            Dictionary mapping filenames to comparison results
        """
        start_time = datetime.now()
        logger.info("Starting folder comparison: %s vs %s", folder1_path, folder2_path)
        
        folder1_path = Path(folder1_path)
        folder2_path = Path(folder2_path)
        
        if not folder1_path.is_dir() or not folder2_path.is_dir():
            raise ValueError("Both paths must be directories")
        
        # Get ReqIF files from both folders
        files1 = self._get_reqif_files(folder1_path)
        files2 = self._get_reqif_files(folder2_path)
        
        all_files = set(files1.keys()) | set(files2.keys())
        results = {}
        total_errors = 0
        
        for filename in all_files:
            try:
                if filename in files1 and filename in files2:
                    # Compare existing files
                    result = self.compare_files(files1[filename], files2[filename])
                    results[filename] = result
                elif filename in files1:
                    # File deleted in folder2
                    result = self._create_deleted_file_result(files1[filename], filename)
                    results[filename] = result
                else:
                    # File added in folder2
                    result = self._create_added_file_result(files2[filename], filename)
                    results[filename] = result
                    
            except Exception as e:
                logger.error("Error comparing file %s: %s", filename, str(e))
                result = self._create_error_result(filename, str(e))
                results[filename] = result
                total_errors += 1
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        logger.info("Folder comparison completed in %.2f seconds (%d files, %d errors)", 
                   total_time, len(all_files), total_errors)
        
        return results
    
    def _compare_requirements(self, reqs1: Dict[str, Requirement], 
                            reqs2: Dict[str, Requirement],
                            file1_path: str, file2_path: str) -> ComparisonResult:
        """Compare two sets of requirements"""
        
        # Initialize result
        result = ComparisonResult(
            file1_path=file1_path,
            file2_path=file2_path,
            comparison_mode=self.options.mode,
            matching_strategy=self.options.matching_strategy
        )
        
        # Match requirements
        matcher = RequirementMatcher(self.options.matching_strategy, self.options)
        matches = matcher.match_requirements(reqs1, reqs2)
        
        # Analyze matches to determine changes
        for match_id, (req1, req2) in matches.items():
            if req1 is None:
                # Added requirement
                result.added[req2.id] = req2
            elif req2 is None:
                # Deleted requirement
                result.deleted[req1.id] = req1
            elif self._requirements_equal(req1, req2):
                # Unchanged requirement
                result.unchanged[req1.id] = req2
            else:
                # Modified requirement
                diff = self._create_requirement_difference(req1, req2)
                result.modified[req1.id] = diff
        
        return result
    
    def _requirements_equal(self, req1: Requirement, req2: Requirement) -> bool:
        """Check if two requirements are equal"""
        if not self.options.case_sensitive:
            text1 = req1.text.lower()
            text2 = req2.text.lower()
        else:
            text1 = req1.text
            text2 = req2.text
        
        if self.options.ignore_whitespace:
            text1 = ' '.join(text1.split())
            text2 = ' '.join(text2.split())
        
        text_equal = text1 == text2
        
        if self.options.include_attributes:
            attrs_equal = req1.attributes == req2.attributes
            return text_equal and attrs_equal
        else:
            return text_equal
    
    def _create_requirement_difference(self, req1: Requirement, req2: Requirement) -> RequirementDifference:
        """Create a detailed difference between two requirements"""
        diff = RequirementDifference(
            old_requirement=req1,
            new_requirement=req2,
            change_type=ChangeType.MODIFIED
        )
        
        # Generate text diff
        if req1.text != req2.text:
            diff.text_diff = self._generate_text_diff(req1.text, req2.text)
        
        # Generate attribute differences
        if self.options.include_attributes:
            diff.attribute_changes = self._compare_attributes(req1.attributes, req2.attributes)
        
        # Calculate similarity score
        diff.similarity_score = calculate_text_similarity(req1.text, req2.text)
        
        return diff
    
    def _generate_text_diff(self, text1: str, text2: str) -> str:
        """Generate unified diff between two texts"""
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        diff_lines = list(difflib.unified_diff(
            lines1, lines2,
            fromfile='old',
            tofile='new',
            lineterm=''
        ))
        
        # Limit diff size
        if len(diff_lines) > self.options.max_diff_lines:
            diff_lines = diff_lines[:self.options.max_diff_lines]
            diff_lines.append("... (diff truncated) ...")
        
        return ''.join(diff_lines)
    
    def _compare_attributes(self, attrs1: Dict[str, Any], attrs2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare attribute dictionaries"""
        changes = {
            'added': {},
            'removed': {},
            'modified': {}
        }
        
        all_keys = set(attrs1.keys()) | set(attrs2.keys())
        
        for key in all_keys:
            if key not in attrs1:
                changes['added'][key] = attrs2[key]
            elif key not in attrs2:
                changes['removed'][key] = attrs1[key]
            elif attrs1[key] != attrs2[key]:
                changes['modified'][key] = {
                    'old': attrs1[key],
                    'new': attrs2[key]
                }
        
        return changes
    
    def _get_reqif_files(self, folder_path: Path) -> Dict[str, Path]:
        """Get all ReqIF files in a folder"""
        files = {}
        
        for ext in ['*.reqif', '*.reqifz']:
            for file_path in folder_path.glob(ext):
                if file_path.is_file():
                    files[file_path.name] = file_path
        
        return files
    
    def _create_deleted_file_result(self, file_path: Path, filename: str) -> ComparisonResult:
        """Create result for a deleted file"""
        try:
            result = self.parser.parse_file(file_path)
            
            comparison_result = ComparisonResult(
                file1_path=str(file_path),
                file2_path="[DELETED]",
                comparison_mode=self.options.mode,
                matching_strategy=self.options.matching_strategy
            )
            
            # All requirements are deleted
            comparison_result.deleted = result.requirements
            comparison_result.file1_info = result.file_info
            
            return comparison_result
            
        except Exception as e:
            return self._create_error_result(filename, f"Error reading deleted file: {str(e)}")
    
    def _create_added_file_result(self, file_path: Path, filename: str) -> ComparisonResult:
        """Create result for an added file"""
        try:
            result = self.parser.parse_file(file_path)
            
            comparison_result = ComparisonResult(
                file1_path="[ADDED]",
                file2_path=str(file_path),
                comparison_mode=self.options.mode,
                matching_strategy=self.options.matching_strategy
            )
            
            # All requirements are added
            comparison_result.added = result.requirements
            comparison_result.file2_info = result.file_info
            
            return comparison_result
            
        except Exception as e:
            return self._create_error_result(filename, f"Error reading added file: {str(e)}")
    
    def _create_error_result(self, filename: str, error_message: str) -> ComparisonResult:
        """Create result for a comparison error"""
        result = ComparisonResult(
            file1_path=filename,
            file2_path=filename,
            comparison_mode=self.options.mode,
            matching_strategy=self.options.matching_strategy
        )
        
        result.errors.append(error_message)
        return result
    
    def quick_compare(self, file1_path: Union[str, Path], 
                     file2_path: Union[str, Path]) -> bool:
        """
        Quick comparison to check if files are different
        
        Args:
            file1_path: Path to first file
            file2_path: Path to second file
            
        Returns:
            True if files are different, False if identical
        """
        try:
            # First check file size and modification time
            if filecmp.cmp(str(file1_path), str(file2_path), shallow=True):
                return False
            
            # If files are different, they need detailed comparison
            return True
            
        except Exception as e:
            logger.warning("Quick compare failed for %s vs %s: %s", 
                          file1_path, file2_path, str(e))
            return True  # Assume different if comparison fails


def quick_compare(file1_path: Union[str, Path], file2_path: Union[str, Path]) -> bool:
    """
    Quick comparison utility function
    
    Args:
        file1_path: Path to first ReqIF file
        file2_path: Path to second ReqIF file
        
    Returns:
        True if files are different
    """
    comparator = ReqIFComparator()
    return comparator.quick_compare(file1_path, file2_path)


def deep_compare(file1_path: Union[str, Path], file2_path: Union[str, Path],
                options: ComparisonOptions = None) -> ComparisonResult:
    """
    Deep comparison utility function
    
    Args:
        file1_path: Path to first ReqIF file
        file2_path: Path to second ReqIF file
        options: Comparison options
        
    Returns:
        Detailed comparison result
    """
    comparator = ReqIFComparator(options)
    return comparator.compare_files(file1_path, file2_path)