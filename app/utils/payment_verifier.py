import httpx
import os
from typing import Dict, Optional

BASE_RPC_URL = "https://mainnet.base.org"
WALLET_ADDRESS = os.getenv("COINBASE_BASE_ADDRESS")
USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # Base USDC

async def verify_usdc_payment(payment_id: str, expected_amount: int = 2000000) -> bool:
    """Verify USDC tx to wallet. expected_amount in micro-USDC (0.002 = 2000000)"""
    
    # Get recent txs to your wallet
    payload = {
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [{
            "fromBlock": "0x1",
            "toBlock": "latest",
            "category": ["erc20"],
            "withMetadata": True,
            "toAddress": WALLET_ADDRESS.lower()
        }],
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(BASE_RPC_URL, json=payload)
        transfers = resp.json()["result"]["transfers"]
        
        for tx in transfers[-10:]:  # Last 10 txs
            if (tx["rawContract"]["address"].lower() == USDC_CONTRACT.lower() and
                int(tx["rawContract"]["value"]) >= expected_amount and
                "memo" in tx["metadata"].get("blockExplorerUrl", "") and
                payment_id in tx["metadata"]["blockExplorerUrl"]):
                return True
        
        return False
