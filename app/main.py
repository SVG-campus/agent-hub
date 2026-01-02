from fastapi import FastAPI, Request, Depends
from app.utils.billing import check_billing
from app.services.scraper import scrape_url
from pydantic import BaseModel

app = FastAPI(title="Agent Native Hub")

class ScrapeRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "online", "instructions": "Send POST to /v1/scrape"}

# The Protected Endpoint
@app.post("/v1/scrape", dependencies=[Depends(check_billing)])
async def run_scraper(payload: ScrapeRequest):
    data = await scrape_url(payload.url)
    return {"status": "success", "data": data}
