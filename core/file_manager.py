"""
File Manager Module
==================

This module provides comprehensive file I/O operations and management
for the ReqIF Tool Suite. Handles file validation, backup, recovery,
and recent files management.

Classes:
    FileManager: Main file management class
    BackupManager: Handles file backup and recovery
    RecentFilesManager: Manages recent file history
    FileValidator: Validates file formats and integrity
    
Functions:
    validate_file_path: Quick path validation
    get_file_info: Extract file information
    ensure_directory: Ensure directory exists
"""

import os
import shutil
import tempfile
import zipfile
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

# Import project modules
from models.file_info import FileInfo, FileStatus
from utils.logger import get_logger
from utils.config import get_config
from utils.constants import SUPPORTED_FORMATS, MAX_FILE_SIZE, TEMP_DIR_PREFIX

logger = get_logger(__name__)


class FileOperation(Enum):
    """File operation types"""
    READ = "read"
    WRITE = "write"
    COPY = "copy"
    MOVE = "move"
    DELETE = "delete"
    BACKUP = "backup"
    RESTORE = "restore"


class FileError(Exception):
    """Custom exception for file operations"""
    
    def __init__(self, message: str, file_path: str = None, operation: FileOperation = None):
        self.message = message
        self.file_path = file_path
        self.operation = operation
        super().__init__(self.message)
    
    def __str__(self):
        error_msg = self.message
        if self.file_path:
            error_msg += f" (File: {self.file_path}"
            if self.operation:
                error_msg += f", Operation: {self.operation.value}"
            error_msg += ")"
        return error_msg


@dataclass
class FileOperationResult:
    """Result of a file operation"""
    success: bool
    operation: FileOperation
    file_path: str
    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BackupInfo:
    """Information about a backup"""
    original_path: str
    backup_path: str
    timestamp: datetime
    size: int
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class FileValidator:
    """Validates file formats and integrity"""
    
    def __init__(self):
        self.supported_extensions = {'.reqif', '.reqifz'}
        self.magic_numbers = {
            'reqif': [b'<?xml', b'<REQ-IF'],
            'reqifz': [b'PK\x03\x04', b'PK\x05\x06']  # ZIP file signatures
        }
    
    def validate_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Comprehensive file validation
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            Dictionary with validation results
        """
        file_path = Path(file_path)
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'file_info': {},
            'format_detected': None
        }
        
        try:
            # Check if file exists
            if not file_path.exists():
                result['errors'].append(f"File does not exist: {file_path}")
                return result
            
            # Check if it's actually a file
            if not file_path.is_file():
                result['errors'].append(f"Path is not a file: {file_path}")
                return result
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                result['errors'].append("File is empty")
                return result
            
            if file_size > MAX_FILE_SIZE:
                result['warnings'].append(f"File size ({file_size:,} bytes) exceeds recommended maximum")
            
            # Check file extension
            extension = file_path.suffix.lower()
            if extension not in self.supported_extensions:
                result['warnings'].append(f"Unsupported file extension: {extension}")
            
            # Detect file format by content
            format_detected = self._detect_format(file_path)
            result['format_detected'] = format_detected
            
            # Validate format-specific structure
            if format_detected == 'reqif':
                self._validate_reqif_structure(file_path, result)
            elif format_detected == 'reqifz':
                self._validate_reqifz_structure(file_path, result)
            else:
                result['errors'].append("Unable to detect valid ReqIF format")
                return result
            
            # Extract file information
            result['file_info'] = self._extract_file_info(file_path)
            
            # Mark as valid if no errors
            result['valid'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
        
        return result
    
    def _detect_format(self, file_path: Path) -> Optional[str]:
        """Detect file format by examining content"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)  # Read first 1KB
            
            # Check for ZIP format (reqifz)
            if header.startswith(b'PK\x03\x04') or header.startswith(b'PK\x05\x06'):
                return 'reqifz'
            
            # Check for XML format (reqif)
            header_str = header.decode('utf-8', errors='ignore').lower()
            if '<?xml' in header_str and ('req-if' in header_str or 'reqif' in header_str):
                return 'reqif'
            
            return None
            
        except Exception as e:
            logger.warning("Error detecting format for %s: %s", file_path, str(e))
            return None
    
    def _validate_reqif_structure(self, file_path: Path, result: Dict[str, Any]):
        """Validate ReqIF XML structure"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read(4096)  # Read first 4KB for structure check
            
            content_str = content.decode('utf-8', errors='ignore')
            
            # Check for required elements
            required_elements = ['REQ-IF', 'THE-HEADER', 'CORE-CONTENT']
            missing_elements = [elem for elem in required_elements if elem not in content_str]
            
            if missing_elements:
                result['warnings'].append(f"Missing ReqIF elements: {', '.join(missing_elements)}")
            
            # Check for namespace declarations
            if 'xmlns' not in content_str:
                result['warnings'].append("Missing XML namespace declarations")
            
        except Exception as e:
            result['errors'].append(f"Error validating ReqIF structure: {str(e)}")
    
    def _validate_reqifz_structure(self, file_path: Path, result: Dict[str, Any]):
        """Validate ReqIFZ archive structure"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Check for .reqif files
                reqif_files = [f for f in file_list if f.endswith('.reqif')]
                if not reqif_files:
                    result['errors'].append("No .reqif files found in archive")
                    return
                
                if len(reqif_files) > 1:
                    result['warnings'].append(f"Multiple .reqif files found: {len(reqif_files)}")
                
                # Validate the first .reqif file
                with zip_file.open(reqif_files[0]) as reqif_file:
                    content = reqif_file.read(4096)
                    content_str = content.decode('utf-8', errors='ignore')
                    
                    if 'REQ-IF' not in content_str:
                        result['errors'].append("Invalid ReqIF content in archive")
                
        except zipfile.BadZipFile:
            result['errors'].append("Invalid ZIP archive format")
        except Exception as e:
            result['errors'].append(f"Error validating ReqIFZ structure: {str(e)}")
    
    def _extract_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract detailed file information"""
        try:
            stat = file_path.stat()
            
            return {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'accessed': datetime.fromtimestamp(stat.st_atime),
                'permissions': oct(stat.st_mode)[-3:],
                'checksum': self._calculate_checksum(file_path)
            }
        except Exception as e:
            logger.warning("Error extracting file info for %s: %s", file_path, str(e))
            return {}
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""


class BackupManager:
    """Manages file backups and recovery"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or Path(get_config().get_backup_directory())
        self.backup_info_file = self.backup_dir / "backup_info.json"
        self.max_backups_per_file = 5
        self.max_backup_age_days = 30
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing backup info
        self.backup_registry = self._load_backup_registry()
    
    def create_backup(self, file_path: Union[str, Path], 
                     metadata: Dict[str, Any] = None) -> BackupInfo:
        """
        Create a backup of the specified file
        
        Args:
            file_path: Path to file to backup
            metadata: Optional metadata to store with backup
            
        Returns:
            BackupInfo object with backup details
            
        Raises:
            FileError: If backup creation fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileError(f"Cannot backup non-existent file", str(file_path), FileOperation.BACKUP)
        
        try:
            # Generate unique backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
            backup_path = self.backup_dir / backup_filename
            
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            
            # Calculate checksum
            validator = FileValidator()
            checksum = validator._calculate_checksum(file_path)
            
            # Create backup info
            backup_info = BackupInfo(
                original_path=str(file_path),
                backup_path=str(backup_path),
                timestamp=datetime.now(),
                size=file_path.stat().st_size,
                checksum=checksum,
                metadata=metadata or {}
            )
            
            # Register backup
            self._register_backup(backup_info)
            
            # Cleanup old backups
            self._cleanup_old_backups(str(file_path))
            
            logger.info("Created backup: %s -> %s", file_path, backup_path)
            return backup_info
            
        except Exception as e:
            raise FileError(f"Backup creation failed: {str(e)}", str(file_path), FileOperation.BACKUP)
    
    def restore_backup(self, backup_info: BackupInfo, 
                      target_path: Optional[Union[str, Path]] = None) -> FileOperationResult:
        """
        Restore a file from backup
        
        Args:
            backup_info: BackupInfo object describing the backup
            target_path: Optional target path (defaults to original path)
            
        Returns:
            FileOperationResult with operation status
        """
        backup_path = Path(backup_info.backup_path)
        target_path = Path(target_path or backup_info.original_path)
        
        try:
            if not backup_path.exists():
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.RESTORE,
                    file_path=str(target_path),
                    error=f"Backup file not found: {backup_path}"
                )
            
            # Verify backup integrity
            validator = FileValidator()
            current_checksum = validator._calculate_checksum(backup_path)
            if current_checksum != backup_info.checksum:
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.RESTORE,
                    file_path=str(target_path),
                    error="Backup file integrity check failed"
                )
            
            # Create backup of existing file if it exists
            if target_path.exists():
                self.create_backup(target_path, {"reason": "pre_restore_backup"})
            
            # Restore file
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, target_path)
            
            logger.info("Restored backup: %s -> %s", backup_path, target_path)
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.RESTORE,
                file_path=str(target_path),
                message=f"Successfully restored from backup created at {backup_info.timestamp}"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                operation=FileOperation.RESTORE,
                file_path=str(target_path),
                error=f"Restore failed: {str(e)}"
            )
    
    def list_backups(self, file_path: Optional[Union[str, Path]] = None) -> List[BackupInfo]:
        """
        List available backups
        
        Args:
            file_path: Optional file path to filter backups
            
        Returns:
            List of BackupInfo objects
        """
        backups = []
        
        for original_path, backup_list in self.backup_registry.items():
            if file_path is None or str(file_path) == original_path:
                for backup_data in backup_list:
                    backups.append(BackupInfo(**backup_data))
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups
    
    def delete_backup(self, backup_info: BackupInfo) -> bool:
        """
        Delete a specific backup
        
        Args:
            backup_info: BackupInfo object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_info.backup_path)
            if backup_path.exists():
                backup_path.unlink()
            
            # Remove from registry
            self._unregister_backup(backup_info)
            
            logger.info("Deleted backup: %s", backup_path)
            return True
            
        except Exception as e:
            logger.error("Failed to delete backup %s: %s", backup_info.backup_path, str(e))
            return False
    
    def _register_backup(self, backup_info: BackupInfo):
        """Register backup in the registry"""
        original_path = backup_info.original_path
        
        if original_path not in self.backup_registry:
            self.backup_registry[original_path] = []
        
        backup_data = {
            'original_path': backup_info.original_path,
            'backup_path': backup_info.backup_path,
            'timestamp': backup_info.timestamp.isoformat(),
            'size': backup_info.size,
            'checksum': backup_info.checksum,
            'metadata': backup_info.metadata
        }
        
        self.backup_registry[original_path].append(backup_data)
        self._save_backup_registry()
    
    def _unregister_backup(self, backup_info: BackupInfo):
        """Remove backup from registry"""
        original_path = backup_info.original_path
        
        if original_path in self.backup_registry:
            self.backup_registry[original_path] = [
                backup for backup in self.backup_registry[original_path]
                if backup['backup_path'] != backup_info.backup_path
            ]
            
            # Remove empty entries
            if not self.backup_registry[original_path]:
                del self.backup_registry[original_path]
            
            self._save_backup_registry()
    
    def _cleanup_old_backups(self, original_path: str):
        """Clean up old backups for a file"""
        if original_path not in self.backup_registry:
            return
        
        backups = self.backup_registry[original_path]
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: datetime.fromisoformat(x['timestamp']), reverse=True)
        
        # Remove excess backups
        if len(backups) > self.max_backups_per_file:
            excess_backups = backups[self.max_backups_per_file:]
            for backup_data in excess_backups:
                backup_info = BackupInfo(**{
                    **backup_data,
                    'timestamp': datetime.fromisoformat(backup_data['timestamp'])
                })
                self.delete_backup(backup_info)
        
        # Remove old backups
        cutoff_date = datetime.now() - timedelta(days=self.max_backup_age_days)
        old_backups = [
            backup for backup in backups
            if datetime.fromisoformat(backup['timestamp']) < cutoff_date
        ]
        
        for backup_data in old_backups:
            backup_info = BackupInfo(**{
                **backup_data,
                'timestamp': datetime.fromisoformat(backup_data['timestamp'])
            })
            self.delete_backup(backup_info)
    
    def _load_backup_registry(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load backup registry from disk"""
        try:
            if self.backup_info_file.exists():
                with open(self.backup_info_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning("Failed to load backup registry: %s", str(e))
        
        return {}
    
    def _save_backup_registry(self):
        """Save backup registry to disk"""
        try:
            with open(self.backup_info_file, 'w') as f:
                json.dump(self.backup_registry, f, indent=2, default=str)
        except Exception as e:
            logger.error("Failed to save backup registry: %s", str(e))


class RecentFilesManager:
    """Manages recent file history"""
    
    def __init__(self, max_recent_files: int = 10):
        self.max_recent_files = max_recent_files
        self.recent_files_file = Path(get_config().get_user_data_dir()) / "recent_files.json"
        self.recent_files = self._load_recent_files()
    
    def add_recent_file(self, file_path: Union[str, Path], 
                       metadata: Dict[str, Any] = None):
        """
        Add a file to recent files list
        
        Args:
            file_path: Path to the file
            metadata: Optional metadata about the file
        """
        file_path = str(Path(file_path).resolve())
        
        # Remove if already exists
        self.recent_files = [rf for rf in self.recent_files if rf['path'] != file_path]
        
        # Add to beginning
        recent_file = {
            'path': file_path,
            'accessed': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.recent_files.insert(0, recent_file)
        
        # Limit list size
        self.recent_files = self.recent_files[:self.max_recent_files]
        
        # Save to disk
        self._save_recent_files()
    
    def get_recent_files(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get list of recent files
        
        Args:
            limit: Optional limit on number of files to return
            
        Returns:
            List of recent file dictionaries
        """
        files = self.recent_files[:limit] if limit else self.recent_files
        
        # Filter out files that no longer exist
        valid_files = []
        for file_info in files:
            if Path(file_info['path']).exists():
                valid_files.append(file_info)
        
        # Update list if any files were removed
        if len(valid_files) != len(files):
            self.recent_files = valid_files
            self._save_recent_files()
        
        return valid_files
    
    def remove_recent_file(self, file_path: Union[str, Path]):
        """Remove a file from recent files list"""
        file_path = str(Path(file_path).resolve())
        self.recent_files = [rf for rf in self.recent_files if rf['path'] != file_path]
        self._save_recent_files()
    
    def clear_recent_files(self):
        """Clear all recent files"""
        self.recent_files = []
        self._save_recent_files()
    
    def _load_recent_files(self) -> List[Dict[str, Any]]:
        """Load recent files from disk"""
        try:
            if self.recent_files_file.exists():
                with open(self.recent_files_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning("Failed to load recent files: %s", str(e))
        
        return []
    
    def _save_recent_files(self):
        """Save recent files to disk"""
        try:
            # Ensure directory exists
            self.recent_files_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.recent_files_file, 'w') as f:
                json.dump(self.recent_files, f, indent=2)
        except Exception as e:
            logger.error("Failed to save recent files: %s", str(e))


class FileManager:
    """
    Main File Manager
    
    Provides comprehensive file management capabilities including:
    - File validation and integrity checking
    - Backup and recovery operations
    - Recent files management
    - Temporary file handling
    - Safe file operations with rollback
    """
    
    def __init__(self):
        self.validator = FileValidator()
        self.backup_manager = BackupManager()
        self.recent_files_manager = RecentFilesManager()
        self.temp_files = []  # Track temporary files for cleanup
        
        logger.info("File Manager initialized")
    
    def validate_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a ReqIF file
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            Validation result dictionary
        """
        return self.validator.validate_file(file_path)
    
    def safe_read_file(self, file_path: Union[str, Path]) -> FileOperationResult:
        """
        Safely read a file with validation and error handling
        
        Args:
            file_path: Path to file to read
            
        Returns:
            FileOperationResult with operation status
        """
        file_path = Path(file_path)
        
        try:
            # Validate file first
            validation = self.validate_file(file_path)
            if not validation['valid']:
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.READ,
                    file_path=str(file_path),
                    error=f"File validation failed: {'; '.join(validation['errors'])}"
                )
            
            # Add to recent files
            self.recent_files_manager.add_recent_file(file_path, validation['file_info'])
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.READ,
                file_path=str(file_path),
                message="File read successfully",
                metadata=validation['file_info']
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                operation=FileOperation.READ,
                file_path=str(file_path),
                error=f"Read operation failed: {str(e)}"
            )
    
    def safe_write_file(self, file_path: Union[str, Path], content: bytes,
                       create_backup: bool = True) -> FileOperationResult:
        """
        Safely write to a file with backup and rollback capability
        
        Args:
            file_path: Path to file to write
            content: Content to write
            create_backup: Whether to create backup before writing
            
        Returns:
            FileOperationResult with operation status
        """
        file_path = Path(file_path)
        backup_info = None
        
        try:
            # Create backup if file exists and backup requested
            if file_path.exists() and create_backup:
                backup_info = self.backup_manager.create_backup(
                    file_path, 
                    {"reason": "pre_write_backup"}
                )
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first
            temp_file = file_path.with_suffix(file_path.suffix + '.tmp')
            self.temp_files.append(temp_file)
            
            with open(temp_file, 'wb') as f:
                f.write(content)
            
            # Atomic move to final location
            shutil.move(temp_file, file_path)
            if temp_file in self.temp_files:
                self.temp_files.remove(temp_file)
            
            # Validate written file
            validation = self.validate_file(file_path)
            if not validation['valid']:
                # Rollback if validation fails
                if backup_info:
                    self.backup_manager.restore_backup(backup_info)
                    return FileOperationResult(
                        success=False,
                        operation=FileOperation.WRITE,
                        file_path=str(file_path),
                        error=f"Written file validation failed, restored backup: {'; '.join(validation['errors'])}"
                    )
                else:
                    file_path.unlink()  # Remove invalid file
                    return FileOperationResult(
                        success=False,
                        operation=FileOperation.WRITE,
                        file_path=str(file_path),
                        error=f"Written file validation failed: {'; '.join(validation['errors'])}"
                    )
            
            # Add to recent files
            self.recent_files_manager.add_recent_file(file_path, validation['file_info'])
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.WRITE,
                file_path=str(file_path),
                message="File written successfully",
                metadata=validation['file_info']
            )
            
        except Exception as e:
            # Rollback on error
            if backup_info:
                try:
                    self.backup_manager.restore_backup(backup_info)
                except:
                    pass  # Best effort rollback
            
            return FileOperationResult(
                success=False,
                operation=FileOperation.WRITE,
                file_path=str(file_path),
                error=f"Write operation failed: {str(e)}"
            )
    
    def copy_file(self, source_path: Union[str, Path], 
                 target_path: Union[str, Path]) -> FileOperationResult:
        """
        Copy a file with validation
        
        Args:
            source_path: Source file path
            target_path: Target file path
            
        Returns:
            FileOperationResult with operation status
        """
        source_path = Path(source_path)
        target_path = Path(target_path)
        
        try:
            # Validate source file
            validation = self.validate_file(source_path)
            if not validation['valid']:
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.COPY,
                    file_path=str(target_path),
                    error=f"Source file validation failed: {'; '.join(validation['errors'])}"
                )
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform copy
            shutil.copy2(source_path, target_path)
            
            # Validate copied file
            target_validation = self.validate_file(target_path)
            if not target_validation['valid']:
                target_path.unlink()  # Remove invalid copy
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.COPY,
                    file_path=str(target_path),
                    error=f"Copied file validation failed: {'; '.join(target_validation['errors'])}"
                )
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.COPY,
                file_path=str(target_path),
                message=f"File copied successfully from {source_path}",
                metadata=target_validation['file_info']
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                operation=FileOperation.COPY,
                file_path=str(target_path),
                error=f"Copy operation failed: {str(e)}"
            )
    
    def move_file(self, source_path: Union[str, Path], 
                 target_path: Union[str, Path],
                 create_backup: bool = True) -> FileOperationResult:
        """
        Move a file with backup and validation
        
        Args:
            source_path: Source file path
            target_path: Target file path
            create_backup: Whether to create backup before moving
            
        Returns:
            FileOperationResult with operation status
        """
        source_path = Path(source_path)
        target_path = Path(target_path)
        backup_info = None
        
        try:
            # Validate source file
            validation = self.validate_file(source_path)
            if not validation['valid']:
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.MOVE,
                    file_path=str(target_path),
                    error=f"Source file validation failed: {'; '.join(validation['errors'])}"
                )
            
            # Create backup if target exists
            if target_path.exists() and create_backup:
                backup_info = self.backup_manager.create_backup(
                    target_path, 
                    {"reason": "pre_move_backup"}
                )
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform move
            shutil.move(source_path, target_path)
            
            # Validate moved file
            target_validation = self.validate_file(target_path)
            if not target_validation['valid']:
                # Rollback - move back to source
                shutil.move(target_path, source_path)
                if backup_info:
                    self.backup_manager.restore_backup(backup_info)
                
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.MOVE,
                    file_path=str(target_path),
                    error=f"Moved file validation failed, operation rolled back: {'; '.join(target_validation['errors'])}"
                )
            
            # Update recent files
            self.recent_files_manager.remove_recent_file(source_path)
            self.recent_files_manager.add_recent_file(target_path, target_validation['file_info'])
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.MOVE,
                file_path=str(target_path),
                message=f"File moved successfully from {source_path}",
                metadata=target_validation['file_info']
            )
            
        except Exception as e:
            # Best effort rollback
            if backup_info:
                try:
                    self.backup_manager.restore_backup(backup_info)
                except:
                    pass
            
            return FileOperationResult(
                success=False,
                operation=FileOperation.MOVE,
                file_path=str(target_path),
                error=f"Move operation failed: {str(e)}"
            )
    
    def delete_file(self, file_path: Union[str, Path],
                   create_backup: bool = True) -> FileOperationResult:
        """
        Delete a file with optional backup
        
        Args:
            file_path: Path to file to delete
            create_backup: Whether to create backup before deletion
            
        Returns:
            FileOperationResult with operation status
        """
        file_path = Path(file_path)
        
        try:
            if not file_path.exists():
                return FileOperationResult(
                    success=False,
                    operation=FileOperation.DELETE,
                    file_path=str(file_path),
                    error="File does not exist"
                )
            
            # Create backup before deletion
            backup_info = None
            if create_backup:
                backup_info = self.backup_manager.create_backup(
                    file_path, 
                    {"reason": "pre_delete_backup"}
                )
            
            # Delete file
            file_path.unlink()
            
            # Remove from recent files
            self.recent_files_manager.remove_recent_file(file_path)
            
            return FileOperationResult(
                success=True,
                operation=FileOperation.DELETE,
                file_path=str(file_path),
                message="File deleted successfully" + (f" (backup created)" if backup_info else ""),
                metadata={"backup_created": backup_info is not None}
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                operation=FileOperation.DELETE,
                file_path=str(file_path),
                error=f"Delete operation failed: {str(e)}"
            )
    
    def create_temporary_file(self, suffix: str = '.tmp', 
                            prefix: str = TEMP_DIR_PREFIX) -> Path:
        """
        Create a temporary file
        
        Args:
            suffix: File suffix
            prefix: File prefix
            
        Returns:
            Path to temporary file
        """
        try:
            temp_file = Path(tempfile.mktemp(suffix=suffix, prefix=prefix))
            self.temp_files.append(temp_file)
            return temp_file
        except Exception as e:
            logger.error("Failed to create temporary file: %s", str(e))
            raise FileError(f"Temporary file creation failed: {str(e)}")
    
    def cleanup_temporary_files(self):
        """Clean up all tracked temporary files"""
        cleaned_count = 0
        for temp_file in self.temp_files[:]:  # Copy list to avoid modification during iteration
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    cleaned_count += 1
                self.temp_files.remove(temp_file)
            except Exception as e:
                logger.warning("Failed to cleanup temp file %s: %s", temp_file, str(e))
        
        if cleaned_count > 0:
            logger.info("Cleaned up %d temporary files", cleaned_count)
    
    def get_file_info(self, file_path: Union[str, Path]) -> FileInfo:
        """
        Get comprehensive file information
        
        Args:
            file_path: Path to file
            
        Returns:
            FileInfo object with detailed information
        """
        file_path = Path(file_path)
        
        try:
            # Basic file info
            stat = file_path.stat()
            
            file_info = FileInfo(
                path=str(file_path),
                name=file_path.name,
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_ctime),
                modified=datetime.fromtimestamp(stat.st_mtime),
                accessed=datetime.fromtimestamp(stat.st_atime)
            )
            
            # Determine format
            if file_path.suffix.lower() == '.reqifz':
                file_info.format = 'reqifz'
            elif file_path.suffix.lower() == '.reqif':
                file_info.format = 'reqif'
            else:
                file_info.format = 'unknown'
            
            # Set status based on validation
            validation = self.validate_file(file_path)
            if validation['valid']:
                file_info.status = FileStatus.VALID
            elif validation['errors']:
                file_info.status = FileStatus.INVALID
            else:
                file_info.status = FileStatus.WARNING
            
            # Add validation details
            file_info.validation_errors = validation['errors']
            file_info.validation_warnings = validation['warnings']
            
            # Calculate checksum
            file_info.checksum = self.validator._calculate_checksum(file_path)
            
            return file_info
            
        except Exception as e:
            # Return minimal info on error
            return FileInfo(
                path=str(file_path),
                name=file_path.name,
                status=FileStatus.ERROR,
                validation_errors=[f"Error reading file info: {str(e)}"]
            )
    
    def get_recent_files(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent files list"""
        return self.recent_files_manager.get_recent_files(limit)
    
    def add_recent_file(self, file_path: Union[str, Path]):
        """Add file to recent files"""
        self.recent_files_manager.add_recent_file(file_path)
    
    def create_backup(self, file_path: Union[str, Path]) -> BackupInfo:
        """Create backup of file"""
        return self.backup_manager.create_backup(file_path)
    
    def list_backups(self, file_path: Optional[Union[str, Path]] = None) -> List[BackupInfo]:
        """List available backups"""
        return self.backup_manager.list_backups(file_path)
    
    def restore_backup(self, backup_info: BackupInfo) -> FileOperationResult:
        """Restore file from backup"""
        return self.backup_manager.restore_backup(backup_info)
    
    def cleanup(self):
        """Cleanup resources and temporary files"""
        self.cleanup_temporary_files()
        logger.info("File Manager cleanup completed")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during cleanup


# Utility functions

def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Quick file path validation
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if path is valid ReqIF file
    """
    try:
        path = Path(file_path)
        return (path.exists() and 
                path.is_file() and 
                path.suffix.lower() in {'.reqif', '.reqifz'})
    except:
        return False


def get_file_info(file_path: Union[str, Path]) -> Optional[FileInfo]:
    """
    Get file information utility function
    
    Args:
        file_path: Path to file
        
    Returns:
        FileInfo object or None if error
    """
    try:
        manager = FileManager()
        return manager.get_file_info(file_path)
    except Exception as e:
        logger.error("Error getting file info for %s: %s", file_path, str(e))
        return None


def ensure_directory(dir_path: Union[str, Path]) -> bool:
    """
    Ensure directory exists
    
    Args:
        dir_path: Directory path to create
        
    Returns:
        True if directory exists or was created
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error("Failed to create directory %s: %s", dir_path, str(e))
        return False


def calculate_directory_size(dir_path: Union[str, Path]) -> int:
    """
    Calculate total size of directory
    
    Args:
        dir_path: Directory path
        
    Returns:
        Total size in bytes
    """
    try:
        total_size = 0
        for file_path in Path(dir_path).rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    except Exception as e:
        logger.error("Error calculating directory size for %s: %s", dir_path, str(e))
        return 0


def find_reqif_files(directory: Union[str, Path], recursive: bool = True) -> List[Path]:
    """
    Find all ReqIF files in directory
    
    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of ReqIF file paths
    """
    try:
        directory = Path(directory)
        files = []
        
        pattern = '**/*' if recursive else '*'
        
        for ext in ['.reqif', '.reqifz']:
            if recursive:
                files.extend(directory.glob(f'**/*{ext}'))
            else:
                files.extend(directory.glob(f'*{ext}'))
        
        return sorted(files)
        
    except Exception as e:
        logger.error("Error finding ReqIF files in %s: %s", directory, str(e))
        return []