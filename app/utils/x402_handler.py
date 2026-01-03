import os
from typing import Dict, Optional
from fastapi import HTTPException, Request
from dotenv import load_dotenv
import json
import base64

load_dotenv()

# x402 Configuration
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402-facilitator.cdp.coinbase.com")
SERVER_WALLET = os.getenv("SERVER_WALLET_ADDRESS", "")
NETWORK = os.getenv("NETWORK", "base-sepolia")

# Convert network to CAIP-2 format
CHAIN_ID = "eip155:84532"  # Base Sepolia


def generate_payment_required_header(amount_usd: float, service_id: str) -> str:
    """
    Generate x402 PAYMENT-REQUIRED header
    Format: <facilitator_url>; amount=<amount>; network=<caip2>; address=<recipient>; nonce=<random>
    """
    import uuid
    
    # USDC has 6 decimals
    amount_usdc = int(amount_usd * 1_000_000)
    nonce = str(uuid.uuid4())
    
    payment_header = (
        f"{FACILITATOR_URL}; "
        f"amount={amount_usdc}; "
        f"network={CHAIN_ID}; "
        f"address={SERVER_WALLET}; "
        f"nonce={nonce}; "
        f"service={service_id}"
    )
    
    return payment_header


async def verify_x402_payment(request: Request, amount_usd: float, service_id: str) -> Dict:
    """
    Verify x402 payment using CDP facilitator
    
    Expected headers:
    - PAYMENT-SIGNATURE: Base64 encoded payment proof from client
    """
    
    # Check if payment signature is present
    payment_signature = request.headers.get("PAYMENT-SIGNATURE")
    
    if not payment_signature:
        # No payment - return 402 with payment instructions
        payment_required_header = generate_payment_required_header(amount_usd, service_id)
        
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Payment required",
                "payment_header": payment_required_header,
                "amount_usd": amount_usd,
                "service": service_id,
                "instructions": {
                    "step_1": f"Send {amount_usd} USDC to {SERVER_WALLET} on Base Sepolia",
                    "step_2": "Include PAYMENT-SIGNATURE header in request",
                    "step_3": "Retry request with signature"
                }
            },
            headers={"PAYMENT-REQUIRED": payment_required_header}
        )
    
    # Verify payment signature with facilitator
    try:
        verification_result = await verify_with_facilitator(payment_signature, amount_usd, service_id)
        
        if not verification_result.get("verified"):
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Payment verification failed",
                    "reason": verification_result.get("error"),
                    "amount_usd": amount_usd
                }
            )
        
        return {
            "status": "paid",
            "amount_usd": amount_usd,
            "tx_hash": verification_result.get("tx_hash"),
            "verified": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Payment processing error",
                "message": str(e)
            }
        )


async def verify_with_facilitator(payment_signature: str, amount_usd: float, service_id: str) -> Dict:
    """
    Call CDP x402 facilitator to verify payment
    """
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FACILITATOR_URL}/verify",
                json={
                    "signature": payment_signature,
                    "amount": int(amount_usd * 1_000_000),
                    "network": CHAIN_ID,
                    "recipient": SERVER_WALLET,
                    "service_id": service_id
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "verified": True,
                    "tx_hash": result.get("transaction_hash"),
                    "amount": result.get("amount")
                }
            else:
                return {
                    "verified": False,
                    "error": f"Facilitator returned {response.status_code}"
                }
                
    except Exception as e:
        return {
            "verified": False,
            "error": f"Facilitator error: {str(e)}"
        }


def check_wallet_configured() -> bool:
    """Check if server wallet is configured"""
    return bool(SERVER_WALLET and SERVER_WALLET != "")
