import pytest
from fastapi.testclient import TestClient
from task2_api.main import app

client = TestClient(app)

def test_price_gap_pair_success():
    response = client.post("/api/price-gap-pair", json={
        "nums": [4, 1, 6, 3, 8],
        "k": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["indices"] == [0, 2]
    assert data["values"] == [4, 6]

def test_price_gap_pair_no_solution():
    response = client.post("/api/price-gap-pair", json={
        "nums": [10, 20, 30],
        "k": 25
    })
    assert response.status_code == 200
    data = response.json()
    assert data["indices"] is None
    assert data["values"] is None

def test_price_gap_pair_validation_error():
    response = client.post("/api/price-gap-pair", json={
        "nums": [1, 2],
        "k": -1  # Invalid - k must be >= 0
    })
    assert response.status_code == 422  # Validation error

def test_price_gap_pair_lexicographic_order():
    response = client.post("/api/price-gap-pair", json={
        "nums": [5, 5, 5],
        "k": 0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["indices"] == [0, 1]  # Lexicographically smallest