#!/usr/bin/env python3
"""
Document Processor - PDF Analysis Tool
Parses PDFs, analyzes with AI, collects user context, outputs structured JSON.
"""

import sys
import time
from pathlib import Path

# Import configuration
import config

# Import modules
from src.pdf_handler import PDFHandler
from src.firecrawl_parser import FirecrawlParser
from src.llm_processor import LLMProcessor
from src.user_prompt import UserPrompt
from src.json_generator import JSONGenerator


def get_pdf_path() -> str:
    """Get PDF path from command line or user input."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        print("📄 Document Processor")
        print("="*60)
        pdf_path = input("Enter path to PDF file: ").strip()
        return pdf_path


def main():
    """Main orchestration function."""
    start_time = time.time()
    
    try:
        # Get PDF path
        pdf_path = get_pdf_path()
        
        # PHASE 1: Validate PDF
        print("\n🔍 Validating PDF...")
        pdf_handler = PDFHandler()
        
        if not pdf_handler.validate_file(pdf_path):
            print("❌ Validation failed. Exiting.")
            return
        
        file_info = pdf_handler.get_file_info(pdf_path)
        print(f"✅ Valid: {file_info['filename']} ({file_info['size_mb']} MB)")
        
        # PHASE 2: Parse PDF (auto-detects URL vs local file)
        print("\n📄 Extracting text from PDF...")
        parser = FirecrawlParser(config.FIRECRAWL_API_KEY)
        
        parse_result = parser.parse_pdf(pdf_path)
        if not parse_result:
            print("❌ Failed to extract text from PDF. Exiting.")
            return
        
        markdown_text = parser.get_parsed_content(parse_result)
        file_info["word_count"] = parse_result.get("word_count", 0)
        
        # PHASE 3: Process with Grok AI
        print("\n🤖 Analyzing with LLM (xAI Grok by default)...")
        grok = LLMProcessor(config.GROK_API_KEY, config.GROK_MODEL, base_url="https://api.x.ai/v1")
        
        ai_analysis = grok.process_document(markdown_text, config.DOCUMENT_TEMPLATE)
        if not ai_analysis:
            print("❌ AI processing failed. Exiting.")
            return
        
        # PHASE 4: Collect user context
        print("\n📝 Collecting additional context...")
        user_prompt = UserPrompt(config.USER_QUESTIONS)
        
        raw_answers = user_prompt.ask_questions()
        user_context = user_prompt.format_for_json(raw_answers)
        
        # PHASE 5: Generate output
        print("\n💾 Generating JSON output...")
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        processing_meta = {
            "grok_model": config.GROK_MODEL,
            "parsing_method": "firecrawl",
            "total_processing_time_seconds": processing_time
        }
        
        generator = JSONGenerator(config.OUTPUT_DIR)
        
        final_output = generator.create_output(
            ai_data=ai_analysis,
            user_answers=user_context,
            file_metadata=file_info,
            processing_metadata=processing_meta
        )
        
        output_path = generator.save_to_file(final_output, file_info["filename"])
        
        if output_path:
            # Display summary
            generator.display_summary(final_output)
            print(f"✅ Processing complete! Saved to: {output_path}")
            print(f"⏱️  Total time: {processing_time}s")
        else:
            print("❌ Failed to save output file.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user. Exiting.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

