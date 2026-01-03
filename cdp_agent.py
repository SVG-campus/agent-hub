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
API_URL = "http://localhost:8000"

w3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))


class CDPPaymentAgent:
    """AI Agent that uses CDP SDK to send USDC payments"""
    
    def __init__(self):
        self.cdp_client = None
        self.wallet_address = None
        self.account = None
    
    async def initialize(self):
        """Initialize CDP client and create/load wallet"""
        print("🤖 Initializing CDP Payment Agent...\n")
        
        self.cdp_client = CdpClient()
        
        # For this demo, create a fresh wallet and fund it
        print("📝 Creating payment wallet...")
        self.account = await self.cdp_client.evm.create_account()
        self.wallet_address = self.account.address
        print(f"✅ Wallet: {self.wallet_address}")
        
        print("\n�� Funding wallet with testnet USDC...")
        faucet_tx = await self.cdp_client.evm.request_faucet(
            address=self.wallet_address,
            network="base-sepolia",
            token="usdc"
        )
        print(f"✅ Funded! TX: https://sepolia.basescan.org/tx/{faucet_tx}")
        
        print("⏳ Waiting for confirmation...")
        w3.eth.wait_for_transaction_receipt(faucet_tx)
        print("✅ Ready!\n")
    
    async def send_usdc(self, to_address, amount_usd):
        """Send USDC payment via CDP"""
        print(f"💸 Sending ${amount_usd} USDC to {to_address}...")
        
        amount_units = int(amount_usd * 1_000_000)  # USDC has 6 decimals
        
        # Build transfer
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
        
        # Send via CDP
        tx_hash = await self.cdp_client.evm.send_transaction(
            address=self.wallet_address,
            transaction=TransactionRequestEIP1559(
                to=USDC_CONTRACT,
                data=transfer_data,
                gas=100000
            ),
            network="base-sepolia"
        )
        
        print(f"✅ Payment sent!")
        print(f"🔗 TX: https://sepolia.basescan.org/tx/{tx_hash}")
        
        # Wait for confirmation
        print("⏳ Waiting for confirmation...")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print("✅ Payment confirmed!")
        
        return tx_hash
    
    async def call_paid_api(self, endpoint, payload):
        """Call API with automatic payment"""
        print(f"\n🤖 Calling API: {endpoint}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")
        
        print("📞 Step 1: Calling API...")
        response = requests.post(f"{API_URL}{endpoint}", json=payload)
        
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
            
            print("💸 Step 2: Sending payment via CDP...")
            tx_hash = await self.send_usdc(recipient, amount_usd)
            
            print()
            
            print("🔄 Step 3: Retrying API with payment signature...")
            response = requests.post(
                f"{API_URL}{endpoint}",
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
        return None
    
    async def close(self):
        """Close CDP client"""
        if self.cdp_client:
            await self.cdp_client.close()


async def main():
    print("=" * 70)
    print("🤖 AI AGENT - CDP AUTOMATED PAYMENT DEMO")
    print("=" * 70)
    print()
    
    agent = CDPPaymentAgent()
    await agent.initialize()
    
    print("=" * 70)
    print("🧪 TESTING PAID API SERVICES")
    print("=" * 70)
    
    # Test 1: Sentiment Analysis ($0.05)
    print("\n" + "-" * 70)
    print("TEST 1: Sentiment Analysis ($0.05)")
    print("-" * 70)
    result1 = await agent.call_paid_api(
        "/agent/sentiment",
        {"text": "CDP makes AI agent payments so easy!"}
    )
    if result1:
        print(f"📊 Result:")
        print(json.dumps(result1, indent=2))
        print()
    
    # Test 2: Translate ($0.05)
    print("\n" + "-" * 70)
    print("TEST 2: Translation ($0.05)")
    print("-" * 70)
    result2 = await agent.call_paid_api(
        "/agent/translate",
        {
            "text": "Autonomous AI agents can now pay for services!",
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
    result3 = await agent.call_paid_api(
        "/agent/summarize",
        {
            "text": "The integration of cryptocurrency payments into AI workflows enables "
                   "autonomous machine-to-machine commerce and automated service consumption.",
            "max_length": 20
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
    
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
