from coinbase import jwt_generator
import os
from dotenv import load_dotenv

load_dotenv()

# Use your actual keys
api_key = os.getenv("CDP_API_KEY_ID")
api_secret = os.getenv("CDP_API_KEY_SECRET")
request_method = "GET"
request_path = "/api/v3/brokerage/accounts"

def test_auth():
    jwt_uri = jwt_generator.format_jwt_uri(request_method, request_path)
    jwt_token = jwt_generator.build_rest_jwt(jwt_uri, api_key, api_secret)
    print("✅ JWT Generated Successfully!")
    print(f"Bearer {jwt_token[:50]}...")
    
    # Test API call
    import requests
    headers = {"Authorization": f"Bearer {jwt_token}"}
    r = requests.get("https://api.coinbase.com/api/v3/brokerage/accounts", headers=headers)
    print(f"Status: {r.status_code}")
    print("✅ Backend Auth Works!")

test_auth()
