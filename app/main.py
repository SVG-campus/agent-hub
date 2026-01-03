from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Import all services
from app.services.scraper import scrape_url
from app.services.research import deep_research, competitive_analysis, market_intelligence
from app.services.content import generate_content, seo_optimize, summarize_content, translate_content
from app.services.leads import generate_leads, enrich_contact
from app.services.intelligence import sentiment_analysis, extract_data, find_emails, company_intelligence
from app.services.bulk_content import bulk_generate_content, generate_social_schedule, generate_email_campaign
from app.services.analysis import swot_analysis, trend_forecast, code_review

# Import all models
from app.models import (
    ScrapeRequest, ResearchRequest, ContentGenRequest, LeadGenRequest,
    CompetitiveRequest, SeoOptimizeRequest, SummarizeRequest, TranslateRequest,
    SentimentRequest, DataExtractionRequest, EmailFinderRequest, CompanyIntelRequest,
    BulkContentRequest, SocialScheduleRequest, EmailCampaignRequest,
    SWOTRequest, TrendForecastRequest, CodeReviewRequest
)

from app.utils.billing import check_agent_payment

load_dotenv()

app = FastAPI(
    title="Agent Hub API",
    description="AI-powered services for autonomous agents with x402 payments",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "Agent Hub API",
        "version": "1.0.0",
        "payment_protocol": "x402 (Coinbase CDP)",
        "network": "Base Sepolia (Testnet)",
        "currency": "USDC",
        "test_mode": os.getenv("TEST_MODE", "true"),
        "services": 17,
        "endpoints": {
            "pricing": "/payment/pricing",
            "payment_info": "/payment/info",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "services": "operational"}


# ========== ORIGINAL SERVICES ==========

@app.post("/agent/scrape")
async def scrape(payload: ScrapeRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="scrape")
    result = await scrape_url(payload.url)
    return {"status": "success", "url": payload.url, **result}

@app.post("/agent/research")
async def research(payload: ResearchRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="research")
    result = await deep_research(payload.query, payload.depth, payload.max_sources)
    return {"status": "success", "query": payload.query, **result}

@app.post("/agent/competitive")
async def competitive(payload: CompetitiveRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="competitive")
    result = await competitive_analysis(payload.company_domain, payload.analysis_type)
    return {"status": "success", **result}

@app.post("/agent/generate-content")
async def gen_content(payload: ContentGenRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="generate_content")
    result = await generate_content(payload.topic, payload.content_type, payload.tone, payload.word_count, payload.keywords)
    return {"status": "success", **result}

@app.post("/agent/seo-optimize")
async def seo(payload: SeoOptimizeRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="seo_optimize")
    result = await seo_optimize(payload.content, payload.target_keywords, payload.optimization_level)
    return {"status": "success", **result}

@app.post("/agent/summarize")
async def summarize(payload: SummarizeRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="summarize")
    result = await summarize_content(payload.text, payload.urls, payload.max_length)
    return {"status": "success", **result}

@app.post("/agent/translate")
async def translate(payload: TranslateRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="translate")
    result = await translate_content(payload.text, payload.target_language, payload.source_language)
    return {"status": "success", **result}

@app.post("/agent/lead-gen")
async def lead_gen(payload: LeadGenRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="lead_gen")
    result = await generate_leads(payload.industry, payload.location, payload.company_size, payload.job_titles, payload.count)
    return {"status": "success", **result}

# ========== TIER 1: DATA INTELLIGENCE ==========

@app.post("/agent/sentiment")
async def analyze_sentiment(payload: SentimentRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="sentiment")
    result = await sentiment_analysis(payload.text, payload.detailed, payload.language)
    return {"status": "success", **result}

@app.post("/agent/extract-data")
async def extract(payload: DataExtractionRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="extract_data")
    result = await extract_data(payload.url, payload.schema, payload.format)
    return {"status": "success", **result}

@app.post("/agent/find-emails")
async def find_email(payload: EmailFinderRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="find_emails")
    result = await find_emails(payload.domain, payload.role, payload.verify)
    return {"status": "success", **result}

@app.post("/agent/company-intel")
async def company_intel(payload: CompanyIntelRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="company_intel")
    result = await company_intelligence(payload.domain, payload.include_funding, payload.include_tech_stack, payload.include_employees)
    return {"status": "success", **result}

# ========== TIER 2: BULK CONTENT ==========

@app.post("/agent/bulk-content")
async def bulk_content(payload: BulkContentRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="bulk_content")
    result = await bulk_generate_content(payload.topics, payload.content_type, payload.tone, payload.word_count)
    return {"status": "success", **result}

@app.post("/agent/social-schedule")
async def social_schedule(payload: SocialScheduleRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="social_schedule")
    result = await generate_social_schedule(payload.topic, payload.platforms, payload.posts_per_day, payload.duration_days)
    return {"status": "success", **result}

@app.post("/agent/email-campaign")
async def email_campaign(payload: EmailCampaignRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="email_campaign")
    result = await generate_email_campaign(payload.product, payload.target_audience, payload.goal, payload.num_emails)
    return {"status": "success", **result}

# ========== TIER 3: ADVANCED ANALYSIS ==========

@app.post("/agent/swot")
async def swot(payload: SWOTRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="swot")
    result = await swot_analysis(payload.subject, payload.industry, payload.include_recommendations)
    return {"status": "success", **result}

@app.post("/agent/forecast")
async def forecast(payload: TrendForecastRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="forecast")
    result = await trend_forecast(payload.topic, payload.timeframe, payload.include_data)
    return {"status": "success", **result}

@app.post("/agent/code-review")
async def review_code(payload: CodeReviewRequest, request: Request, x_agent_id: str = Header(None)):
    await check_agent_payment(request, x_agent_id, service_id="code_review")
    result = await code_review(payload.code, payload.language, payload.check_security, payload.check_performance)
    return {"status": "success", **result}

# ========== PAYMENT ENDPOINTS ==========

@app.get("/payment/info")
async def payment_info():
    return {
        "protocol": "x402",
        "facilitator": os.getenv("FACILITATOR_URL"),
        "currency": "USDC",
        "network": "Base Sepolia",
        "server_wallet": os.getenv("SERVER_WALLET_ADDRESS", "Not configured"),
        "test_mode": os.getenv("TEST_MODE", "true"),
        "docs": "https://docs.cdp.coinbase.com/x402/welcome"
    }

@app.get("/payment/pricing")
async def get_pricing():
    return {
        "currency": "USDC",
        "network": "Base Sepolia",
        "services": {
            "scrape": float(os.getenv("SCRAPE_PRICE", "0.002")),
            "research": float(os.getenv("RESEARCH_PRICE", "0.10")),
            "sentiment": float(os.getenv("SENTIMENT_PRICE", "0.05")),
            "extract_data": float(os.getenv("EXTRACT_DATA_PRICE", "0.15")),
            "find_emails": float(os.getenv("FIND_EMAILS_PRICE", "0.20")),
            "company_intel": float(os.getenv("COMPANY_INTEL_PRICE", "0.30")),
            "generate_content": float(os.getenv("CONTENT_GEN_PRICE", "0.20")),
            "seo_optimize": float(os.getenv("SEO_PRICE", "0.15")),
            "summarize": float(os.getenv("SUMMARIZE_PRICE", "0.08")),
            "translate": float(os.getenv("TRANSLATE_PRICE", "0.05")),
            "bulk_content": float(os.getenv("BULK_CONTENT_PRICE", "1.00")),
            "social_schedule": float(os.getenv("SOCIAL_SCHEDULE_PRICE", "0.50")),
            "email_campaign": float(os.getenv("EMAIL_CAMPAIGN_PRICE", "0.75")),
            "lead_gen": float(os.getenv("LEAD_GEN_PRICE", "0.25")),
            "competitive": float(os.getenv("COMPETITIVE_PRICE", "0.50")),
            "swot": float(os.getenv("SWOT_PRICE", "0.40")),
            "forecast": float(os.getenv("FORECAST_PRICE", "0.60")),
            "code_review": float(os.getenv("CODE_REVIEW_PRICE", "0.25"))
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
