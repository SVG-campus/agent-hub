import asyncio
import requests
import json
from cdp import CdpClient
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# USDC Contract on Base Sepolia
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
BASE_SEPOLIA_RPC = "https://sepolia.base.org"

w3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))


class AIAgent:
    """Simple AI Agent that can pay for API services using x402"""
    
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        self.wallet_address = None
        self.cdp_client = None
        self.account = None
    
    async def initialize(self, use_existing_wallet=None):
        """Initialize the agent with a wallet"""
        print("🤖 Initializing AI Agent...\n")
        
        self.cdp_client = CdpClient()
        
        if use_existing_wallet:
            # Use existing wallet address (you'll need to manage keys separately)
            self.wallet_address = use_existing_wallet
            print(f"✅ Using existing wallet: {self.wallet_address}")
        else:
            # Create new account
            self.account = await self.cdp_client.evm.create_account()
            self.wallet_address = self.account.address
            print(f"✅ Created new wallet: {self.wallet_address}")
            
            # Fund with testnet USDC
            print("🚰 Requesting testnet USDC...")
            faucet_hash = await self.cdp_client.evm.request_faucet(
                address=self.wallet_address,
                network="base-sepolia",
                token="usdc"
            )
            print(f"✅ Funded! TX: https://sepolia.basescan.org/tx/{faucet_hash}")
            
            # Wait for confirmation
            print("⏳ Waiting for confirmation...")
            w3.eth.wait_for_transaction_receipt(faucet_hash)
            print("✅ Wallet ready!\n")
    
    def call_api(self, endpoint, payload, headers=None):
        """Make API call"""
        url = f"{self.api_base_url}{endpoint}"
        if headers is None:
            headers = {}
        
        response = requests.post(url, json=payload, headers=headers)
        return response
    
    async def pay_for_service(self, recipient, amount_usd):
        """Send USDC payment"""
        print(f"\n💸 Sending ${amount_usd} USDC to {recipient}...")
        
        # Convert USD to USDC units (6 decimals)
        amount_units = int(amount_usd * 1_000_000)
        
        # Build transfer transaction
        usdc_contract = w3.eth.contract(
            address=USDC_CONTRACT,
            abi=[{
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }]
        )
        
        transfer_data = usdc_contract.functions.transfer(
            recipient, 
            amount_units
        ).build_transaction({
            "from": self.wallet_address,
            "nonce": w3.eth.get_transaction_count(self.wallet_address),
            "gas": 100000,
            "gasPrice": w3.eth.gas_price
        })
        
        # Send transaction via CDP
        from cdp.evm_transaction_types import TransactionRequestEIP1559
        
        tx_hash = await self.cdp_client.evm.send_transaction(
            address=self.wallet_address,
            transaction=TransactionRequestEIP1559(
                to=USDC_CONTRACT,
                data=transfer_data["data"],
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
    
    async def paid_api_call(self, endpoint, payload):
        """Make a paid API call with automatic payment"""
        print(f"\n🤖 AI Agent calling: {endpoint}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        # Step 1: Try API call
        print("\n📞 Step 1: Calling API...")
        response = self.call_api(endpoint, payload)
        
        # Step 2: Check if payment required
        if response.status_code == 402:
            print("💰 Payment required!")
            
            payment_info = response.json()["detail"]
            amount_usd = payment_info["amount_usd"]
            service = payment_info["service"]
            
            # Extract recipient from instructions
            instructions = payment_info["instructions"]["step_1"]
            recipient = instructions.split("to ")[1].split(" on")[0]
            
            print(f"\n💵 Payment Details:")
            print(f"   Service: {service}")
            print(f"   Amount: ${amount_usd} USDC")
            print(f"   Recipient: {recipient}")
            
            # Step 3: Send payment
            tx_hash = await self.pay_for_service(recipient, amount_usd)
            
            # Step 4: Retry with payment signature
            print("\n🔄 Step 2: Retrying with payment signature...")
            response = self.call_api(
                endpoint, 
                payload, 
                headers={"PAYMENT-SIGNATURE": tx_hash}
            )
            
            if response.status_code == 200:
                print("✅ Payment verified! Request successful!\n")
                return response.json()
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        
        elif response.status_code == 200:
            print("✅ Request successful (no payment required)\n")
            return response.json()
        
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    async def close(self):
        """Close CDP client"""
        if self.cdp_client:
            await self.cdp_client.close()


async def main():
    print("=" * 60)
    print("🤖 AI AGENT - AUTOMATED PAYMENT DEMO")
    print("=" * 60)
    
    # Initialize agent
    agent = AIAgent(api_base_url="http://localhost:8000")
    
    # Option 1: Create new wallet
    # await agent.initialize()
    
    # Option 2: Use your existing wallet with $0.34 USDC
    # Replace with your actual wallet address from Coinbase
    await agent.initialize(use_existing_wallet="YOUR_WALLET_ADDRESS_HERE")
    
    print("\n" + "=" * 60)
    print("🧪 TESTING CHEAP SERVICES")
    print("=" * 60)
    
    # Test 1: Sentiment Analysis ($0.05)
    print("\n" + "-" * 60)
    print("TEST 1: Sentiment Analysis")
    print("-" * 60)
    result1 = await agent.paid_api_call(
        "/agent/sentiment",
        {"text": "This AI agent is incredible! It can pay for services automatically!"}
    )
    if result1:
        print(f"📊 Result: {json.dumps(result1, indent=2)}")
    
    # Test 2: Translate ($0.05)
    print("\n" + "-" * 60)
    print("TEST 2: Translation")
    print("-" * 60)
    result2 = await agent.paid_api_call(
        "/agent/translate",
        {
            "text": "Hello, I am an AI agent that can pay for services!",
            "target_language": "es"
        }
    )
    if result2:
        print(f"📊 Result: {json.dumps(result2, indent=2)}")
    
    # Test 3: Summarize ($0.08)
    print("\n" + "-" * 60)
    print("TEST 3: Summarization")
    print("-" * 60)
    result3 = await agent.paid_api_call(
        "/agent/summarize",
        {
            "text": "Artificial intelligence is transforming how we interact with technology. "
                   "From automated customer service to advanced data analysis, AI agents are "
                   "becoming increasingly capable. This agent can autonomously pay for services "
                   "using cryptocurrency, enabling true machine-to-machine commerce.",
            "max_length": 50
        }
    )
    if result3:
        print(f"📊 Result: {json.dumps(result3, indent=2)}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    
    # Close client
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
