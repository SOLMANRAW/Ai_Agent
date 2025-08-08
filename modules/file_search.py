import os
import glob
import fnmatch
from typing import List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileSearch:
    def __init__(self, config):
        self.config = config
        self.search_paths = config.SEARCH_PATHS
        self.max_results = config.MAX_FILE_SEARCH_RESULTS
    
    def search_files(self, query: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Search for files based on query"""
        results = []
        query_lower = query.lower()
        
        # Common file extensions to search
        if file_types is None:
            file_types = ['*']
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
            
            try:
                for file_type in file_types:
                    pattern = os.path.join(search_path, '**', f'*{file_type}')
                    for file_path in glob.glob(pattern, recursive=True):
                        if os.path.isfile(file_path):
                            filename = os.path.basename(file_path)
                            if query_lower in filename.lower():
                                results.append({
                                    'name': filename,
                                    'path': file_path,
                                    'size': os.path.getsize(file_path),
                                    'modified': os.path.getmtime(file_path),
                                    'type': self._get_file_type(file_path)
                                })
                                
                                if len(results) >= self.max_results:
                                    return results
                                    
            except Exception as e:
                logger.error(f"Error searching in {search_path}: {e}")
        
        return results
    
    def search_by_extension(self, extension: str) -> List[Dict[str, Any]]:
        """Search for files by extension"""
        return self.search_files(f"*.{extension}")
    
    def search_recent_files(self, days: int = 7) -> List[Dict[str, Any]]:
        """Search for recently modified files"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        results = []
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
            
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            mtime = os.path.getmtime(file_path)
                            if mtime > cutoff_time:
                                results.append({
                                    'name': file,
                                    'path': file_path,
                                    'size': os.path.getsize(file_path),
                                    'modified': mtime,
                                    'type': self._get_file_type(file_path)
                                })
                                
                                if len(results) >= self.max_results:
                                    return results
                        except OSError:
                            continue
                            
            except Exception as e:
                logger.error(f"Error searching recent files in {search_path}: {e}")
        
        return results
    
    def search_large_files(self, min_size_mb: int = 100) -> List[Dict[str, Any]]:
        """Search for large files"""
        min_size_bytes = min_size_mb * 1024 * 1024
        results = []
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
            
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            if size > min_size_bytes:
                                results.append({
                                    'name': file,
                                    'path': file_path,
                                    'size': size,
                                    'modified': os.path.getmtime(file_path),
                                    'type': self._get_file_type(file_path)
                                })
                                
                                if len(results) >= self.max_results:
                                    return results
                        except OSError:
                            continue
                            
            except Exception as e:
                logger.error(f"Error searching large files in {search_path}: {e}")
        
        return results
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file"""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'type': self._get_file_type(file_path),
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {}
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type based on extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        type_mapping = {
            '.txt': 'text',
            '.pdf': 'document',
            '.doc': 'document',
            '.docx': 'document',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.mp4': 'video',
            '.avi': 'video',
            '.zip': 'archive',
            '.tar': 'archive',
            '.gz': 'archive',
            '.py': 'code',
            '.js': 'code',
            '.html': 'code',
            '.css': 'code',
            '.json': 'data',
            '.csv': 'data',
            '.xlsx': 'spreadsheet',
            '.xls': 'spreadsheet'
        }
        
        return type_mapping.get(ext, 'unknown')
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results as a readable string"""
        if not results:
            return "No files found."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            size_str = self.format_file_size(result['size'])
            formatted_results.append(
                f"{i}. {result['name']} ({size_str}) - {result['path']}"
            )
        
        return "\n".join(formatted_results)



