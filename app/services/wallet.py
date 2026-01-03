from coinbase.rest import RESTClient
from web3 import Web3
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Initialize Coinbase client
client = RESTClient(
    api_key=os.getenv("CDP_API_KEY"),
    api_secret=os.getenv("CDP_API_SECRET")
)

# Persistent JSON storage
WALLET_FILE = Path("wallets_db.json")

def load_wallets():
    """Load wallets from JSON file"""
    if WALLET_FILE.exists():
        with open(WALLET_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_wallets(wallets):
    """Save wallets to JSON file"""
    with open(WALLET_FILE, 'w') as f:
        json.dump(wallets, f, indent=2)

async def create_agent_wallet(agent_id: str) -> dict:
    """Create a new Base network wallet for an agent"""
    try:
        wallets = load_wallets()
        
        wallet_id = f"wallet_{agent_id}_{int(datetime.now().timestamp())}"
        
        # Generate address
        w3 = Web3()
        account = w3.eth.account.create()
        
        wallet_info = {
            "wallet_id": wallet_id,
            "agent_id": agent_id,
            "address": account.address,
            "private_key": account.key.hex(),  # WARNING: Encrypt in production!
            "network": "base-sepolia",
            "created_at": datetime.now().isoformat(),
            "transactions": []
        }
        
        wallets[wallet_id] = wallet_info
        save_wallets(wallets)
        
        # Don't return private key in response
        response = wallet_info.copy()
        del response["private_key"]
        return response
    except Exception as e:
        raise Exception(f"Failed to create wallet: {str(e)}")

async def get_wallet_balance(wallet_id: str) -> dict:
    """Get USDC and ETH balance for a wallet"""
    try:
        wallets = load_wallets()
        if wallet_id not in wallets:
            raise Exception("Wallet not found")
        
        wallet = wallets[wallet_id]
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
        wallets = load_wallets()
        if wallet_id not in wallets:
            raise Exception("Wallet not found")
        
        wallet = wallets[wallet_id]
        
        # Simplified for MVP - generates mock tx
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
        wallet["transactions"].append(transaction)
        save_wallets(wallets)
        
        return transaction
    except Exception as e:
        raise Exception(f"Transfer failed: {str(e)}")

async def get_transactions(wallet_id: str, limit: int = 10) -> list:
    """Get transaction history for a wallet"""
    try:
        wallets = load_wallets()
        if wallet_id not in wallets:
            raise Exception("Wallet not found")
        
        wallet = wallets[wallet_id]
        transactions = wallet.get("transactions", [])
        
        return transactions[-limit:]
    except Exception as e:
        raise Exception(f"Failed to get transactions: {str(e)}")
