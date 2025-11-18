import google.generativeai as genai
import os
import json
import time
from typing import Dict, Any, Optional

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_w2_data(self, text_content: str) -> Dict[str, Any]:
        """Extract W-2 data using Gemini with retry logic"""
        try:
            # Get extraction prompt
            prompt_dir = os.path.join(os.path.dirname(__file__), 'prompts')
            extraction_prompt_path = os.path.join(prompt_dir, 'extraction_prompt.txt')
            
            if os.path.exists(extraction_prompt_path):
                with open(extraction_prompt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read()
            else:
                # Fallback prompt
                prompt = """EXTRACT W-2 INFORMATION TO JSON
                Extract all W-2 tax form fields into structured JSON format.
                Include employee info, employer info, federal tax data, and state/local data.
                Mask SSN and EIN to last 4 digits only.
                Return ONLY valid JSON, no other text."""
        
            full_prompt = f"{prompt}\n\nW-2 CONTENT:\n{text_content}"
            
            # Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(full_prompt)
                    result_text = response.text.strip()
                    
                    # Clean the response to ensure valid JSON
                    if result_text.startswith("```json"):
                        result_text = result_text[7:]
                    if result_text.endswith("```"):
                        result_text = result_text[:-3]
                    if result_text.startswith("```"):
                        result_text = result_text[3:]
                    
                    return json.loads(result_text)
                    
                except json.JSONDecodeError as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                        continue
                    else:
                        raise Exception(f"Failed to parse JSON response after {max_retries} attempts: {str(e)}")
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        raise
            
        except Exception as e:
            raise Exception(f"Gemini extraction failed: {str(e)}")
    
    def generate_insights(self, extracted_data: Dict[str, Any], address: str) -> Dict[str, Any]:
        """Generate insights using Gemini with retry logic"""
        try:
            # Get insights prompt
            prompt_dir = os.path.join(os.path.dirname(__file__), 'prompts')
            insights_prompt_path = os.path.join(prompt_dir, 'insights_prompt.txt')
            
            if os.path.exists(insights_prompt_path):
                with open(insights_prompt_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
            else:
                prompt_template = """Generate 5-8 concise insights for this W-2 data:
                {extracted_data}
                
                Employee Address: {employee_address}
                
                Focus on:
                - Address validation
                - Tax withholding analysis  
                - Social Security & Medicare
                - Data quality issues
                - Follow-up actions
                
                Return JSON: {"insights": ["• insight 1", "• insight 2", ...]}"""
        
            prompt = prompt_template.format(
                extracted_data=json.dumps(extracted_data, indent=2),
                employee_address=address
            )
            
            # Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    result_text = response.text.strip()
                    
                    # Clean the response
                    if result_text.startswith("```json"):
                        result_text = result_text[7:]
                    if result_text.endswith("```"):
                        result_text = result_text[:-3]
                    if result_text.startswith("```"):
                        result_text = result_text[3:]
                    
                    insights_data = json.loads(result_text)
                    
                    # Ensure insights is a list
                    if isinstance(insights_data.get('insights'), list):
                        return insights_data
                    else:
                        return {'insights': []}
                        
                except json.JSONDecodeError as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        # Return default insights on failure
                        return {'insights': ['• Unable to generate insights due to processing error']}
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        return {'insights': ['• Insight generation failed']}
            
        except Exception as e:
            return {'insights': [f'• Error generating insights: {str(e)}']}