from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.models import (
    ResearchRequest, LeadGenRequest, ContentGenRequest,
    CompetitiveRequest, SeoOptimizeRequest, SummarizeRequest,
    TranslateRequest, SentimentRequest
)
from app.services.research import deep_research, competitive_analysis, market_intelligence
from app.services.content import generate_content, seo_optimize, summarize_content, translate_content
from app.services.leads import generate_leads, enrich_contact
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

# app/main.py - add this endpoint

@app.post("/agent/research")
async def research(
    payload: ResearchRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Deep web research with structured results"""
    await check_agent_payment(request, x_agent_id, amount=0.10)
    
    result = await deep_research(payload.query, payload.depth)
    return {
        "status": "success",
        "query": payload.query,
        "answer": result["answer"],
        "sources": result["sources"],
        "confidence": result["confidence"]
    }

# ===== RESEARCH & INTELLIGENCE =====

@app.post("/agent/research")
async def research(
    payload: ResearchRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Deep web research with structured results and sources"""
    await check_agent_payment(request, x_agent_id, amount=float(os.getenv("RESEARCH_PRICE", 0.10)))
    
    result = await deep_research(payload.query, payload.depth, payload.max_sources)
    return {
        "status": "success",
        "query": payload.query,
        **result
    }

@app.post("/agent/competitive")
async def competitive(
    payload: CompetitiveRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Competitive intelligence and analysis"""
    await check_agent_payment(request, x_agent_id, amount=float(os.getenv("COMPETITIVE_PRICE", 0.50)))
    
    result = await competitive_analysis(payload.company_domain, payload.analysis_type)
    return {
        "status": "success",
        **result
    }

@app.get("/agent/market-intel/{topic}")
async def market_intel(
    topic: str,
    timeframe: str = "30d",
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Market trends and intelligence"""
    await check_agent_payment(request, x_agent_id, amount=0.15)
    
    result = await market_intelligence(topic, timeframe)
    return {
        "status": "success",
        **result
    }

# ===== CONTENT GENERATION =====

@app.post("/agent/generate-content")
async def gen_content(
    payload: ContentGenRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Generate SEO-optimized content"""
    await check_agent_payment(request, x_agent_id, amount=float(os.getenv("CONTENT_GEN_PRICE", 0.20)))
    
    result = await generate_content(
        payload.topic,
        payload.content_type,
        payload.tone,
        payload.word_count,
        payload.keywords
    )
    return {
        "status": "success",
        **result
    }

@app.post("/agent/seo-optimize")
async def seo_opt(
    payload: SeoOptimizeRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Optimize content for SEO"""
    await check_agent_payment(request, x_agent_id, amount=float(os.getenv("SEO_PRICE", 0.15)))
    
    result = await seo_optimize(payload.content, payload.target_keywords, payload.optimization_level)
    return {
        "status": "success",
        **result
    }

@app.post("/agent/summarize")
async def summarize(
    payload: SummarizeRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Summarize text or URLs"""
    await check_agent_payment(request, x_agent_id, amount=0.08)
    
    result = await summarize_content(payload.text, payload.urls, payload.max_length)
    return {
        "status": "success",
        **result
    }

@app.post("/agent/translate")
async def translate(
    payload: TranslateRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Translate text to any language"""
    await check_agent_payment(request, x_agent_id, amount=0.05)
    
    result = await translate_content(payload.text, payload.target_language, payload.source_language)
    return {
        "status": "success",
        **result
    }

# ===== LEAD GENERATION =====

@app.post("/agent/lead-gen")
async def lead_gen(
    payload: LeadGenRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Generate qualified leads"""
    await check_agent_payment(request, x_agent_id, amount=float(os.getenv("LEAD_GEN_PRICE", 0.25)))
    
    result = await generate_leads(
        payload.industry,
        payload.location,
        payload.company_size,
        payload.job_titles,
        payload.count
    )
    return {
        "status": "success",
        **result
    }

@app.post("/agent/enrich/{domain}")
async def enrich(
    domain: str,
    x_agent_id: str = Header(None),
    request: Request = None
):
    """Enrich company/contact data"""
    await check_agent_payment(request, x_agent_id, amount=0.15)
    
    result = await enrich_contact(domain)
    return {
        "status": "success",
        **result
    }