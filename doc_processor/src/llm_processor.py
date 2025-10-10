"""Generic LLM API integration for document analysis (xAI Grok-compatible)."""

import json
from typing import Dict, Optional
import requests


class LLMProcessor:
    """Processes documents using xAI's Grok API via direct HTTP calls."""

    def __init__(self, api_key: str, model_name: str = "grok-4-fast-reasoning", base_url: str = "https://api.x.ai/v1"):
        """Initialize LLM processor.

        Args:
            api_key: xAI API key
            model_name: Grok model to use
            base_url: xAI API base URL
        """
        if not api_key:
            raise ValueError("LLM API key is required")

        self.api_key = api_key
        self.model = model_name
        self.base_url = base_url.rstrip('/')
    
    def create_analysis_prompt(self, text_content: str, template: Dict) -> str:
        """
        Create prompt for the LLM to analyze the document and fill the template.
        """
        template_str = json.dumps(template, indent=2)
        
        prompt = f"""Analyze the following document and fill the JSON template with accurate information extracted from the text.

INSTRUCTIONS:
- Be concise but thorough
- Extract only information present in the document
- Use "N/A" for fields where information is not available
- For lists, provide the most relevant items
- Estimate complexity as: Simple, Medium, or Complex

DOCUMENT CONTENT:
{text_content[:15000]}  

JSON TEMPLATE TO FILL:
{template_str}

Return ONLY the filled JSON, no other text."""
        
        return prompt
    
    def process_document(self, markdown_text: str, template: Dict) -> Optional[Dict]:
        """
        Send document to the LLM for analysis and return the filled JSON template.
        """
        try:
            print("🤖 Processing with LLM (xAI Grok)...")

            # Create prompt
            prompt = self.create_analysis_prompt(markdown_text, template)

            # Build request
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a document analysis AI that extracts structured information and fills JSON templates accurately.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.3,
                "max_tokens": 4000,
            }

            resp = requests.post(url, headers=headers, json=payload, timeout=60)

            if resp.status_code != 200:
                print(f"❌ Grok API error: {resp.status_code} - {resp.text[:500]}")
                return None

            data = resp.json()

            # Extract assistant message content
            try:
                content = data["choices"][0]["message"]["content"]
            except Exception:
                print("❌ Unexpected response format from Grok API")
                return None
            
            # Parse JSON response
            try:
                filled_template = json.loads(content)
                print("✅ AI analysis complete")
                return filled_template
            except json.JSONDecodeError:
                print("⚠️  Warning: Response was not valid JSON, attempting to extract...")
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    filled_template = json.loads(json_str)
                    print("✅ AI analysis complete (extracted JSON)")
                    return filled_template
                else:
                    print("❌ Could not parse AI response as JSON")
                    return None
        except Exception as e:
            print(f"❌ Error processing with LLM: {e}")
            return None
