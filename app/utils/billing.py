import os
import uuid
import stripe
import time
from fastapi import HTTPException, Request

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
SUBSCRIPTION_ITEM_ID = "si_Tij7RECZ3mF3Zc"  # From Stripe dashboard subscription
COINBASE_BASE_ADDRESS = os.getenv("COINBASE_BASE_ADDRESS")

async def check_billing(request: Request):
    api_key = request.headers.get("X-API-Key")
    
    if api_key and api_key.startswith("sk_"):
        # Record REAL Stripe usage
        stripe.UsageRecord.create(
            subscription_item=SUBSCRIPTION_ITEM_ID,
            quantity=1,  # 1 API call
            timestamp=int(time.time()),
            action="increment"
        )
        print(f"💳 Stripe usage recorded: {api_key[:8]}...")
        return
    
    # x402 Crypto
    raise HTTPException(
        status_code=402,
        detail={
            "error": "Payment Required",
            "type": "x402",
            "amount": 0.01,
            "currency": "USDC",
            "address": COINBASE_BASE_ADDRESS,
            "chain": "base"
        }
    )
