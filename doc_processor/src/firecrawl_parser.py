"""Firecrawl PDF/XML parsing integration."""

from typing import Optional, Dict
from firecrawl import Firecrawl
import fitz  # PyMuPDF
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from .bmecat_parser import BMEcatParser

class FirecrawlParser:
    """Handles PDF and XML to text conversion using Firecrawl and local parsers."""

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

    def _parse_local_xml(self, file_path: str) -> Optional[Dict[str, object]]:
        """
        Parse local XML file using enhanced BMEcat parser.

        Args:
            file_path: Path to local XML file
            
        Returns:
            Dict with parsed content or None if failed
        """
        try:
            print("📄 Parsing BMEcat XML with enhanced parser...")
            
            # Use BMEcat-specific parser
            bmecat_parser = BMEcatParser()
            parsed_data = bmecat_parser.parse_bmecat_file(file_path)
            
            if not parsed_data:
                print("⚠️  Failed to parse BMEcat XML")
                return None
            
            # Convert to markdown for AI processing
            markdown_content = bmecat_parser.to_markdown(parsed_data)
            word_count = len(markdown_content.split())
            
            print(f"✅ Extracted {word_count:,} words")
            print(f"   - {parsed_data['metadata']['total_catalog_structures']} catalog structures")
            print(f"   - {parsed_data['metadata']['root_categories']} root categories")
            
            return {
                "markdown": markdown_content,
                "word_count": word_count,
                "method": "bmecat_parser"
            }
        
        except Exception as e:
            print(f"❌ Error parsing BMEcat XML: {e}")
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

    def _parse_url_xml(self, url: str) -> Optional[Dict[str, object]]:
        """
        Parse XML from URL.
        
        Args:
            url: URL to XML file
            
        Returns:
            Dict with parsed content or None if failed
        """
        try:
            import requests
            
            # Fetch XML from URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Convert to pretty-printed string
            xml_string = ET.tostring(root, encoding='unicode')
            pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
            
            # Combine structure content (pretty XML only)
            markdown_text = f"# XML Document Structure\n\n```xml\n{pretty_xml}\n```"
            
            word_count = len(pretty_xml.split())
            
            return {
                "markdown": markdown_text,
                "word_count": word_count,
                "method": "xml_url_parser"
            }
            
        except Exception as e:
            print(f"❌ Error parsing XML URL: {e}")
            return None



    def parse_document(self, file_path: str, file_type: str = 'pdf') -> Optional[Dict[str, object]]:
        """
        Parse document (PDF or XML) based on type and location.

        Args:
            file_path: Path to local file OR URL to file
            file_type: 'pdf' or 'xml' (default: 'pdf')

        Returns:
            Dict with parsed content or None if failed
        """
        is_url = self._is_url(file_path)

        # Route to appropriate parser
        if file_type == 'pdf':
            if is_url:
                print("🌐 Detected PDF URL - using Firecrawl")
                return self._parse_url_pdf(file_path)
            else:
                print("💾 Detected local PDF - using PyMuPDF")
                return self._parse_local_pdf(file_path)
        elif file_type == 'xml':
            if is_url:
                print("🌐 Detected XML URL - using XML parser")
                return self._parse_url_xml(file_path)
            else:
                print("💾 Detected local XML - using XML parser")
                return self._parse_local_xml(file_path)
        else:
            print(f"❌ Unsupported file type: {file_type}")
            return None

    def get_parsed_content(self, parse_result: Dict) -> str:
        """
        Extract markdown text from parse result.
        
        Args:
            parse_result: Result from parse_document()
        
        Returns:
            Markdown text content
        """
        if not parse_result:
            return ""
        return parse_result.get("markdown", "")
