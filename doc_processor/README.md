# Document Processor - PDF & XML Analysis


## Overview

Converts PDF and XML documents into structured JSON summaries with:
- Automated text extraction (Firecrawl)
- AI-powered analysis (xAI Grok via HTTP requests)
- User context collection (terminal Q&A)
- Timestamped JSON output

## Requirements

- Python 3.7+
- PyMuPDF (for local PDF parsing)
- Firecrawl API key (for URL-based PDF parsing)
- xAI Grok API key
- requests (for fetching XML over HTTP)

## Installation

```bash
cd doc_processor
pip install -r requirements.txt
```

## Configuration

Add to root `.env` file:

```
FIRECRAWL_API_KEY=fc-your-key-here
GROK_API_KEY=xai-your-key-here
# Optional model (defaults to grok-beta)
GROK_MODEL=grok-4-fast-reasoning
```

## Usage

### Command Line

```bash
# Local PDF
python3 main.py /path/to/your/document.pdf

# Local XML
python3 main.py /path/to/your/document.xml

# PDF URL
python3 main.py https://example.com/document.pdf

# XML URL
python3 main.py https://example.com/data.xml
```

### Interactive Mode

```bash
python3 main.py
# Then enter path or URL when prompted
```

## Output

JSON files saved to `outputs/` with structure:

```json
{
  "document_info": {
    "source_file": "specs.pdf",
    "processed_at": "2025-10-10T14:30:00Z",
    "file_size_mb": 1.2,
    "word_count": 2345
  },
  "ai_analysis": {
    "executive_summary": "...",
    "key_topics": ["..."],
    "technical_details": {"technologies_mentioned": ["..."], "requirements": ["..."], "constraints": ["..."]},
    "entities": {"people": ["..."], "organizations": ["..."], "products": ["..."], "dates": ["..."]},
    "action_items": ["..."],
    "decisions_made": ["..."],
    "open_questions": ["..."],
    "complexity_assessment": "Medium",
    "estimated_read_time_minutes": 12,
    "critical_sections": ["..."]
  },
  "user_context": {
    "purpose": "...",
    "audience": "...",
    "project_or_client_name": "..."
  }
}
```

## Architecture

```
doc_processor/
├── main.py                  # Orchestrator
├── config.py                # Settings & templates
├── outputs/                 # Generated JSON files
└── src/
    ├── pdf_handler.py       # File validation (PDF & XML)
    ├── firecrawl_parser.py  # PDF/XML → text extraction
    ├── llm_processor.py     # AI analysis (generic)
    ├── user_prompt.py       # Terminal Q&A
    └── json_generator.py    # Output creation
```

## Features

- ✅ Hybrid PDF Processing: Automatically detects and processes local PDFs (PyMuPDF) and PDF URLs (Firecrawl)
- ✅ XML Processing: Supports local XML files and XML URLs (requests + xml parsers)
- ✅ PDF text extraction with Firecrawl
- ✅ AI analysis via LLM (xAI Grok by default)
- ✅ Interactive context collection
- ✅ Structured JSON output
- ✅ Timestamped filenames
- ✅ Error handling & validation

## XML Processing

The tool now includes an enhanced BMEcat XML parser that:

- Captures all XML attributes (type, language, relationships)
- Preserves complete content including long descriptions
- Maintains multi-language support (deu, fra, ita)
- Provides structured output optimized for AI processing

The BMEcat parser automatically extracts:
- Catalog header information (ID, version, languages, supplier)
- Complete catalog structure hierarchy (root, node, leaf categories)
- All group names and descriptions in all available languages
- Parent-child relationships and ordering information

## Notes

- Processes one PDF at a time
- Text-focused (images in PDFs ignored)
- Output saved with timestamp to prevent overwriting
