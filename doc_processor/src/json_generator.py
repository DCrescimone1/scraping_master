"""JSON output file generation."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class JSONGenerator:
    """Creates structured JSON output files."""
    
    def __init__(self, output_dir: str = "outputs/"):
        """
        Initialize generator.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def create_output(
        self,
        ai_data: Dict,
        user_answers: Dict,
        file_metadata: Dict,
        processing_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Combine all data into final JSON structure.
        
        Args:
            ai_data: AI analysis results
            user_answers: User context answers
            file_metadata: Source file info
            processing_metadata: Optional processing stats
            
        Returns:
            Complete output dict
        """
        timestamp = datetime.now().isoformat()
        
        output = {
            "document_info": {
                "source_file": file_metadata.get("filename", "unknown"),
                "file_path": file_metadata.get("file_path", ""),
                "processed_at": timestamp,
                "file_size_mb": file_metadata.get("size_mb", 0),
                "word_count": file_metadata.get("word_count", 0)
            },
            "ai_analysis": ai_data,
            "user_context": user_answers,
            "processing_metadata": processing_metadata or {}
        }
        
        return output
    
    def save_to_file(self, data: Dict, original_filename: str) -> str:
        """
        Save JSON data to timestamped file.
        
        Args:
            data: JSON data to save
            original_filename: Original PDF filename
            
        Returns:
            Path to saved file
        """
        try:
            # Generate filename
            base_name = Path(original_filename).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{base_name}_summary_{timestamp}.json"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return ""
    
    def display_summary(self, data: Dict):
        """
        Display key information in terminal.
        
        Args:
            data: Complete output data
        """
        print("\n" + "="*60)
        print("📊 Document Summary")
        print("="*60)
        
        # Executive summary
        if "ai_analysis" in data:
            summary = data["ai_analysis"].get("executive_summary", "N/A")
            print(f"\nSummary:\n{summary[:200]}...")
            
            # Key topics
            topics = data["ai_analysis"].get("key_topics", [])
            if topics:
                print(f"\nKey Topics: {', '.join(topics[:5])}")
            
            # Complexity
            complexity = data["ai_analysis"].get("complexity_assessment", "N/A")
            print(f"Complexity: {complexity}")
        
        print("\n" + "="*60 + "\n")
