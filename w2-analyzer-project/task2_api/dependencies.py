import os
from typing import Dict, Any

def get_movie_api_key() -> str:
    """Get movie API key from environment"""
    api_key = os.getenv("MOVIE_API_KEY")
    if not api_key:
        raise ValueError("MOVIE_API_KEY environment variable is required")
    return api_key