import difflib
from pathlib import Path
from reqif_parser import ReqIFParser

class ReqIFComparator:
    """Compares ReqIF files and generates statistics"""
    
    def __init__(self):
        self.parser = ReqIFParser()
    
    def compare_files(self, file1_path, file2_path):
        """Compare two ReqIF files"""
        try:
            reqs1 = self.parser.parse_reqif_file(file1_path)
            reqs2 = self.parser.parse_reqif_file(file2_path)
            
            return self._compare_requirements(reqs1, reqs2)
        except Exception as e:
            raise Exception(f"Error comparing files: {str(e)}")
    
    def compare_folders(self, folder1_path, folder2_path):
        """Compare two folders containing ReqIF files"""
        results = {}
        
        # Get all ReqIF files in both folders
        files1 = self._get_reqif_files(folder1_path)
        files2 = self._get_reqif_files(folder2_path)
        
        all_files = set(files1.keys()) | set(files2.keys())
        
        for filename in all_files:
            if filename in files1 and filename in files2:
                # Compare existing files
                try:
                    result = self.compare_files(files1[filename], files2[filename])
                    results[filename] = result
                except Exception as e:
                    results[filename] = {'error': str(e)}
            elif filename in files1:
                # File only in folder1 (deleted)
                results[filename] = {'status': 'deleted', 'file1': files1[filename]}
            else:
                # File only in folder2 (added)
                results[filename] = {'status': 'added', 'file2': files2[filename]}
        
        return results
    
    def _get_reqif_files(self, folder_path):
        """Get all ReqIF files in a folder"""
        files = {}
        folder = Path(folder_path)
        
        for ext in ['*.reqif', '*.reqifz']:
            for file_path in folder.glob(ext):
                files[file_path.name] = str(file_path)
        
        return files
    
    def _compare_requirements(self, reqs1, reqs2):
        """Compare two sets of requirements"""
        added = {}
        modified = {}
        deleted = {}
        unchanged = {}
        
        all_ids = set(reqs1.keys()) | set(reqs2.keys())
        
        for req_id in all_ids:
            if req_id in reqs1 and req_id in reqs2:
                # Requirement exists in both
                req1 = reqs1[req_id]
                req2 = reqs2[req_id]
                
                if self._requirements_equal(req1, req2):
                    unchanged[req_id] = req2
                else:
                    modified[req_id] = {
                        'old': req1,
                        'new': req2,
                        'diff': self._generate_diff(req1, req2)
                    }
            elif req_id in reqs1:
                # Requirement deleted
                deleted[req_id] = reqs1[req_id]
            else:
                # Requirement added
                added[req_id] = reqs2[req_id]
        
        return {
            'added': added,
            'modified': modified,
            'deleted': deleted,
            'unchanged': unchanged,
            'summary': {
                'added_count': len(added),
                'modified_count': len(modified),
                'deleted_count': len(deleted),
                'unchanged_count': len(unchanged),
                'total_old': len(reqs1),
                'total_new': len(reqs2)
            }
        }
    
    def _requirements_equal(self, req1, req2):
        """Check if two requirements are equal"""
        return (req1.get('text', '') == req2.get('text', '') and 
                req1.get('attributes', {}) == req2.get('attributes', {}))
    
    def _generate_diff(self, req1, req2):
        """Generate a diff between two requirements"""
        text1 = req1.get('text', '')
        text2 = req2.get('text', '')
        
        differ = difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            fromfile='old',
            tofile='new',
            lineterm=''
        )
        
        return ''.join(differ)
