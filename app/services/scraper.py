import httpx
from bs4 import BeautifulSoup

async def scrape_url(url: str):
    headers = {"User-Agent": "AgentHub-Bot/1.0"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()
        
    soup = BeautifulSoup(resp.text, "html.parser")
    
    data = {
        "url": url,
        "title": soup.title.string.strip() if soup.title else None,
        "description": "",
        "h1s": [h.get_text().strip() for h in soup.find_all("h1")],
        "status": "success"
    }
    
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        data["description"] = meta_desc.get("content", "").strip()
        
    return data
