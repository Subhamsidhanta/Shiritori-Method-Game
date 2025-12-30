import requests
import json

url = "http://localhost:5000/save-score"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "gameType": "number",
    "score": 100,
    "timePlayed": 60,
    "playerId": "debug_user",
    "playerName": "Debug Player",
    "level": 5,
    "minRange": 1,
    "maxRange": 100,
    "memoryTime": 3
}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
