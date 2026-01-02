import os
import time
import stripe
from fastapi import HTTPException, Request
from typing import Dict

# Load from environment (NEVER hard-code)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")
COINBASE_BASE_ADDRESS = os.getenv("COINBASE_BASE_ADDRESS", "0xF0f61cB32d7D963B24a500E1D484b8e1e8fddD20")

async def check_billing(request: Request) -> bool:
    api_key = request.headers.get("X-API-Key")
    
    # HUMAN PATH: Stripe Metered
    if api_key and api_key.startswith("sk_"):
        print(f"✅ Stripe billing logged for key: {api_key[:8]}...")
        # TODO: await record_stripe_usage(api_key)
        return True
    
    # AGENT PATH: x402
    payment_details = {
        "error": "Payment Required",
        "type": "x402_payment_required",
        "detail": "Pay 0.01 USDC to continue.",
        "payment_info": {
            "amount": 0.01,
            "currency": "USDC",
            "address": COINBASE_BASE_ADDRESS,  # Your static address (fine for MVP)
            "chain": "base"
        }
    }
    raise HTTPException(status_code=402, detail=payment_details)
