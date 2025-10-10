"""Firecrawl PDF parsing integration."""

from typing import Optional, Dict
from firecrawl import Firecrawl
import fitz  # PyMuPDF

class FirecrawlParser:
    """Handles PDF to text conversion using Firecrawl."""

    def __init__(self, api_key: str):
        """
        Initialize Firecrawl client.

        Args:
            api_key: Firecrawl API key
        """
        if not api_key:
            raise ValueError("Firecrawl API key is required")

        self.firecrawl = Firecrawl(api_key=api_key)

    def _is_url(self, path: str) -> bool:
        """
        Check if input is a URL or local file path.

        Args:
            path: Input path or URL

        Returns:
            True if URL, False if local path
        """
        return path.startswith("http://") or path.startswith("https://")

    def _parse_local_pdf(self, file_path: str) -> Optional[Dict[str, object]]:
        """
        Parse local PDF file using PyMuPDF.

        Args:
            file_path: Path to local PDF file

        Returns:
            Dict with parsed content or None if failed
        """
        try:
            print("📄 Parsing local PDF with PyMuPDF...")

            # Open PDF
            doc = fitz.open(file_path)

            # Extract text from all pages
            markdown_content = ""
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                markdown_content += f"\n\n## Page {page_num}\n\n{text}"

            page_count = len(doc)
            doc.close()

            if not markdown_content or len(markdown_content) < 50:
                print("⚠️  Warning: Extracted content is very short")
                return None

            # Count words
            word_count = len(markdown_content.split())

            print(f"✅ Extracted {word_count:,} words from {page_count} pages")

            return {
                "markdown": markdown_content.strip(),
                "word_count": word_count,
                "page_count": page_count,
                "method": "pymupdf",
            }

        except Exception as e:
            print(f"❌ Error parsing local PDF: {e}")
            return None

    def _parse_url_pdf(self, pdf_url: str) -> Optional[Dict[str, object]]:
        """
        Parse PDF from URL using Firecrawl.

        Args:
            pdf_url: URL to PDF file

        Returns:
            Dict with parsed content or None if failed
        """
        try:
            print("📄 Parsing PDF from URL with Firecrawl...")

            # Use Firecrawl with PDF parser explicitly
            result = self.firecrawl.scrape(
                pdf_url, formats=["markdown"], parsers=["pdf"]
            )

            # Extract markdown content
            markdown_content = getattr(result, "markdown", "")

            if not markdown_content or len(markdown_content) < 50:
                print(" Warning: Extracted content is very short")
                return None

            # Count words for info
            word_count = len(markdown_content.split())

            print(f"✅ Extracted {word_count:,} words")

            return {
                "markdown": markdown_content,
                "word_count": word_count,
                "raw_result": result,
                "method": "firecrawl",
            }

        except Exception as e:
            print(f"❌ Error parsing PDF from URL: {e}")
            return None

    def parse_pdf(self, file_path: str) -> Optional[Dict[str, object]]:
        """
        Parse PDF file using appropriate method (URL → Firecrawl, Local → PyMuPDF).

        Args:
            file_path: Path to local PDF file OR URL to PDF

        Returns:
            Dict with parsed content or None if failed
        """
        # Detect if input is URL or local path
        if self._is_url(file_path):
            print("🌐 Detected URL input - using Firecrawl")
            return self._parse_url_pdf(file_path)
        else:
            print("💾 Detected local file - using PyMuPDF")
            return self._parse_local_pdf(file_path)

    def get_parsed_content(self, parse_result: Dict) -> str:
        """
        Extract markdown text from parse result.

        Args:
            parse_result: Result from parse_pdf()

        Returns:
            Markdown text content
        """
        if not parse_result:
            return ""

        return parse_result.get("markdown", "")
