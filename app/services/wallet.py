from coinbase.rest import RESTClient
from web3 import Web3
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# Initialize Coinbase client
client = RESTClient(
    api_key=os.getenv("CDP_API_KEY"),
    api_secret=os.getenv("CDP_API_SECRET")
)

# In-memory wallet storage (replace with database in production)
WALLETS = {}

async def create_agent_wallet(agent_id: str) -> dict:
    """Create a new Base network wallet for an agent"""
    try:
        # Create wallet on Base (network_id = "base-sepolia" for testnet, "base-mainnet" for prod)
        wallet_data = {
            "name": f"agent_{agent_id}",
            "network_id": "base-sepolia"  # Change to "base-mainnet" for production
        }
        
        # Using CDP SDK to create wallet
        # Note: You'll need to adjust this based on actual CDP SDK methods
        wallet_id = f"wallet_{agent_id}_{datetime.now().timestamp()}"
        
        # Generate address (simplified - use actual CDP methods)
        w3 = Web3()
        account = w3.eth.account.create()
        
        wallet_info = {
            "wallet_id": wallet_id,
            "agent_id": agent_id,
            "address": account.address,
            "network": "base-sepolia",
            "created_at": datetime.now().isoformat()
        }
        
        WALLETS[wallet_id] = wallet_info
        
        return wallet_info
    except Exception as e:
        raise Exception(f"Failed to create wallet: {str(e)}")

async def get_wallet_balance(wallet_id: str) -> dict:
    """Get USDC and ETH balance for a wallet"""
    try:
        if wallet_id not in WALLETS:
            raise Exception("Wallet not found")
        
        wallet = WALLETS[wallet_id]
        address = wallet["address"]
        
        # Connect to Base RPC
        w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
        
        # Get ETH balance
        eth_balance = w3.eth.get_balance(address)
        eth_balance_ether = w3.from_wei(eth_balance, 'ether')
        
        # USDC contract on Base Sepolia
        usdc_address = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
        usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)
        usdc_balance = usdc_contract.functions.balanceOf(address).call()
        usdc_decimals = usdc_contract.functions.decimals().call()
        usdc_balance_formatted = usdc_balance / (10 ** usdc_decimals)
        
        return {
            "ETH": float(eth_balance_ether),
            "USDC": float(usdc_balance_formatted)
        }
    except Exception as e:
        raise Exception(f"Failed to get balance: {str(e)}")

async def send_transfer(wallet_id: str, to_address: str, amount: float, currency: str = "USDC") -> dict:
    """Send USDC or ETH to another address"""
    try:
        if wallet_id not in WALLETS:
            raise Exception("Wallet not found")
        
        wallet = WALLETS[wallet_id]
        
        # In production, you would:
        # 1. Load private key from secure storage
        # 2. Sign transaction
        # 3. Broadcast via CDP or Web3
        
        # Simplified for MVP
        tx_hash = f"0x{os.urandom(32).hex()}"
        
        transaction = {
            "tx_hash": tx_hash,
            "from": wallet["address"],
            "to": to_address,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        
        # Store transaction
        if "transactions" not in wallet:
            wallet["transactions"] = []
        wallet["transactions"].append(transaction)
        
        return transaction
    except Exception as e:
        raise Exception(f"Transfer failed: {str(e)}")

async def get_transactions(wallet_id: str, limit: int = 10) -> list:
    """Get transaction history for a wallet"""
    try:
        if wallet_id not in WALLETS:
            raise Exception("Wallet not found")
        
        wallet = WALLETS[wallet_id]
        transactions = wallet.get("transactions", [])
        
        return transactions[-limit:]
    except Exception as e:
        raise Exception(f"Faile
