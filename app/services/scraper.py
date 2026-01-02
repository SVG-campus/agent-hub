import httpx
from bs4 import BeautifulSoup

async def scrape_url(url: str):
    headers = {"User-Agent": "AgentHub-Bot/1.0"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, follow_redirects=True)
        
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Basic structuring (Title, Meta Description, H1s)
    data = {
        "url": url,
        "title": soup.title.string if soup.title else None,
        "description": "",
        "h1s": [h.get_text().strip() for h in soup.find_all("h1")]
    }
    
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        data["description"] = meta.get("content")
        
    return data
