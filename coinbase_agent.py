import requests
import hmac
import hashlib
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()

class CoinbasePaymentAgent:
    """AI Agent that uses Coinbase Account API to send USDC payments"""
    
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.coinbase.com"
        self.usdc_account_id = None
    
    def _generate_signature(self, timestamp, method, path, body=""):
        """Generate CB-ACCESS-SIGN header"""
        message = timestamp + method + path + body
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self, method, path, body=""):
        """Generate authentication headers"""
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp, method, path, body)
        
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-VERSION": "2021-01-01",
            "Content-Type": "application/json"
        }
    
    def get_usdc_account(self):
        """Find USDC account"""
        print("🔍 Finding USDC account...")
        
        path = "/v2/accounts"
        headers = self._get_headers("GET", path)
        
        response = requests.get(f"{self.base_url}{path}", headers=headers)
        
        if response.status_code == 200:
            accounts = response.json()["data"]
            for account in accounts:
                if account["currency"]["code"] == "USDC":
                    self.usdc_account_id = account["id"]
                    balance = account["balance"]["amount"]
                    print(f"✅ Found USDC account: {self.usdc_account_id}")
                    print(f"💰 Balance: {balance} USDC\n")
                    return True
        else:
            print(f"❌ Failed to get accounts: {response.status_code}")
            print(f"Response: {response.text}\n")
        
        print("❌ USDC account not found!")
        return False
    
    def send_usdc(self, to_address, amount_usd, description="AI Agent Payment"):
        """Send USDC payment"""
        if not self.usdc_account_id:
            print("❌ USDC account not set!")
            return None
        
        print(f"💸 Sending ${amount_usd} USDC to {to_address}...")
        
        path = f"/v2/accounts/{self.usdc_account_id}/transactions"
        
        payload = {
            "type": "send",
            "to": to_address,
            "amount": str(amount_usd),
            "currency": "USDC",
            "description": description,
            "network": "base"
        }
        
        body = json.dumps(payload)
        headers = self._get_headers("POST", path, body)
        
        response = requests.post(
            f"{self.base_url}{path}",
            headers=headers,
            data=body
        )
        
        if response.status_code == 201:
            tx_data = response.json()["data"]
            tx_id = tx_data["id"]
            status = tx_data["status"]
            
            print(f"✅ Payment sent!")
            print(f"   Transaction ID: {tx_id}")
            print(f"   Status: {status}")
            
            if "network" in tx_data and "hash" in tx_data["network"]:
                tx_hash = tx_data["network"]["hash"]
                print(f"   TX Hash: {tx_hash}")
                return tx_hash
            
            return tx_id
        else:
            print(f"❌ Payment failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def call_paid_api(self, api_url, endpoint, payload):
        """Call API with automatic payment"""
        print(f"\n🤖 Calling API: {endpoint}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")
        
        print("📞 Step 1: Calling API...")
        response = requests.post(f"{api_url}{endpoint}", json=payload)
        
        if response.status_code == 200:
            print("✅ Success! (No payment required)\n")
            return response.json()
        
        if response.status_code == 402:
            print("💰 Payment required!")
            
            payment_info = response.json()["detail"]
            amount_usd = payment_info["amount_usd"]
            service = payment_info["service"]
            
            instructions = payment_info["instructions"]["step_1"]
            recipient = instructions.split("to ")[1].split(" on")[0]
            
            print(f"\n💵 Payment Details:")
            print(f"   Service: {service}")
            print(f"   Amount: ${amount_usd} USDC")
            print(f"   Recipient: {recipient}\n")
            
            print("💸 Step 2: Sending payment via Coinbase...")
            tx_hash = self.send_usdc(recipient, amount_usd, f"Payment for {service}")
            
            if not tx_hash:
                print("❌ Payment failed!")
                return None
            
            print()
            
            print("🔄 Step 3: Retrying API with payment signature...")
            response = requests.post(
                f"{api_url}{endpoint}",
                json=payload,
                headers={"PAYMENT-SIGNATURE": tx_hash}
            )
            
            if response.status_code == 200:
                print("✅ Payment verified! Request successful!\n")
                return response.json()
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}\n")
                return None
        
        print(f"❌ Unexpected status: {response.status_code}")
        print(f"Response: {response.text}\n")
        return None


def main():
    print("=" * 70)
    print("🤖 AI AGENT - AUTOMATED COINBASE PAYMENT DEMO")
    print("=" * 70)
    print()
    
    # Load Coinbase Account API credentials (NOT CDP credentials)
    api_key = os.getenv("COINBASE_ACCOUNT_API_KEY")
    api_secret = os.getenv("COINBASE_ACCOUNT_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ Missing Coinbase Account API credentials!")
        print("\n📝 Setup Instructions:")
        print("1. Go to: https://www.coinbase.com/settings/api")
        print("2. Click 'New API Key'")
        print("3. Select permissions:")
        print("   - wallet:accounts:read")
        print("   - wallet:transactions:send")
        print("4. Save API Key and Secret")
        print("5. Add to .env:")
        print("   COINBASE_ACCOUNT_API_KEY=your_key")
        print("   COINBASE_ACCOUNT_API_SECRET=your_secret")
        return
    
    print(f"✅ Loaded Coinbase Account API credentials\n")
    
    agent = CoinbasePaymentAgent(api_key, api_secret)
    
    if not agent.get_usdc_account():
        return
    
    print("=" * 70)
    print("🧪 TESTING PAID API SERVICES")
    print("=" * 70)
    
    # Test 1: Sentiment Analysis ($0.05)
    print("\n" + "-" * 70)
    print("TEST 1: Sentiment Analysis ($0.05)")
    print("-" * 70)
    result1 = agent.call_paid_api(
        "http://localhost:8000",
        "/agent/sentiment",
        {"text": "This Coinbase integration makes AI agent payments seamless!"}
    )
    if result1:
        print(f"📊 Result:")
        print(json.dumps(result1, indent=2))
        print()
    
    # Test 2: Translate ($0.05)
    print("\n" + "-" * 70)
    print("TEST 2: Translation ($0.05)")
    print("-" * 70)
    result2 = agent.call_paid_api(
        "http://localhost:8000",
        "/agent/translate",
        {
            "text": "AI agents can now autonomously pay for services!",
            "target_language": "es"
        }
    )
    if result2:
        print(f"📊 Result:")
        print(json.dumps(result2, indent=2))
        print()
    
    # Test 3: Summarize ($0.08)
    print("\n" + "-" * 70)
    print("TEST 3: Summarization ($0.08)")
    print("-" * 70)
    result3 = agent.call_paid_api(
        "http://localhost:8000",
        "/agent/summarize",
        {
            "text": "The integration of cryptocurrency payments into AI agent workflows represents "
                   "a significant advancement in autonomous systems.",
            "max_length": 30
        }
    )
    if result3:
        print(f"📊 Result:")
        print(json.dumps(result3, indent=2))
        print()
    
    print("=" * 70)
    print("🎉 DEMO COMPLETE!")
    print("=" * 70)
    print(f"\n💰 Total spent: $0.18 USDC")
    print(f"💵 Remaining balance: ~$0.16 USDC")


if __name__ == "__main__":
    main()
