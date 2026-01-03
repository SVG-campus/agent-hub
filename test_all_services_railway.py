"""Comprehensive test of ALL Agent Hub services on Railway"""
import asyncio
import requests
import json
from cdp import CdpClient
from cdp.evm_transaction_types import TransactionRequestEIP1559
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
BASE_SEPOLIA_RPC = "https://sepolia.base.org"
API_URL = "https://web-production-4833.up.railway.app"  # Railway production!

w3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))

class CDPPaymentAgent:
    def __init__(self):
        self.cdp_client = None
        self.wallet_address = None
        self.account = None
        self.total_spent = 0.0

    async def initialize(self):
        print("🤖 Initializing CDP Payment Agent...\n")

        self.cdp_client = CdpClient()

        print("📝 Creating payment wallet...")
        self.account = await self.cdp_client.evm.create_account()
        self.wallet_address = self.account.address
        print(f"✅ Wallet: {self.wallet_address}\n")

        # Request ETH for gas
        print("⛽ Requesting testnet ETH for gas...")
        eth_faucet_tx = await self.cdp_client.evm.request_faucet(
            address=self.wallet_address,
            network="base-sepolia",
            token="eth"
        )
        print(f"✅ ETH Faucet TX: https://sepolia.basescan.org/tx/{eth_faucet_tx}")
        print("⏳ Waiting for ETH confirmation...")
        w3.eth.wait_for_transaction_receipt(eth_faucet_tx, timeout=120)
        print("✅ ETH confirmed\n")

        # Request USDC
        print("🚰 Requesting testnet USDC...")
        usdc_faucet_tx = await self.cdp_client.evm.request_faucet(
            address=self.wallet_address,
            network="base-sepolia",
            token="usdc"
        )
        print(f"✅ USDC Faucet TX: https://sepolia.basescan.org/tx/{usdc_faucet_tx}")
        print("⏳ Waiting for USDC confirmation...")
        w3.eth.wait_for_transaction_receipt(usdc_faucet_tx, timeout=120)

        # Check balance
        usdc_abi = [{
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }]

        usdc_contract = w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)

        for i in range(10):
            balance = usdc_contract.functions.balanceOf(self.wallet_address).call()
            usdc_balance = balance / 1_000_000

            if usdc_balance > 0:
                print(f"💵 USDC Balance: {usdc_balance} USDC\n")
                return True

            print(f"   Checking USDC balance... ({i+1}/10)")
            await asyncio.sleep(5)

        print("⚠️  USDC not received yet. Continuing anyway...\n")
        return True

    async def send_usdc(self, to_address, amount_usd):
        print(f"💸 Sending ${amount_usd} USDC to {to_address}...")

        amount_units = int(amount_usd * 1_000_000)

        usdc_abi = [{
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }]

        contract = w3.eth.contract(address=USDC_CONTRACT, abi=usdc_abi)
        transfer_data = contract.functions.transfer(to_address, amount_units).build_transaction({
            "from": self.wallet_address,
            "nonce": w3.eth.get_transaction_count(self.wallet_address)
        })["data"]

        tx_hash = await self.cdp_client.evm.send_transaction(
            address=self.wallet_address,
            transaction=TransactionRequestEIP1559(
                to=USDC_CONTRACT,
                data=transfer_data,
                gas=100000
            ),
            network="base-sepolia"
        )

        print(f"✅ Payment sent: https://sepolia.basescan.org/tx/{tx_hash}")
        print("⏳ Waiting for confirmation...")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print("✅ Confirmed!")

        self.total_spent += amount_usd
        return tx_hash

    async def call_paid_api(self, endpoint, payload, service_name):
        print(f"\n{'='*70}")
        print(f"🧪 Testing: {service_name}")
        print(f"{'='*70}")
        print(f"📡 Endpoint: {endpoint}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")

        try:
            response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=30)
        except Exception as e:
            print(f"❌ Connection Error: {str(e)}\n")
            return None

        if response.status_code == 200:
            print("✅ Success (no payment required in test mode)")
            result = response.json()
            print(f"📊 Result Preview: {str(result)[:200]}...\n")
            return result

        if response.status_code == 402:
            payment_info = response.json()["detail"]
            amount_usd = payment_info["amount_usd"]
            recipient = payment_info["instructions"]["step_1"].split("to ")[1].split(" on")[0]

            print(f"💰 Payment Required: ${amount_usd} USDC")

            tx_hash = await self.send_usdc(recipient, amount_usd)

            print("\n🔄 Retrying with payment signature...")
            response = requests.post(
                f"{API_URL}{endpoint}",
                json=payload,
                headers={"PAYMENT-SIGNATURE": tx_hash},
                timeout=30
            )

            if response.status_code == 200:
                print("✅ Payment verified! Service delivered!")
                result = response.json()
                print(f"📊 Result Preview: {str(result)[:200]}...\n")
                return result
            else:
                print(f"❌ Failed: {response.status_code} - {response.text[:200]}\n")
                return None

        if response.status_code == 503:
            print(f"⚠️  Service Unavailable: {response.json().get('detail', 'Unknown error')}\n")
            return None

        print(f"❌ Unexpected status: {response.status_code}\n")
        return None

    async def close(self):
        if self.cdp_client:
            await self.cdp_client.close()

async def main():
    print("\n" + "="*70)
    print("🚀 AGENT HUB - COMPREHENSIVE SERVICE TEST (Railway)")
    print("="*70)
    print(f"🌐 Testing against: {API_URL}")
    print("="*70)

    agent = CDPPaymentAgent()

    try:
        await agent.initialize()

        # Test all services
        tests = [
            # Core Services
            ("/agent/sentiment", {"text": "AI agents paying for services is revolutionary!"}, "Sentiment Analysis"),
            ("/agent/translate", {"text": "Hello world", "target_language": "es"}, "Translation"),
            ("/agent/summarize", {"text": "AI agents can autonomously pay for API services using cryptocurrency on blockchain networks."}, "Summarization"),

            # Data Services
            ("/agent/scrape", {"url": "https://example.com"}, "Web Scraping"),
            ("/agent/extract", {"url": "https://example.com", "extraction_schema": {"title": "string"}}, "Data Extraction"),

            # Research & Content
            ("/agent/research", {"query": "AI agent payments", "max_sources": 3}, "Research"),
            ("/agent/content-gen", {"topic": "AI Automation", "word_count": 200}, "Content Generation"),

            # Code & SEO
            ("/agent/code-review", {"code": "def hello():\n    print('world')", "language": "python"}, "Code Review"),
            ("/agent/seo-optimize", {"content": "AI agents are powerful", "target_keywords": ["AI", "automation"]}, "SEO Optimization"),

            # Business Analysis
            ("/agent/swot", {"subject": "AI Agents", "industry": "Technology"}, "SWOT Analysis"),
            ("/agent/competitive-analysis", {"company_domain": "example.com"}, "Competitive Analysis"),
        ]

        results = []
        for endpoint, payload, name in tests:
            try:
                result = await agent.call_paid_api(endpoint, payload, name)
                results.append((name, "✅ SUCCESS" if result else "❌ FAILED"))
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
                results.append((name, f"❌ ERROR: {str(e)}"))

            await asyncio.sleep(2)  # Rate limit between requests

        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        for name, status in results:
            print(f"{status:15} | {name}")

        print("\n" + "="*70)
        print(f"💰 Total Spent: ${agent.total_spent:.2f} USDC")
        print(f"🎯 Successful Tests: {sum(1 for _, s in results if '✅' in s)}/{len(results)}")
        print("="*70)

    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
