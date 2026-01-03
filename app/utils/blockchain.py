import os
from web3 import Web3
from typing import Optional, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Base Network Configuration
BASE_RPC_URL = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
USDC_ADDRESS = os.getenv("USDC_CONTRACT_ADDRESS", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
PAYMENT_WALLET = os.getenv("PAYMENT_WALLET_ADDRESS", "")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

# USDC Contract ABI (minimal - just for Transfer events)
USDC_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

usdc_contract = w3.eth.contract(address=Web3.to_checksum_address(USDC_ADDRESS), abi=USDC_ABI)


async def verify_payment(
    from_address: str,
    amount_usd: float,
    tx_hash: Optional[str] = None,
    timeout_minutes: int = 5
) -> Dict:
    """
    Verify USDC payment on Base blockchain
    
    Args:
        from_address: Sender's wallet address
        amount_usd: Expected payment amount in USD
        tx_hash: Optional specific transaction hash to verify
        timeout_minutes: How far back to search for payment
        
    Returns:
        Dict with verification status and details
    """
    try:
        if not PAYMENT_WALLET:
            return {
                "verified": False,
                "error": "Payment wallet not configured",
                "message": "Server payment address not set"
            }
        
        # Convert addresses to checksum format
        from_addr = Web3.to_checksum_address(from_address)
        to_addr = Web3.to_checksum_address(PAYMENT_WALLET)
        
        # USDC has 6 decimals
        expected_amount = int(amount_usd * 1_000_000)
        
        # If specific tx_hash provided, verify it directly
        if tx_hash:
            return await verify_specific_transaction(tx_hash, from_addr, to_addr, expected_amount)
        
        # Otherwise, search recent blocks for payment
        return await search_recent_payments(from_addr, to_addr, expected_amount, timeout_minutes)
        
    except Exception as e:
        return {
            "verified": False,
            "error": str(e),
            "message": "Payment verification failed"
        }


async def verify_specific_transaction(tx_hash: str, from_addr: str, to_addr: str, expected_amount: int) -> Dict:
    """Verify a specific transaction hash"""
    try:
        # Get transaction receipt
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        if not receipt:
            return {
                "verified": False,
                "error": "Transaction not found",
                "tx_hash": tx_hash
            }
        
        # Check if transaction was successful
        if receipt['status'] != 1:
            return {
                "verified": False,
                "error": "Transaction failed",
                "tx_hash": tx_hash
            }
        
        # Parse logs for USDC Transfer event
        for log in receipt['logs']:
            if log['address'].lower() == USDC_ADDRESS.lower():
                try:
                    # Decode Transfer event
                    transfer_event = usdc_contract.events.Transfer().process_log(log)
                    event_from = transfer_event['args']['from']
                    event_to = transfer_event['args']['to']
                    event_value = transfer_event['args']['value']
                    
                    # Verify sender, recipient, and amount
                    if (event_from.lower() == from_addr.lower() and
                        event_to.lower() == to_addr.lower() and
                        event_value >= expected_amount):
                        
                        return {
                            "verified": True,
                            "tx_hash": tx_hash,
                            "amount_paid": event_value / 1_000_000,
                            "from": event_from,
                            "to": event_to,
                            "block_number": receipt['blockNumber']
                        }
                except:
                    continue
        
        return {
            "verified": False,
            "error": "No matching USDC transfer found in transaction",
            "tx_hash": tx_hash
        }
        
    except Exception as e:
        return {
            "verified": False,
            "error": f"Transaction verification error: {str(e)}",
            "tx_hash": tx_hash
        }


async def search_recent_payments(from_addr: str, to_addr: str, expected_amount: int, timeout_minutes: int) -> Dict:
    """Search recent blocks for matching payment"""
    try:
        current_block = w3.eth.block_number
        
        # Base produces ~2 blocks per second, so check last N blocks
        blocks_to_check = timeout_minutes * 60 * 2  # 2 blocks/sec * 60 sec * N minutes
        from_block = max(0, current_block - blocks_to_check)
        
        print(f"🔍 Searching blocks {from_block} to {current_block} for payment...")
        
        # Get Transfer events to our wallet
        transfer_filter = usdc_contract.events.Transfer.create_filter(
            fromBlock=from_block,
            toBlock='latest',
            argument_filters={'to': to_addr}
        )
        
        events = transfer_filter.get_all_entries()
        
        # Check each transfer
        for event in events:
            event_from = event['args']['from']
            event_value = event['args']['value']
            
            # Match sender and amount (allow ±1% tolerance for fees)
            if (event_from.lower() == from_addr.lower() and
                event_value >= expected_amount * 0.99):
                
                tx_hash = event['transactionHash'].hex()
                
                return {
                    "verified": True,
                    "tx_hash": tx_hash,
                    "amount_paid": event_value / 1_000_000,
                    "from": event_from,
                    "to": to_addr,
                    "block_number": event['blockNumber']
                }
        
        return {
            "verified": False,
            "error": "No matching payment found",
            "message": f"Searched last {timeout_minutes} minutes, no USDC transfer found from {from_addr}",
            "searched_blocks": f"{from_block} to {current_block}"
        }
        
    except Exception as e:
        return {
            "verified": False,
            "error": f"Block search error: {str(e)}"
        }


async def get_wallet_balance(address: str) -> Dict:
    """Get USDC balance for a wallet"""
    try:
        checksum_addr = Web3.to_checksum_address(address)
        
        # Call balanceOf function
        balance_wei = usdc_contract.functions.balanceOf(checksum_addr).call()
        balance_usd = balance_wei / 1_000_000
        
        return {
            "address": address,
            "balance_usdc": balance_usd,
            "balance_wei": balance_wei
        }
    except Exception as e:
        return {
            "error": str(e)
        }


def check_connection() -> Dict:
    """Check if connected to Base network"""
    try:
        is_connected = w3.is_connected()
        chain_id = w3.eth.chain_id if is_connected else None
        latest_block = w3.eth.block_number if is_connected else None
        
        return {
            "connected": is_connected,
            "chain_id": chain_id,
            "chain_name": "Base Mainnet" if chain_id == 8453 else "Unknown",
            "latest_block": latest_block,
            "usdc_contract": USDC_ADDRESS,
            "payment_wallet": PAYMENT_WALLET
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }
