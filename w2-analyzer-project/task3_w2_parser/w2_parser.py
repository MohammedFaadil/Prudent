import os
import json
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import PyPDF2
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from .gemini_client import GeminiClient
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from gemini_client import GeminiClient

class W2Parser:
    def __init__(self, api_key: Optional[str] = None, test_mode: bool = False):
        self.test_mode = test_mode
        if test_mode:
            self.gemini_client = None
        else:
            self.gemini_client = GeminiClient(api_key)
        
    def process_w2(self, file_path: str) -> Dict[str, Any]:
        """
        Main entrypoint for W-2 processing
        Returns: { fields, insights, quality }
        """
        if self.test_mode:
            return self._process_test_mode()
        
        try:
            # Step 1: Extract text from file
            text_content, extraction_method = self._extract_text_from_file(file_path)
            
            # Step 2: Extract structured data using Gemini
            extracted_data = self.gemini_client.extract_w2_data(text_content)
            
            # Step 3: Post-process and normalize data
            normalized_data = self._normalize_data(extracted_data)
            
            # Step 4: Generate insights
            address = self._get_employee_address(normalized_data)
            insights_data = self.gemini_client.generate_insights(normalized_data, address)
            
            # Step 5: Generate quality report
            quality_report = self._generate_quality_report(normalized_data, text_content, extraction_method)
            
            return {
                "fields": normalized_data,
                "insights": insights_data.get("insights", []),
                "quality": quality_report
            }
            
        except Exception as e:
            return {
                "fields": {},
                "insights": [f"• Processing error: {str(e)}"],
                "quality": {
                    "confidence": "low",
                    "warnings": [f"Processing failed: {str(e)}"],
                    "ocr_quality": "unknown",
                    "extraction_method": "failed"
                }
            }
    
    def _extract_text_from_file(self, file_path: str) -> tuple[str, str]:
        """Extract text from PDF or image file, return text and method used"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.pdf']:
            return self._extract_text_from_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self._extract_text_from_image(file_path)
        elif file_ext in ['.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), "direct_text"
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_text_from_pdf(self, file_path: str) -> tuple[str, str]:
        """Extract text from PDF file"""
        if not OCR_AVAILABLE:
            return "PDF processing requires PyPDF2 and pytesseract", "failed"
            
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # If little text was extracted, try OCR
                if len(text.strip()) < 100:
                    ocr_text = self._ocr_pdf(file_path)
                    return ocr_text, "ocr"
                return text, "direct_extraction"
                
        except Exception as e:
            # Fallback to OCR
            try:
                ocr_text = self._ocr_pdf(file_path)
                return ocr_text, "ocr_fallback"
            except Exception as ocr_error:
                return f"PDF extraction failed: {str(e)}", "failed"
    
    def _extract_text_from_image(self, file_path: str) -> tuple[str, str]:
        """Extract text from image using OCR"""
        if not OCR_AVAILABLE:
            return "Image processing requires PIL and pytesseract", "failed"
            
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text, "ocr"
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")
    
    def _ocr_pdf(self, file_path: str) -> str:
        """OCR for PDF files - simplified implementation"""
        # In production, you'd use pdf2image to convert PDF to images then OCR
        return "PDF OCR would be implemented here with pdf2image conversion"
    
    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and clean extracted data"""
        if not data:
            return {}
            
        # Ensure all expected sections exist
        normalized = {
            "employee": data.get("employee", {}),
            "employer": data.get("employer", {}),
            "federal": data.get("federal", {}),
            "state_local": data.get("state_local", []),
            "other_boxes": data.get("other_boxes", {})
        }
        
        # Mask SSN and EIN
        self._mask_sensitive_data(normalized)
        
        # Normalize state codes
        self._normalize_state_codes(normalized)
        
        # Convert numeric fields
        self._convert_numeric_fields(normalized)
        
        return normalized
    
    def _mask_sensitive_data(self, data: Dict[str, Any]):
        """Mask SSN and EIN to last 4 digits"""
        # Employee SSN
        if 'employee' in data and data['employee'].get('ssn'):
            ssn = str(data['employee']['ssn'])
            # Remove non-digits and get last 4
            digits = re.sub(r'\D', '', ssn)
            if len(digits) >= 4:
                data['employee']['ssn'] = f"***-**-{digits[-4:]}"
            else:
                data['employee']['ssn'] = "***-**-****"
        
        # Employer EIN
        if 'employer' in data and data['employer'].get('ein'):
            ein = str(data['employer']['ein'])
            digits = re.sub(r'\D', '', ein)
            if len(digits) >= 4:
                data['employer']['ein'] = f"***-**-{digits[-4:]}"
            else:
                data['employer']['ein'] = "***-**-****"
    
    def _normalize_state_codes(self, data: Dict[str, Any]):
        """Normalize state codes to 2-letter format"""
        state_mapping = {
            'alabama': 'AL', 'al': 'AL',
            'alaska': 'AK', 'ak': 'AK',
            'arizona': 'AZ', 'az': 'AZ',
            'arkansas': 'AR', 'ar': 'AR',
            'california': 'CA', 'ca': 'CA',
            'colorado': 'CO', 'co': 'CO',
            'connecticut': 'CT', 'ct': 'CT',
            'delaware': 'DE', 'de': 'DE',
            'florida': 'FL', 'fl': 'FL',
            'georgia': 'GA', 'ga': 'GA',
            'hawaii': 'HI', 'hi': 'HI',
            'idaho': 'ID', 'id': 'ID',
            'illinois': 'IL', 'il': 'IL',
            'indiana': 'IN', 'in': 'IN',
            'iowa': 'IA', 'ia': 'IA',
            'kansas': 'KS', 'ks': 'KS',
            'kentucky': 'KY', 'ky': 'KY',
            'louisiana': 'LA', 'la': 'LA',
            'maine': 'ME', 'me': 'ME',
            'maryland': 'MD', 'md': 'MD',
            'massachusetts': 'MA', 'ma': 'MA',
            'michigan': 'MI', 'mi': 'MI',
            'minnesota': 'MN', 'mn': 'MN',
            'mississippi': 'MS', 'ms': 'MS',
            'missouri': 'MO', 'mo': 'MO',
            'montana': 'MT', 'mt': 'MT',
            'nebraska': 'NE', 'ne': 'NE',
            'nevada': 'NV', 'nv': 'NV',
            'new hampshire': 'NH', 'nh': 'NH',
            'new jersey': 'NJ', 'nj': 'NJ',
            'new mexico': 'NM', 'nm': 'NM',
            'new york': 'NY', 'ny': 'NY',
            'north carolina': 'NC', 'nc': 'NC',
            'north dakota': 'ND', 'nd': 'ND',
            'ohio': 'OH', 'oh': 'OH',
            'oklahoma': 'OK', 'ok': 'OK',
            'oregon': 'OR', 'or': 'OR',
            'pennsylvania': 'PA', 'pa': 'PA',
            'rhode island': 'RI', 'ri': 'RI',
            'south carolina': 'SC', 'sc': 'SC',
            'south dakota': 'SD', 'sd': 'SD',
            'tennessee': 'TN', 'tn': 'TN',
            'texas': 'TX', 'tx': 'TX',
            'utah': 'UT', 'ut': 'UT',
            'vermont': 'VT', 'vt': 'VT',
            'virginia': 'VA', 'va': 'VA',
            'washington': 'WA', 'wa': 'WA',
            'west virginia': 'WV', 'wv': 'WV',
            'wisconsin': 'WI', 'wi': 'WI',
            'wyoming': 'WY', 'wy': 'WY'
        }
        
        # Normalize employee state
        if 'employee' in data and 'address' in data['employee']:
            state = data['employee']['address'].get('state', '')
            if state and isinstance(state, str):
                state_lower = state.lower().strip()
                if state_lower in state_mapping:
                    data['employee']['address']['state'] = state_mapping[state_lower]
        
        # Normalize employer state
        if 'employer' in data and 'address' in data['employer']:
            state = data['employer']['address'].get('state', '')
            if state and isinstance(state, str):
                state_lower = state.lower().strip()
                if state_lower in state_mapping:
                    data['employer']['address']['state'] = state_mapping[state_lower]
        
        # Normalize state/local states
        if 'state_local' in data:
            for state_data in data['state_local']:
                state = state_data.get('state', '')
                if state and isinstance(state, str):
                    state_lower = state.lower().strip()
                    if state_lower in state_mapping:
                        state_data['state'] = state_mapping[state_lower]
    
    def _convert_numeric_fields(self, data: Dict[str, Any]):
        """Convert string numeric fields to numbers"""
        monetary_fields = [
            'wages_tips', 'federal_income_tax', 'social_security_wages',
            'social_security_tax', 'medicare_wages', 'medicare_tax',
            'social_security_tips', 'allocated_tips', 'dependent_care_benefits',
            'nonqualified_plans'
        ]
        
        # Federal fields
        if 'federal' in data:
            for field in monetary_fields:
                if field in data['federal'] and data['federal'][field]:
                    try:
                        value = data['federal'][field]
                        if isinstance(value, str):
                            # Remove non-numeric characters except decimal point and minus
                            cleaned = re.sub(r'[^\d.-]', '', value)
                            if cleaned and cleaned != '-':
                                data['federal'][field] = float(cleaned)
                            else:
                                data['federal'][field] = None
                    except (ValueError, TypeError):
                        data['federal'][field] = None
        
        # State fields
        if 'state_local' in data:
            for state_data in data['state_local']:
                for field in ['state_wages', 'state_income_tax']:
                    if field in state_data and state_data[field]:
                        try:
                            value = state_data[field]
                            if isinstance(value, str):
                                cleaned = re.sub(r'[^\d.-]', '', value)
                                if cleaned and cleaned != '-':
                                    state_data[field] = float(cleaned)
                                else:
                                    state_data[field] = None
                        except (ValueError, TypeError):
                            state_data[field] = None
    
    def _get_employee_address(self, data: Dict[str, Any]) -> str:
        """Extract employee address as string"""
        if 'employee' in data and 'address' in data['employee']:
            addr = data['employee']['address']
            components = []
            if addr.get('street'):
                components.append(addr['street'])
            if addr.get('city'):
                components.append(addr['city'])
            if addr.get('state'):
                components.append(addr['state'])
            if addr.get('zip'):
                components.append(addr['zip'])
            return ', '.join(components)
        return ""
    
    def _generate_quality_report(self, data: Dict[str, Any], extracted_text: str, extraction_method: str) -> Dict[str, Any]:
        """Generate data quality report"""
        warnings = []
        confidence = "high"
        
        # Check for missing critical fields
        critical_fields = [
            'employee.name', 'employee.ssn', 'federal.wages_tips',
            'federal.federal_income_tax'
        ]
        
        missing_fields = []
        for field_path in critical_fields:
            parts = field_path.split('.')
            current = data
            found = True
            for part in parts:
                if part in current and current[part] not in [None, ""]:
                    current = current[part]
                else:
                    found = False
                    break
            if not found:
                missing_fields.append(field_path)
        
        if missing_fields:
            warnings.append(f"Missing critical fields: {', '.join(missing_fields)}")
            confidence = "medium"
        
        # Check text extraction quality
        text_quality = "good"
        if len(extracted_text.strip()) < 50:
            warnings.append("Low text extraction - possible OCR issues")
            text_quality = "poor"
            confidence = "low"
        elif len(extracted_text.strip()) < 200:
            text_quality = "fair"
            if confidence != "low":
                confidence = "medium"
        
        # Check for inconsistent data
        federal = data.get('federal', {})
        if (federal.get('wages_tips') and 
            federal.get('social_security_wages') and
            federal['social_security_wages'] > federal['wages_tips']):
            warnings.append("Social Security wages exceed Box 1 wages - possible data inconsistency")
        
        return {
            "confidence": confidence,
            "warnings": warnings,
            "text_quality": text_quality,
            "extraction_method": extraction_method,
            "text_length": len(extracted_text.strip()),
            "critical_fields_missing": len(missing_fields)
        }
    
    def _process_test_mode(self) -> Dict[str, Any]:
        """Process in test mode without network calls"""
        # Create comprehensive test data
        return {
            "fields": {
                "employee": {
                    "name": "John A. Doe",
                    "address": {
                        "street": "123 Main Street",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10001"
                    },
                    "ssn": "***-**-1234"
                },
                "employer": {
                    "name": "Tech Solutions Inc.",
                    "address": {
                        "street": "456 Business Avenue",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10002"
                    },
                    "ein": "***-**-5678",
                    "state_id": "NY-123456789"
                },
                "federal": {
                    "wages_tips": 75000.0,
                    "federal_income_tax": 15000.0,
                    "social_security_wages": 75000.0,
                    "social_security_tax": 4650.0,
                    "medicare_wages": 75000.0,
                    "medicare_tax": 1087.5,
                    "social_security_tips": 0.0,
                    "allocated_tips": 0.0,
                    "dependent_care_benefits": 0.0,
                    "nonqualified_plans": 0.0
                },
                "state_local": [
                    {
                        "state": "NY",
                        "employer_state_id": "NY-123456789",
                        "state_wages": 75000.0,
                        "state_income_tax": 4500.0
                    }
                ],
                "other_boxes": {
                    "box_12": {
                        "D": 5000.0
                    },
                    "box_13": {
                        "statutory_employee": False,
                        "retirement_plan": True,
                        "third_party_sick_pay": False
                    },
                    "box_14": {
                        "other_info": "Professional dues: 300.00"
                    }
                }
            },
            "insights": [
                "• Test mode: Using simulated W-2 data",
                "• Address validation: ZIP code 10001 corresponds to NY state, matches employer state",
                "• Federal withholding at 20.0% of Box 1 wages ($15,000 / $75,000)",
                "• Social Security wages below annual limit of $160,200 for 2023",
                "• Single state income reported for New York with $4,500 state tax withheld",
                "• All critical W-2 boxes present and consistent",
                "• Retirement plan participation indicated in Box 13"
            ],
            "quality": {
                "confidence": "high",
                "warnings": ["Test mode - no actual processing performed"],
                "text_quality": "good",
                "extraction_method": "test_mode",
                "text_length": 0,
                "critical_fields_missing": 0
            }
        }