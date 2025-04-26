import pytest
from fastapi.testclient import TestClient
from main import app, calculate_index, get_prices
from unittest.mock import patch
import pandas as pd

# Mock prices for testing
mock_prices = {
    'AAPL': 175.0,
    'MSFT': 320.0,
    'META': 290.0,
    'AMZN': 140.0,
    'GOOGL': 130.0,
    'QCOM': 115.0,
    'AVGO': 890.0,
    'TSLA': 260.0,
    'NVDA': 720.0,
    'AMD': 170.0,
    'ORCL': 120.0,
    'ASML': 850.0
}

client = TestClient(app)

# Testing the root route
def test_root_route_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text.lower()  # Extra strictness

# Testing the index calculation logic
def test_calculate_index():
    index = calculate_index(mock_prices)
    expected = sum(mock_prices.values()) / len(mock_prices)
    assert index == expected

def test_calculate_index_empty():
    assert calculate_index({}) == 0

# Mocking Yahoo Finance data fetching
@patch("main.yf.download")
def test_get_prices(mock_download):
    # Simulate Yahoo Finance response
    data = pd.DataFrame({
        ('Close', 'AAPL'): [175.0],
        ('Close', 'MSFT'): [320.0],
        ('Close', 'META'): [290.0],
        ('Close', 'AMZN'): [140.0],
        ('Close', 'GOOGL'): [130.0],
        ('Close', 'QCOM'): [115.0],
        ('Close', 'AVGO'): [890.0],
        ('Close', 'TSLA'): [260.0],
        ('Close', 'NVDA'): [720.0],
        ('Close', 'AMD'): [170.0],
        ('Close', 'ORCL'): [120.0],
        ('Close', 'ASML'): [850.0]
    }, index=[0])

    data.columns = pd.MultiIndex.from_tuples(data.columns)
    mock_download.return_value = data

    prices = get_prices()
    assert isinstance(prices, dict)
    assert prices == mock_prices

# Testing WebSocket endpoint for stock average price calculation
@patch("main.TIME_TO_SLEEP", 0)  # Make loop instant for testing
@patch("main.get_prices")
@patch("main.insert_stock_price")  # Prevent DB writes during test
def test_websocket_index(mock_insert, mock_get_prices):
    mock_get_prices.return_value = {
        'AAPL': 100.0,
        'MSFT': 200.0,
        'GOOGL': 300.0,
    }

    with TestClient(app) as client:
        with client.websocket_connect("/ws/index") as websocket:
            data = websocket.receive_json()
            assert "value" in data
            expected_value = sum(mock_get_prices.return_value.values()) / len(mock_get_prices.return_value)
            assert round(data["value"], 2) == round(expected_value, 2)