import requests
import json
from typing import Optional

def query_agent(question: str, api_url: str) -> Optional[dict]:

    try:
        payload = {
            "question": question,
            "top_k": 1
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.HTTPError:
        return None
    except Exception:
        return None

def test_connection(api_url: str) -> bool:

    try:
        
        base_url = api_url.replace('/query', '')
        response = requests.get(base_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def validate_api_response(response: dict) -> bool:

    if not isinstance(response, dict):
        return False
    

    expected_fields = ['answer', 'response', 'result']
    return any(field in response for field in expected_fields)