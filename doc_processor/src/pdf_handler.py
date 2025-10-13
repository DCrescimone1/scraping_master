"""PDF and XML file validation and handling."""

import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict


class PDFHandler:
    """Validates and prepares PDF and XML files for processing."""
    
    def __init__(self):
        """Initialize file handler for PDF and XML files."""
        pass
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.pdf', '.xml'}
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that input is either a valid local PDF/XML file or a PDF/XML URL.
        
        Args:
            file_path: Path to PDF or XML file
            
        Returns:
        """
        try:
            # URL case
            if isinstance(file_path, str) and (file_path.startswith("http://") or file_path.startswith("https://")):
                parsed = urlparse(file_path)
                # Basic sanity: must have netloc and path ending with supported extension
                if not parsed.netloc:
                    print(f"❌ Invalid URL: {file_path}")
                    return False
                path_lower = parsed.path.lower()
                if not any(path_lower.endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
                    print(f"❌ URL does not point to a supported file (PDF or XML): {file_path}")
                    return False
                return True

            # Local file case
            path = Path(file_path)

            # Check exists
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return False

            # Check is file (not directory)
            if not path.is_file():
                print(f"❌ Not a file: {file_path}")
                return False

            # Check supported extension
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                print(f"❌ Not a supported file type (PDF or XML): {file_path}")
                return False

            # Check readable
            if not os.access(file_path, os.R_OK):
                print(f"❌ File not readable: {file_path}")
                return False

            return True

        except Exception as e:
            print(f"❌ Error validating file: {e}")
            return False

    def get_file_type(self, file_path: str) -> str:
        """
        Determine file type (pdf or xml).
        
        Args:
            file_path: Path to file or URL
            
        Returns:
            'pdf' or 'xml' or 'unknown'
        """
        try:
            if isinstance(file_path, str) and (file_path.startswith("http://") or file_path.startswith("https://")):
                parsed = urlparse(file_path)
                path_lower = parsed.path.lower()
            else:
                path_lower = str(file_path).lower()
            
            if path_lower.endswith('.pdf'):
                return 'pdf'
            elif path_lower.endswith('.xml'):
                return 'xml'
            else:
                return 'unknown'
        except Exception:
            return 'unknown'
    
    def get_file_info(self, file_path: str) -> Dict[str, object]:
        """
        Extract file metadata for local PDF/XML or URL.
        
        Args:
            file_path: Path to PDF or XML file
            
        Returns:
            Dict with file info
        """
        try:
            file_type = self.get_file_type(file_path)
            # URL case
            if isinstance(file_path, str) and (file_path.startswith("http://") or file_path.startswith("https://")):
                parsed = urlparse(file_path)
                # Derive filename from URL path
                name = Path(parsed.path).name or f"document.{file_type}"
                return {
                    "filename": name,
                    "file_path": file_path,
                    "size_mb": 0,
                    "file_type": file_type
                }
            
            # Local file case
            path = Path(file_path)
            size_mb = path.stat().st_size / (1024 * 1024)
            
            return {
                "filename": path.name,
                "file_path": str(path.absolute()),
                "size_mb": round(size_mb, 2),
                "file_type": file_type
            }
        except Exception as e:
            print(f"⚠️  Error getting file info: {e}")
            return {
                "filename": "unknown",
                "file_path": file_path,
                "size_mb": 0,
                "file_type": "unknown"
            }
