import requests
import hmac
import hashlib
import time
import os
from dotenv import load_dotenv

load_dotenv()

print("🔐 Testing Coinbase API Authentication\n")

# Try to load both possible key names
api_key = os.getenv("COINBASE_ACCOUNT_API_KEY") or os.getenv("CDP_API_KEY_ID")
api_secret = os.getenv("COINBASE_ACCOUNT_API_SECRET") or os.getenv("CDP_API_KEY_SECRET")

print("Checking environment variables:")
print(f"COINBASE_ACCOUNT_API_KEY: {'✅ Found' if os.getenv('COINBASE_ACCOUNT_API_KEY') else '❌ Not found'}")
print(f"COINBASE_ACCOUNT_API_SECRET: {'✅ Found' if os.getenv('COINBASE_ACCOUNT_API_SECRET') else '❌ Not found'}")
print(f"CDP_API_KEY_ID: {'✅ Found' if os.getenv('CDP_API_KEY_ID') else '❌ Not found'}")
print(f"CDP_API_KEY_SECRET: {'✅ Found' if os.getenv('CDP_API_KEY_SECRET') else '❌ Not found'}")
print()

if api_key:
    print(f"Using API Key: {api_key[:20]}...")
else:
    print("❌ No API Key found!")

if api_secret:
    print(f"Using API Secret: {api_secret[:20]}...")
else:
    print("❌ No API Secret found!")

print()

if not api_key or not api_secret:
    print("❌ Keys missing!")
    print("\n📝 Debug: Let's check your .env file")
    print("\nRun this command:")
    print("cat .env | grep -E 'COINBASE_ACCOUNT|CDP_API'")
    exit(1)

# Test with Coinbase API
timestamp = str(int(time.time()))
method = "GET"
path = "/v2/user"
body = ""

message = timestamp + method + path + body
signature = hmac.new(
    api_secret.encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()

headers = {
    "CB-ACCESS-KEY": api_key,
    "CB-ACCESS-SIGN": signature,
    "CB-ACCESS-TIMESTAMP": timestamp,
    "CB-VERSION": "2021-01-01"
}

print("📞 Testing API call to Coinbase /v2/user...")
response = requests.get("https://api.coinbase.com/v2/user", headers=headers)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✅ Authentication successful!")
    user_data = response.json()["data"]
    print(f"   User: {user_data.get('name', 'N/A')}")
    print(f"   Email: {user_data.get('email', 'N/A')}")
    print("\n🎉 Your API keys work! You can now run coinbase_agent.py")
else:
    print("❌ Authentication failed!")
    print(f"Response: {response.text[:500]}")
    print("\n⚠️  This might mean:")
    print("1. These are CDP API keys (for Server Wallets), not Coinbase Account API keys")
    print("2. You need to create separate keys at: https://www.coinbase.com/settings/api")
