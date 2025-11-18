#!/usr/bin/env python3
"""
W-2 Parser CLI
Usage: python run_parser.py <file_path> [--test-mode]
"""
import argparse
import sys
import os
import json

# Add the current directory to Python path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from w2_parser import W2Parser

def main():
    parser = argparse.ArgumentParser(
        description="Process W-2 forms and extract structured data with AI insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_parser.py w2_form.pdf                    # Process with Gemini AI
  python run_parser.py w2_form.pdf --test-mode        # Test mode (no API calls)
  python run_parser.py w2_image.jpg                   # Process image file
        """
    )
    
    parser.add_argument(
        "file_path", 
        help="Path to W-2 file (PDF, image, or text)"
    )
    
    parser.add_argument(
        "--test-mode", 
        action="store_true",
        help="Run in test mode (no API calls, uses sample data)"
    )
    
    parser.add_argument(
        "--output", 
        "-o",
        help="Output file path for JSON results (default: print to console)"
    )
    
    parser.add_argument(
        "--api-key",
        help="Gemini API key (default: uses GEMINI_API_KEY environment variable)"
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.file_path):
        print(f"❌ Error: File not found: {args.file_path}")
        sys.exit(1)
    
    # Check file size
    file_size = os.path.getsize(args.file_path)
    if file_size == 0:
        print(f"❌ Error: File is empty: {args.file_path}")
        sys.exit(1)
    
    print(f"🔍 Processing W-2 file: {args.file_path}")
    print(f"📁 File size: {file_size} bytes")
    print(f"🧪 Test mode: {'Yes' if args.test_mode else 'No'}")
    
    try:
        # Initialize parser
        w2_parser = W2Parser(api_key=args.api_key, test_mode=args.test_mode)
        
        # Process the file
        print("⏳ Processing...")
        result = w2_parser.process_w2(args.file_path)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Results saved to: {args.output}")
        else:
            print("\n" + "="*60)
            print("W-2 PROCESSING RESULTS")
            print("="*60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"  Confidence: {result['quality']['confidence']}")
        print(f"  Fields extracted: {len(result['fields'])} sections")
        print(f"  Insights generated: {len(result['insights'])}")
        
        if result['quality']['warnings']:
            print(f"  Warnings: {len(result['quality']['warnings'])}")
        
    except Exception as e:
        print(f"❌ Error processing W-2: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()