"""Main API application with x402 payment protocol"""
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from app.models import *
from app.payment import PaymentVerifier
from typing import Optional, List
import os
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from google import genai
from google.genai import types
import json
import re

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

app = FastAPI(
    title="Agent Hub API",
    description="AI-powered API services with x402 payment protocol",
    version="1.0.0",
    servers=[
        {"url": "https://web-production-4833.up.railway.app", "description": "Production Server"},
        {"url": "http://localhost:8000", "description": "Local Development"}
    ]
)

# Configuration
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
SERVER_WALLET = os.getenv("SERVER_WALLET_ADDRESS", "0xDE8A632E7386A919b548352e0CB57DaCE566BbB5")

# 🧪 TEMPORARY TEST PRICING
PRICING = {
    "sentiment": 0.01,
    "translate": 0.01,
    "summarize": 0.01,
    "extract": 0.01,
    "scrape": 0.01,
    "email_finder": 0.01,
    "company_intel": 0.01,
    "code_review": 0.01,
    "research": 0.01,
    "content_gen": 0.01,
    "seo_optimize": 0.01,
    "social_schedule": 0.01,
    "email_campaign": 0.01,
    "lead_gen": 0.01,
    "competitive": 0.01,
    "swot": 0.01,
    "trend_forecast": 0.01,
    "bulk_content": 0.01,
}

# 💰 PRODUCTION PRICING (Uncomment when testing is done)
# PRICING = {
#     "sentiment": 0.05,
#     "translate": 0.05,
#     "summarize": 0.08,
#     "extract": 0.10,
#     "scrape": 0.15,
#     "email_finder": 0.20,
#     "company_intel": 0.25,
#     "code_review": 0.50,
#     "research": 0.30,
#     "content_gen": 0.20,
#     "seo_optimize": 0.15,
#     "social_schedule": 0.40,
#     "email_campaign": 0.35,
#     "lead_gen": 2.00,
#     "competitive": 1.50,
#     "swot": 0.75,
#     "trend_forecast": 1.00,
#     "bulk_content": 1.00,
# }

payment_verifier = PaymentVerifier(SERVER_WALLET)

def extract_json_from_response(text: str) -> dict:
    """Extract JSON from Gemini response, handling markdown code blocks"""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Try to parse as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If that fails, try to find JSON object in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError(f"Could not extract valid JSON from response: {text[:200]}")

def require_payment(service: str, payment_signature: Optional[str] = None) -> Optional[JSONResponse]:
    if TEST_MODE:
        return None
    
    amount = PRICING.get(service, 0.10)
    
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
    
    return None


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
        "services_available": len(PRICING),
        "gemini_configured": client is not None,
        "gemini_model": GEMINI_MODEL if client else None,
        "endpoints": {"pricing": "/payment/pricing", "docs": "/docs"}
    }


@app.get("/payment/pricing")
async def get_pricing():
    return {"currency": "USDC", "network": "Base Sepolia", "services": PRICING, "test_mode": TEST_MODE}


# ==========================================
# TIER 1: CORE & DATA ENDPOINTS
# ==========================================

@app.post("/agent/sentiment")
async def sentiment_analysis(request: SentimentRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("sentiment", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        prompt = f"Analyze the sentiment of this text and respond with ONLY a JSON object containing 'sentiment' (positive/negative/neutral) and 'score' (float between -1 and 1). Do not include markdown formatting or code blocks.\n\nText: {request.text}"
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        result = extract_json_from_response(response.text)
        return {"status": "success", **result, "paid": not TEST_MODE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/translate")
async def translate(request: TranslateRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("translate", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        prompt = f"Translate this text to {request.target_language}. Respond with ONLY the translated text:\n\n{request.text}"
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return {
            "status": "success",
            "original_text": request.text,
            "translated_text": response.text.strip(),
            "target_language": request.target_language,
            "paid": not TEST_MODE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/summarize")
async def summarize(request: SummarizeRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("summarize", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        content = request.text or ""
        if request.urls:
            async with httpx.AsyncClient() as c:
                for url in request.urls[:3]:
                    try:
                        resp = await c.get(url, timeout=10)
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        content += "\n\n" + soup.get_text()[:5000]
                    except:
                        pass
        
        prompt = f"Summarize this content in approximately {request.max_length} words:\n\n{content[:10000]}"
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return {
            "status": "success",
            "summary": response.text.strip(),
            "original_length": len(content.split()),
            "paid": not TEST_MODE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/scrape")
async def scrape_web(request: ScrapeRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("scrape", payment_signature): return err
    
    try:
        async with httpx.AsyncClient() as c:
            response = await c.get(request.url, timeout=15, follow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                "status": "success",
                "url": request.url,
                "title": soup.title.string if soup.title else None,
                "text": soup.get_text()[:5000],
                "links": [a.get('href') for a in soup.find_all('a', href=True)][:50],
                "images": [img.get('src') for img in soup.find_all('img', src=True)][:20],
                "status_code": response.status_code,
                "paid": not TEST_MODE
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrape failed: {str(e)}")


@app.post("/agent/extract")
async def extract_data(request: DataExtractionRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("extract", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        async with httpx.AsyncClient() as c:
            response = await c.get(request.url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_content = soup.get_text()[:8000]
        
        schema_str = str(request.extraction_schema) if request.extraction_schema else "title, description, main_content"
        prompt = f"Extract the following fields from this webpage content: {schema_str}\n\nReturn ONLY a valid JSON object without markdown formatting or code blocks.\n\nContent:\n{page_content}"
        
        ai_response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        extracted = extract_json_from_response(ai_response.text)
        
        return {
            "status": "success",
            "url": request.url,
            "extracted_data": extracted,
            "paid": not TEST_MODE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/research")
async def research_topic(request: ResearchRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("research", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        ddgs = DDGS()
        results = list(ddgs.text(request.query, max_results=request.max_sources))
        sources_text = "\n\n".join([f"Source: {r['title']}\n{r['body']}" for r in results])
        
        prompt = f"Based on these search results, provide a comprehensive research summary about: {request.query}\n\nSources:\n{sources_text}"
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        
        return {
            "status": "success",
            "query": request.query,
            "sources": [{"title": r['title'], "url": r['href'], "snippet": r['body']} for r in results],
            "summary": response.text.strip(),
            "paid": not TEST_MODE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/content-gen")
async def generate_content(request: ContentGenRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("content_gen", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        keywords_str = ", ".join(request.keywords) if request.keywords else ""
        prompt = f"Write a {request.word_count}-word {request.content_type} about {request.topic} in a {request.tone} tone."
        if keywords_str:
            prompt += f" Include these keywords: {keywords_str}"
        
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return {
            "status": "success",
            "topic": request.topic,
            "content": response.text.strip(),
            "word_count": len(response.text.split()),
            "paid": not TEST_MODE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/code-review")
async def code_review(request: CodeReviewRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("code_review", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        prompt = f"Review this {request.language} code. Check for:"
        if request.check_security: prompt += " security vulnerabilities,"
        if request.check_performance: prompt += " performance issues,"
        prompt += f" and code quality. Return ONLY a valid JSON object (no markdown formatting) with 'issues' (array), 'quality_score' (0-100), and 'recommendations' (array).\n\nCode:\n{request.code}"
        
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        result = extract_json_from_response(response.text)
        return {"status": "success", **result, "paid": not TEST_MODE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/seo-optimize")
async def seo_optimize(request: SeoOptimizeRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("seo_optimize", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        keywords_str = ", ".join(request.target_keywords)
        prompt = f"Optimize this content for SEO with these keywords: {keywords_str}. Return the optimized version:\n\n{request.content}"
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        
        return {
            "status": "success",
            "optimized_content": response.text.strip(),
            "keywords_used": request.target_keywords,
            "paid": not TEST_MODE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/swot")
async def swot_analysis(request: SWOTRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("swot", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        prompt = f"Perform a SWOT analysis for {request.subject} in the {request.industry} industry. Return ONLY a valid JSON object (no markdown formatting) with 'strengths', 'weaknesses', 'opportunities', 'threats' (each as arrays)."
        if request.include_recommendations:
            prompt += " Also include 'recommendations' array."
        
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        result = extract_json_from_response(response.text)
        return {"status": "success", "subject": request.subject, "swot": result, "paid": not TEST_MODE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/competitive-analysis")
async def competitive_analysis(request: CompetitiveRequest, payment_signature: Optional[str] = Header(None)):
    if err := require_payment("competitive", payment_signature): return err
    
    if not client:
        raise HTTPException(status_code=503, detail="Google Gemini API not configured. Set GOOGLE_API_KEY environment variable.")
    
    try:
        ddgs = DDGS()
        results = list(ddgs.text(f"{request.company_domain} competitors analysis", max_results=5))
        context = "\n".join([r['body'] for r in results])
        
        prompt = f"Based on this research, analyze {request.company_domain}. Return ONLY a valid JSON object (no markdown formatting) with 'competitors' (array), 'market_position' (string), 'strengths' (array), 'weaknesses' (array).\n\nResearch:\n{context}"
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        result = extract_json_from_response(response.text)
        return {"status": "success", "target": request.company_domain, **result, "paid": not TEST_MODE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
