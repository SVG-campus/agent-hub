"""Main API application with x402 payment protocol"""
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from app.models import *
from app.payment import PaymentVerifier
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Agent Hub API",
    description="AI-powered API services with x402 payment protocol",
    version="1.0.0"
)

# Configuration
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
SERVER_WALLET = os.getenv("SERVER_WALLET_ADDRESS", "0xDE8A632E7386A919b548352e0CB57DaCE566BbB5")

# Pricing (in USD)
PRICING = {
    "sentiment": 0.05,
    "translate": 0.05,
    "summarize": 0.08,
    "extract": 0.10,
    "classify": 0.05,
}

payment_verifier = PaymentVerifier(SERVER_WALLET)


def require_payment(service: str, payment_signature: Optional[str] = None) -> Optional[JSONResponse]:
    """Check if payment is required and verify if provided"""
    
    if TEST_MODE:
        return None  # No payment required in test mode
    
    amount = PRICING.get(service, 0.10)
    
    # If no payment signature provided, return 402
    if not payment_signature:
        return JSONResponse(
            status_code=402,
            content={
                "detail": {
                    "error": "Payment Required",
                    "service": service,
                    "amount_usd": amount,
                    "currency": "USDC",
                    "network": "Base Sepolia",
                    "instructions": {
                        "step_1": f"Send ${amount} USDC to {SERVER_WALLET} on Base Sepolia network",
                        "step_2": "Include the transaction hash in PAYMENT-SIGNATURE header",
                        "step_3": "Retry your request with the payment signature"
                    }
                }
            }
        )
    
    # Verify payment
    result = payment_verifier.verify_payment(payment_signature, amount)
    
    if not result["verified"]:
        return JSONResponse(
            status_code=402,
            content={
                "detail": {
                    "error": "Payment processing error",
                    "message": f"402: {result}"
                }
            }
        )
    
    return None  # Payment verified


@app.get("/")
async def root():
    return {
        "name": "Agent Hub API",
        "version": "1.0.0",
        "payment_protocol": "x402 (Coinbase CDP)",
        "network": "Base Sepolia (Testnet)",
        "currency": "USDC",
        "test_mode": str(TEST_MODE).lower(),
        "server_wallet": SERVER_WALLET,
        "services": len(PRICING),
        "endpoints": {
            "pricing": "/payment/pricing",
            "payment_info": "/payment/info",
            "docs": "/docs"
        }
    }


@app.get("/payment/pricing")
async def get_pricing():
    return {
        "currency": "USDC",
        "network": "Base Sepolia",
        "services": PRICING,
        "test_mode": TEST_MODE
    }


@app.post("/agent/sentiment")
async def sentiment_analysis(
    request: SentimentRequest,
    payment_signature: Optional[str] = Header(None)
):
    """Analyze sentiment of text"""
    payment_check = require_payment("sentiment", payment_signature)
    if payment_check:
        return payment_check
    
    # Simulate sentiment analysis
    text = request.text.lower()
    
    if any(word in text for word in ["good", "great", "excellent", "amazing", "love"]):
        sentiment = "positive"
        score = 0.85
    elif any(word in text for word in ["bad", "terrible", "awful", "hate", "worst"]):
        sentiment = "negative"
        score = -0.75
    else:
        sentiment = "neutral"
        score = 0.05
    
    return {
        "status": "success",
        "text": request.text,
        "sentiment": sentiment,
        "score": score,
        "paid": not TEST_MODE
    }


@app.post("/agent/translate")
async def translate(
    request: TranslateRequest,
    payment_signature: Optional[str] = Header(None)
):
    """Translate text to target language"""
    payment_check = require_payment("translate", payment_signature)
    if payment_check:
        return payment_check
    
    # Simulate translation
    translations = {
        "es": f"[ES] {request.text}",
        "fr": f"[FR] {request.text}",
        "de": f"[DE] {request.text}",
        "it": f"[IT] {request.text}",
        "pt": f"[PT] {request.text}",
    }
    
    translated = translations.get(request.target_language, f"[{request.target_language.upper()}] {request.text}")
    
    return {
        "status": "success",
        "original_text": request.text,
        "translated_text": translated,
        "source_language": "en",
        "target_language": request.target_language,
        "paid": not TEST_MODE
    }


@app.post("/agent/summarize")
async def summarize(
    request: SummarizeRequest,
    payment_signature: Optional[str] = Header(None)
):
    """Summarize text"""
    payment_check = require_payment("summarize", payment_signature)
    if payment_check:
        return payment_check
    
    # Simple summarization
    words = request.text.split()[:request.max_length]
    summary = " ".join(words) + ("..." if len(request.text.split()) > request.max_length else "")
    
    return {
        "status": "success",
        "original_text": request.text,
        "summary": summary,
        "original_length": len(request.text.split()),
        "summary_length": len(words),
        "paid": not TEST_MODE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
