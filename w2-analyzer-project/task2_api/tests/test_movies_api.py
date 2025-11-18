import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from task2_api.main import app

client = TestClient(app)

def test_movies_empty_query():
    response = client.get("/api/movies?q=")
    assert response.status_code == 200
    data = response.json()
    assert data["movies"] == []
    assert data["total_results"] == 0

def test_movies_no_query_param():
    response = client.get("/api/movies")
    assert response.status_code == 200
    data = response.json()
    assert data["movies"] == []
    assert data["total_results"] == 0

def test_movies_invalid_page():
    response = client.get("/api/movies?q=avengers&page=0")
    assert response.status_code == 422  # Validation error