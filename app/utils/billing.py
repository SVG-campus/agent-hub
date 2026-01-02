import os
import stripe
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse

# Configure Stripe
stripe.api_key = os.getenv("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")
STRIPE_PRICE_ID = os.getenv("price_1SlGmMDScMyEC9pqUekZMpWZ")

async def check_billing(request: Request):
    api_key = request.headers.get("X-API-Key")

    # 1. HUMAN/DEV PATH: Metered Billing via Stripe
    if api_key and api_key.startswith("sk_"): 
        # In prod, validate this key against your DB of customers
        # Here we simulate logging usage to Stripe
        try:
            # Create a usage record (async in background recommended for prod)
            # stripe.SubscriptionItem.create_usage_record(...)
            print(f"Billing event recorded for key: {api_key}")
            return True
        except Exception as e:
            print(f"Stripe Error: {e}")
            return True # Fail open or closed depending on preference

    # 2. AGENT PATH: x402 Payment Required
    # If no key, or explicit "Prefer: payment=x402" header
    # We return the 402 status code which Agents recognize
    
    payment_details = {
        "error": "Payment Required",
        "type": "x402_payment_required",
        "detail": "Please pay 0.01 USDC to access this resource.",
        "payment_info": {
            "amount": 0.01,
            "currency": "USDC",
            "address": "0xF0f61cB32d7D963B24a500E1D484b8e1e8fddD20", # Replace with dynamic address generation
            "chain": "base"
        }
    }
    
    # Return a JSONResponse with 402 status
    raise HTTPException(status_code=402, detail=payment_details)
