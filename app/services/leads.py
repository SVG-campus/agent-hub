import os
from typing import List, Optional
from tavily import TavilyClient
import openai
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_leads(
    industry: str,
    location: Optional[str] = None,
    company_size: Optional[str] = None,
    job_titles: Optional[List[str]] = None,
    count: int = 10
) -> dict:
    """
    Find qualified leads matching criteria
    """
    try:
        # Build search query
        query_parts = [industry]
        if location:
            query_parts.append(location)
        if company_size:
            query_parts.append(company_size)
        if job_titles:
            query_parts.append(" OR ".join(job_titles))
        
        query = f"{' '.join(query_parts)} companies contacts email"
        
        # Search for companies
        results = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=count * 2
        )
        
        # Extract and structure leads
        leads = []
        for result in results.get('results', [])[:count]:
            lead = {
                "company_name": result.get('title', '').split('-')[0].strip(),
                "url": result.get('url', ''),
                "description": result.get('content', '')[:200],
                "industry": industry,
                "location": location,
                "source": result.get('url', '')
            }
            leads.append(lead)
        
        return {
            "leads": leads,
            "count": len(leads),
            "criteria": {
                "industry": industry,
                "location": location,
                "company_size": company_size,
                "job_titles": job_titles
            }
        }
        
    except Exception as e:
        raise Exception(f"Lead generation failed: {str(e)}")


async def enrich_contact(domain: str) -> dict:
    """
    Enrich contact/company data
    """
    try:
        query = f"{domain} company info contact email leadership"
        results = tavily_client.search(query=query, max_results=5)
        
        content = "\n\n".join([r.get('content', '') for r in results.get('results', [])])
        
        prompt = f"""Extract company information for {domain}:

{content}

Provide JSON with:
- company_name
- industry
- size (employees)
- location
- description
- technologies
- social_media links"""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data enrichment specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        enriched_data = response.choices[0].message.content
        
        return {
            "domain": domain,
            "enriched_data": enriched_data,
            "sources": [r.get('url') for r in results.get('results', [])]
        }
        
    except Exception as e:
        raise Exception(f"Contact enrichment failed: {str(e)}")
