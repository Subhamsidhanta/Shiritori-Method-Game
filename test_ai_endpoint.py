import requests
import json

url = "http://localhost:5000/get-ai-word"
headers = {"Content-Type": "application/json"}

# Test 1: Start new game (no last word)
payload1 = {
    "topic": "fruits",
    "lastWord": None,
    "usedWords": []
}

try:
    print("Testing Start Game...")
    response = requests.post(url, headers=headers, json=payload1)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Continuation (last word 'apple' -> needs 'e')
payload2 = {
    "topic": "fruits",
    "lastWord": "apple",
    "usedWords": ["apple"]
}

try:
    print("\nTesting Continuation (after 'apple')...")
    response = requests.post(url, headers=headers, json=payload2)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
