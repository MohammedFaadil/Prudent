import unittest
import os
import sys
import tempfile

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from w2_parser import W2Parser

class TestW2Parser(unittest.TestCase):
    
    def setUp(self):
        self.parser = W2Parser(test_mode=True)
    
    def test_test_mode_returns_data(self):
        result = self.parser.process_w2("dummy.pdf")
        
        self.assertIn("fields", result)
        self.assertIn("insights", result) 
        self.assertIn("quality", result)
        
        # Check structure
        self.assertIn("employee", result["fields"])
        self.assertIn("employer", result["fields"])
        self.assertIn("federal", result["fields"])
        self.assertIn("state_local", result["fields"])
        
        # Check insights are list
        self.assertIsInstance(result["insights"], list)
        self.assertGreater(len(result["insights"]), 0)
    
    def test_quality_report_structure(self):
        result = self.parser.process_w2("dummy.pdf")
        quality = result["quality"]
        
        self.assertIn("confidence", quality)
        self.assertIn("warnings", quality)
        self.assertIn("text_quality", quality)
        self.assertIn("extraction_method", quality)
    
    def test_sensitive_data_masking(self):
        test_data = {
            "employee": {"ssn": "123-45-6789"},
            "employer": {"ein": "12-3456789"}
        }
        
        self.parser._mask_sensitive_data(test_data)
        
        self.assertEqual(test_data["employee"]["ssn"], "***-**-6789")
        self.assertEqual(test_data["employer"]["ein"], "***-**-6789")
    
    def test_state_normalization(self):
        test_data = {
            "employee": {
                "address": {"state": "california"}
            },
            "employer": {
                "address": {"state": "ny"}
            }
        }
        
        self.parser._normalize_state_codes(test_data)
        
        self.assertEqual(test_data["employee"]["address"]["state"], "CA")
        self.assertEqual(test_data["employer"]["address"]["state"], "NY")
    
    def test_numeric_conversion(self):
        test_data = {
            "federal": {
                "wages_tips": "$75,000.00",
                "federal_income_tax": "15000"
            }
        }
        
        self.parser._convert_numeric_fields(test_data)
        
        self.assertEqual(test_data["federal"]["wages_tips"], 75000.0)
        self.assertEqual(test_data["federal"]["federal_income_tax"], 15000.0)

if __name__ == '__main__':
    unittest.main()