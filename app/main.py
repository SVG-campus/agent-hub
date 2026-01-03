from app.utils.billing import check_agent_payment
from app.utils.payment_verifier import verify_usdc_payment

@app.post("/v1/scrape")
async def run_scrape(
    payload: ScrapeRequest,
    x_agent_id: str = Header(None),
    request: Request = None
):
    # x402 check ONLY
    await check_agent_payment(request, x_agent_id)
    
    # If here, agent paid (manual verification for MVP)
    data = await scrape_url(payload.url)
    return {"status": "success", "data": data, "verified": True}

@app.get("/v1/verify-payment/{payment_id}")
async def verify_payment(payment_id: str):
    verified = await verify_usdc_payment(payment_id)
    if verified:
        return {"verified": True, "access_token": f"token_{payment_id}"}
    return HTTPException(status_code=402, detail="Payment not confirmed")
