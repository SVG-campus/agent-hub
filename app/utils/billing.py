from fastapi import HTTPException, Request
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"


def get_service_price(service_id: str) -> float:
    """Get price for a service from environment variables"""
    price_map = {
        "scrape": "SCRAPE_PRICE",
        "research": "RESEARCH_PRICE",
        "sentiment": "SENTIMENT_PRICE",
        "extract_data": "EXTRACT_DATA_PRICE",
        "find_emails": "FIND_EMAILS_PRICE",
        "company_intel": "COMPANY_INTEL_PRICE",
        "generate_content": "CONTENT_GEN_PRICE",
        "seo_optimize": "SEO_PRICE",
        "summarize": "SUMMARIZE_PRICE",
        "translate": "TRANSLATE_PRICE",
        "bulk_content": "BULK_CONTENT_PRICE",
        "social_schedule": "SOCIAL_SCHEDULE_PRICE",
        "email_campaign": "EMAIL_CAMPAIGN_PRICE",
        "lead_gen": "LEAD_GEN_PRICE",
        "competitive": "COMPETITIVE_PRICE",
        "swot": "SWOT_PRICE",
        "forecast": "FORECAST_PRICE",
        "code_review": "CODE_REVIEW_PRICE"
    }
    
    env_var = price_map.get(service_id, "DEFAULT_PRICE")
    return float(os.getenv(env_var, "0.10"))


async def check_agent_payment(
    request: Request,
    agent_id: Optional[str],
    service_id: str = "ai_agent_service"
) -> dict:
    """
    Check payment via x402 protocol
    Amount is read from .env based on service_id
    """
    
    # Get price from environment
    amount = get_service_price(service_id)
    
    # TEST MODE: Skip verification
    if TEST_MODE:
        print(f"💰 [TEST MODE] Would charge ${amount:.2f} for {service_id}")
        return {"status": "test_mode", "amount": amount, "service": service_id}
    
    # PRODUCTION MODE: Verify x402 payment
    # Import here to avoid circular dependency
    from app.utils.x402_handler import verify_x402_payment, check_wallet_configured
    
    if not check_wallet_configured():
        raise HTTPException(
            status_code=500,
            detail="Server wallet not configured"
        )
    
    result = await verify_x402_payment(request, amount, service_id)
    
    print(f"✅ Payment verified: ${amount:.2f} for {service_id}")
    return result
