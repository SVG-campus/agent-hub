import os
from typing import List, Optional, Dict
from ddgs import DDGS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"))

def search_web_free(query: str, max_results: int = 10) -> List[Dict]:
    """Free web search"""
    print(f"🔍 Lead search: {query}")
    try:
        # CORRECT: query as first arg
        results = DDGS().text(query, max_results=max_results)
        
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "content": r.get("body", "")
            })
        
        print(f"✅ Found {len(formatted)} leads")
        return formatted
    except Exception as e:
        print(f"❌ Lead search error: {e}")
        return []


async def generate_leads(industry: str, location: Optional[str] = None, company_size: Optional[str] = None, job_titles: Optional[List[str]] = None, count: int = 10) -> dict:
    """Find leads"""
    try:
        query = f"top {industry} companies directory"
        if location:
            query += f" {location}"
        
        results = search_web_free(query, max_results=count * 2)
        
        if not results:
            return {
                "leads": [],
                "count": 0,
                "criteria": {"industry": industry, "location": location, "company_size": company_size, "job_titles": job_titles},
                "note": "No leads found. Try different criteria."
            }
        
        leads = []
        for result in results[:count]:
            title = result.get("title", "").split("-")[0].split("|")[0].strip()
            leads.append({
                "company_name": title,
                "url": result.get("url", ""),
                "description": result.get("content", "")[:200],
                "industry": industry,
                "location": location,
                "source": result.get("url", "")
            })
        
        return {
            "leads": leads,
            "count": len(leads),
            "criteria": {"industry": industry, "location": location, "company_size": company_size, "job_titles": job_titles}
        }
        
    except Exception as e:
        raise Exception(f"Lead generation failed: {str(e)}")


async def enrich_contact(domain: str) -> dict:
    """Enrich data"""
    try:
        results = search_web_free(f"{domain} company info", max_results=5)
        
        if not results:
            return {"domain": domain, "enriched_data": "No data found.", "sources": []}
        
        content = "\n\n".join([r.get("content", "") for r in results])
        prompt = f"Extract company info for {domain}:\n\n{content[:2000]}\n\nBrief summary."
        
        response = model.generate_content(prompt)
        
        return {
            "domain": domain,
            "enriched_data": response.text,
            "sources": [r.get("url") for r in results[:3]]
        }
        
    except Exception as e:
        raise Exception(f"Enrichment failed: {str(e)}")
