"""PDF file validation and handling."""

import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict


class PDFHandler:
    """Validates and prepares PDF files for processing."""
    
    def __init__(self):
        """Initialize PDF handler."""
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that input is either a valid local PDF file or a PDF URL.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # URL case
            if isinstance(file_path, str) and (file_path.startswith("http://") or file_path.startswith("https://")):
                parsed = urlparse(file_path)
                # Basic sanity: must have netloc and path ending with .pdf
                if not parsed.netloc:
                    print(f"❌ Invalid URL: {file_path}")
                    return False
                if not parsed.path.lower().endswith('.pdf'):
                    print(f"❌ URL does not point to a PDF: {file_path}")
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

            # Check PDF extension
            if path.suffix.lower() != '.pdf':
                print(f"❌ Not a PDF file: {file_path}")
                return False

            # Check readable
            if not os.access(file_path, os.R_OK):
                print(f"❌ File not readable: {file_path}")
                return False

            return True

        except Exception as e:
            print(f"❌ Error validating file: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, object]:
        """
        Extract file metadata for local PDF or URL.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with file info
        """
        try:
            # URL case
            if isinstance(file_path, str) and (file_path.startswith("http://") or file_path.startswith("https://")):
                parsed = urlparse(file_path)
                # Derive filename from URL path
                name = Path(parsed.path).name or "document.pdf"
                return {
                    "filename": name,
                    "file_path": file_path,
                    "size_mb": 0
                }

            # Local file case
            path = Path(file_path)
            size_mb = path.stat().st_size / (1024 * 1024)

            return {
                "filename": path.name,
                "file_path": str(path.absolute()),
                "size_mb": round(size_mb, 2)
            }
        except Exception as e:
            print(f"⚠️  Error getting file info: {e}")
            return {
                "filename": "unknown",
                "file_path": file_path,
                "size_mb": 0
            }
