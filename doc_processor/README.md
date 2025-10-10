# Document Processor


## Overview

Converts PDF documents into structured JSON summaries with:
- Automated text extraction (Firecrawl)
- AI-powered analysis (xAI Grok via HTTP requests)
- User context collection (terminal Q&A)
- Timestamped JSON output

## Requirements

- Python 3.7+
- PyMuPDF (for local PDF parsing)
- Firecrawl API key (for URL-based PDF parsing)
- xAI Grok API key

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
# With Local PDF
python3 main.py /path/to/your/document.pdf

# With PDF URL
python3 main.py https://example.com/document.pdf
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
    ├── pdf_handler.py       # File validation
    ├── firecrawl_parser.py  # PDF→text extraction
    ├── llm_processor.py     # AI analysis (generic)
    ├── user_prompt.py       # Terminal Q&A
    └── json_generator.py    # Output creation
```

## Features

- ✅ Hybrid PDF Processing: Automatically detects and processes both local PDFs (PyMuPDF) and PDF URLs (Firecrawl)
- ✅ PDF text extraction with Firecrawl
- ✅ AI analysis via LLM (xAI Grok by default)
- ✅ Interactive context collection
- ✅ Structured JSON output
- ✅ Timestamped filenames
- ✅ Error handling & validation

## Notes

- Processes one PDF at a time
- Text-focused (images in PDFs ignored)
- Output saved with timestamp to prevent overwriting
