import hmac
import hashlib
import requests
import json

# Must match the $env:WEBHOOK_SECRET you set earlier
SECRET = "testsecret"
URL = "http://localhost:8000/webhook"

payload = {
    "message_id": "m1",
    "from": "+919876543210",
    "to": "+14155550100",
    "ts": "2025-01-15T10:00:00Z",
    "text": "Hello from Vivek!"
}

# Convert payload to raw bytes to calculate signature
body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')

# Calculate HMAC-SHA256
signature = hmac.new(SECRET.encode(), body_bytes, hashlib.sha256).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-Signature": signature
}

print(f"Sending message with signature: {signature}")
response = requests.post(URL, data=body_bytes, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")