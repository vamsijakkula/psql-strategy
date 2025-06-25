import requests
import json

# Sample data matching your PostgreSQL table
test_data = {
    "data": [
        {
            "id": 1,
            "parameter": "alpha",
            "value": 0.7505,
            "timestamp": "2025-05-25T12:50:35Z",
            "description": "Primary scaling factor",
            "is_active": True
        },
        {
            "id": 2,
            "parameter": "beta",
            "value": 1.3695,
            "timestamp": "2025-05-25T12:50:35Z",
            "description": "Volatility coefficient",
            "is_active": True
        },
        {
            "id": 3,
            "parameter": "gamma",
            "value": 0.9395,
            "timestamp": "2025-05-25T12:50:35Z",
            "description": "Momentum adjustment",
            "is_active": True
        },
        {
            "id": 4,
            "parameter": "delta",
            "value": 0.3256,
            "timestamp": "2025-05-25T12:50:35Z",
            "description": "Risk sensitivity parameter",
            "is_active": False
        },
        {
            "id": 5,
            "parameter": "epsilon",
            "value": 1.8765,
            "timestamp": "2025-05-25T12:50:35Z",
            "description": "Liquidity factor",
            "is_active": True
        }
    ]
}

# Test the service
def test_strategy_service():
    url = "http://localhost:8080/strategy"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(test_data), headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print("=== Table Output ===")
        print(result["display_output"])
        print("\n=== Analysis ===")
        print(json.dumps(result["analysis"], indent=2))
        print("\n=== Summary ===")
        print(result["summary"])
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing service: {e}")

if __name__ == "__main__":
    test_strategy_service()