W-2 ANALYZER PROJECT
====================

A comprehensive solution with three interconnected tasks:
1. Price Gap Pair Finder Algorithm
2. FastAPI Web Service with Movie Search
3. AI-Powered W-2 Form Parser

PREREQUISITES
-------------
- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment recommended

QUICK START
-----------
1. Extract the project to your desired location
2. Open terminal/command prompt in the project root
3. Set up virtual environment and install dependencies:

   # Windows
   python -m venv w2_analyzer_venv
   w2_analyzer_venv\Scripts\activate
   pip install -r requirements.txt

   # macOS/Linux
   python3 -m venv w2_analyzer_venv
   source w2_analyzer_venv/bin/activate
   pip install -r requirements.txt

4. Set up environment variables (create .env file):
   MOVIE_API_KEY=your_movie_db_api_key
   GEMINI_API_KEY=your_gemini_ai_key

TASK 1: PRICE GAP PAIR FINDER
------------------------------
Location: task1_price_gap/

Purpose: Algorithm to find pairs of indices where absolute difference equals k

Run Tests:
cd task1_price_gap
python -m unittest test_price_gap.py

Expected Output:
.....
Ran 5 tests in 0.001s
OK

Usage as Library:
from price_gap import find_price_gap_pair
result = find_price_gap_pair([4, 1, 6, 3, 8], 2)
# Returns: (0, 2)

TASK 2: FASTAPI WEB SERVICE
----------------------------
Location: task2_api/

Purpose: REST API with price gap algorithm and movie search

Required API Key: 
- Get from https://www.themoviedb.org/settings/api
- Add to .env as MOVIE_API_KEY

Run API Server:
cd task2_api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

Access Points:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Price Gap Endpoint: POST http://localhost:8000/api/price-gap-pair
- Movies Endpoint: GET http://localhost:8000/api/movies?q=avengers

Test API:
cd task2_api
python -m pytest tests/ -v

Example API Calls:
# Price Gap
curl -X POST "http://localhost:8000/api/price-gap-pair" ^
  -H "Content-Type: application/json" ^
  -d "{\"nums\": [4,1,6,3,8], \"k\": 2}"

# Movies
curl "http://localhost:8000/api/movies?q=avengers&page=1"

TASK 3: AI W-2 FORM PARSER
---------------------------
Location: task3_w2_parser/

Purpose: Extract and analyze W-2 forms using Gemini AI

Required API Key:
- Get from https://aistudio.google.com/app/apikey  
- Add to .env as GEMINI_API_KEY

Run in Test Mode (No API Key Needed):
cd task3_w2_parser
python run_parser.py test.pdf --test-mode

Run with Real Processing:
python run_parser.py w2_form.pdf

Run Tests:
python -m unittest tests/test_w2_parser.py

Supported File Types:
- PDF files (.pdf)
- Image files (.jpg, .png, .tiff, .bmp)
- Text files (.txt)

Example Output:
{
  "fields": { ... structured W-2 data ... },
  "insights": [ ... AI-generated insights ... ],
  "quality": { ... processing metrics ... }
}

PROJECT STRUCTURE
-----------------
w2-analyzer-project/
├── task1_price_gap/          # Algorithm implementation
│   ├── price_gap.py
│   └── test_price_gap.py
├── task2_api/                # FastAPI web service
│   ├── main.py
│   ├── routes/
│   │   ├── price_gap.py
│   │   └── movies.py
│   └── tests/
├── task3_w2_parser/          # AI W-2 processor
│   ├── w2_parser.py
│   ├── gemini_client.py
│   ├── run_parser.py
│   ├── prompts/
│   └── tests/
├── requirements.txt          # All dependencies
├── .env.example             # Environment template
└── README.txt              # This file

ENVIRONMENT VARIABLES
---------------------
Create a .env file in project root:

MOVIE_API_KEY=your_themoviedb_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here

API KEYS SETUP
--------------
1. Movie Database API (The Movie DB):
   - Visit: https://www.themoviedb.org/settings/api
   - Create account and generate API key
   - Add to .env as MOVIE_API_KEY

2. Gemini AI API (Google AI):
   - Visit: https://aistudio.google.com/app/apikey
   - Create API key
   - Add to .env as GEMINI_API_KEY

TROUBLESHOOTING
---------------
1. ModuleNotFoundError: 
   - Run: pip install -r requirements.txt
   - Ensure virtual environment is activated

2. Import errors in Task 3:
   - Run from project root: python -m task3_w2_parser.run_parser

3. API connection issues:
   - Check API keys in .env file
   - Verify internet connection
   - Check API service status

4. Port 8000 already in use:
   - Use different port: uvicorn main:app --port 8001
   - Or kill existing process using port 8000

TESTING ALL TASKS
-----------------
# Task 1 - Algorithm
cd task1_price_gap && python -m unittest test_price_gap.py

# Task 2 - API 
cd task2_api && python -m pytest tests/

# Task 3 - W-2 Parser
cd task3_w2_parser && python -m unittest tests/test_w2_parser.py

DEPENDENCIES
------------
All required packages are in requirements.txt
Key dependencies:
- FastAPI: Modern web framework
- Uvicorn: ASGI server
- Google Generative AI: Gemini AI integration
- PyPDF2: PDF text extraction
- Pytesseract: OCR for images
- Pytest: Testing framework

SUPPORT
-------
For issues:
1. Check all prerequisites are installed
2. Verify API keys are correct
3. Ensure virtual environment is activated
4. Check file paths and permissions

LICENSE
-------
This project is for educational/demonstration purposes.