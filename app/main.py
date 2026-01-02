from app.utils.billing import check_agent_payment

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
