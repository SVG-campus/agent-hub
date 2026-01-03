from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(
    title="Agent Hub API",
    description="Agent-native financial API with x402 payment support",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class WalletRequest(BaseModel):
    agent_id: str
    
class TransferRequest(BaseModel):
    from_wallet_id: str
    to_address: str
    amount: float
    currency: str = "USDC"

class ScrapeRequest(BaseModel):
    url: str

# Import services
from app.services.wallet import create_agent_wallet, get_wallet_balance, send_transfer, get_transactions
from app.services.scraper import scrape_url
from app.utils.billing import check_agent_payment

# Health check
@app.get("/")
async def root():
    return {
        "status": "live",
        "service": "Agent Hub API",
        "endpoints": [
            "/agent/wallet",
            "/agent/balance/{wallet_id}",
            "/agent/transfer",
            "/agent/transactions/{wallet_id}",
            "/v1/scrape"
        ]
    }

# Phase 1: Core Financial Tools
@app.post("/agent/wallet")
async def create_wallet(payload: WalletRequest):
    """Create a new wallet for an agent"""
    try:
        wallet = await create_agent_wallet(payload.agent_id)
        return {
            "status": "success",
            "agent_id": payload.agent_id,
            "wallet_id": wallet["wallet_id"],
            "address": wallet["address"],
            "network": wallet["network"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/balance/{wallet_id}")
async def check_balance(wallet_id: str):
    """Check USDC and ETH balance"""
    try:
        balance = await get_wallet_balance(wallet_id)
        return {
            "status": "success",
            "wallet_id": wallet_id,
            "balances": balance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/transfer")
async def transfer_funds(payload: TransferRequest):
    """Send USDC to another address"""
    try:
        result = await send_transfer(
            wallet_id=payload.from_wallet_id,
            to_address=payload.to_address,
            amount=payload.amount,
            currency=payload.currency
        )
        return {
            "status": "success",
            "transaction_hash": result["tx_hash"],
            "amount": payload.amount,
            "currency": payload.currency,
            "to": payload.to_address
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/transactions/{wallet_id}")
async def list_transactions(wallet_id: str, limit: int = 10):
    """Get transaction history"""
    try:
        txs = await get_transactions(wallet_id, limit)
        return {
            "status": "success",
            "wallet_id": wallet_id,
            "transactions": txs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Existing x402 scraper endpoint
@app.post("/v1/scrape")
async def run_scrape(
    payload: ScrapeRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Web scraper with x402 payment support"""
    await check_agent_payment(request, x_agent_id)
    data = await scrape_url(payload.url)
    return {"status": "success", "data": data, "verified": True}
