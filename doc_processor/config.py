"""
Configuration settings for Document Processor.
Follows same pattern as easy_rich and manual_scrape configs.
"""

import os
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv()

# API Configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")  # Used for URL-based PDF parsing
GROK_API_KEY = os.getenv("GROK_API_KEY")  # xAI API key
GROK_MODEL = os.getenv("GROK_MODEL", "grok-beta")  # Default model

# Output Settings
OUTPUT_DIR = "outputs/"
FILENAME_PATTERN = "{original_name}_summary_{timestamp}.json"

# JSON Template - AI fills these fields
DOCUMENT_TEMPLATE = {
    "executive_summary": "",
    "document_type": "",
    "key_topics": [],
    "technical_details": {
        "technologies_mentioned": [],
        "requirements": [],
        "constraints": []
    },
    "entities": {
        "people": [],
        "organizations": [],
        "products": [],
        "dates": []
    },
    "action_items": [],
    "decisions_made": [],
    "open_questions": [],
    "complexity_assessment": "",
    "estimated_read_time_minutes": 0,
    "critical_sections": []
}

# User Questions - asked in terminal after AI processing
USER_QUESTIONS = [
    "What is the primary purpose of this document?",
    "Who is the intended audience? (e.g., developers, executives)",
    "Project or client name (if applicable):",
    "Any critical deadlines or milestones mentioned?",
    "Specific areas you want highlighted or tracked:",
    "Additional context or notes:"
]

# Validation
if not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables")

if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY not found in environment variables")

