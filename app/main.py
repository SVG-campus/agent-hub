from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.utils.billing import check_billing
from app.services.scraper import scrape_url

app = FastAPI(title="Agent Native Hub")

class ScrapeRequest(BaseModel):
    url: str

@app.get("/")
async def home():
    return {"status": "online", "endpoints": ["/v1/scrape"]}

@app.post("/v1/scrape")
async def run_scraper(payload: ScrapeRequest, request: Request):
    try:
        # Check billing FIRST
        await check_billing(request)
        # Run service
        data = await scrape_url(payload.url)
        return {"status": "success", "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
