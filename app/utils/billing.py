import os
from fastapi import HTTPException, Request, Header
import hashlib
import uuid

COINBASE_BASE_ADDRESS = os.getenv("COINBASE_BASE_ADDRESS")
PAYMENT_AMOUNT_USD = 0.002  # Per scrape

async def check_agent_payment(request: Request, x_agent_id: str = Header(None)):
    # Generate unique payment address per request/agent
    request_id = str(uuid.uuid4())
    payment_hash = hashlib.sha256(f"{x_agent_id}{request_id}".encode()).hexdigest()
    agent_address = f"0x{payment_hash[:40]}"  # Deterministic per agent+request
    
    # For MVP: Assume agents pay to main address, verify later
    # Production: Check blockchain tx via Alchemy API
    
    detail = {
        "error": "Payment Required",
        "type": "x402",
        "request_id": request_id,
        "agent_id": x_agent_id or "anonymous",
        "amount_usd": PAYMENT_AMOUNT_USD,
        "amount_usdc": PAYMENT_AMOUNT_USD,
        "address": COINBASE_BASE_ADDRESS,  # Collect all here
        "chain": "base",
        "memo": f"{x_agent_id[:8]}-{request_id[:8]}"
    }
    
    raise HTTPException(status_code=402, detail=detail)
