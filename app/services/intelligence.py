import os
from typing import Dict, Optional
from ddgs import DDGS
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"))


async def sentiment_analysis(text: str, detailed: bool = False, language: str = "en") -> Dict:
    """Analyze sentiment of text"""
    try:
        prompt = f"""Analyze the sentiment of this {language} text:

"{text}"

Provide:
1. Overall sentiment (positive/negative/neutral/mixed)
2. Confidence score (0-100%)
3. Key emotions detected
{"4. Detailed breakdown by sentence" if detailed else ""}

Format as JSON."""

        response = model.generate_content(prompt)
        
        return {
            "text": text[:200] + "..." if len(text) > 200 else text,
            "analysis": response.text,
            "language": language,
            "detailed": detailed
        }
    except Exception as e:
        raise Exception(f"Sentiment analysis failed: {str(e)}")


async def extract_data(url: str, schema: Optional[Dict] = None, format: str = "json") -> Dict:
    """Extract structured data from webpage"""
    try:
        import httpx
        from bs4 import BeautifulSoup
        
        # Fetch page
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Get text content
        text_content = soup.get_text()[:5000]
        
        schema_instruction = ""
        if schema:
            schema_instruction = f"\nExtract according to this schema: {schema}"
        
        prompt = f"""Extract structured data from this webpage content:

{text_content}
{schema_instruction}

Return data in {format} format."""

        response = model.generate_content(prompt)
        
        return {
            "url": url,
            "extracted_data": response.text,
            "format": format
        }
    except Exception as e:
        raise Exception(f"Data extraction failed: {str(e)}")


async def find_emails(domain: str, role: Optional[str] = None, verify: bool = False) -> Dict:
    """Find business emails from domain"""
    try:
        # Search for email patterns
        query = f"{domain} email contact"
        if role:
            query += f" {role}"
        
        results = DDGS().text(query, max_results=5)
        
        # Extract emails from results
        emails = []
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        for r in results:
            content = r.get("body", "") + r.get("title", "")
            found = re.findall(email_pattern, content)
            for email in found:
                if domain in email and email not in emails:
                    emails.append(email)
        
        # Use AI to categorize emails
        if emails:
            prompt = f"""Categorize these emails by role/department:

{emails}

Provide JSON with email and likely role."""
            
            response = model.generate_content(prompt)
            categorization = response.text
        else:
            categorization = "No emails found"
        
        return {
            "domain": domain,
            "emails_found": emails,
            "categorization": categorization,
            "verified": verify
        }
    except Exception as e:
        raise Exception(f"Email finding failed: {str(e)}")


async def company_intelligence(domain: str, include_funding: bool = True, 
                                include_tech_stack: bool = True, 
                                include_employees: bool = True) -> Dict:
    """Get comprehensive company intelligence"""
    try:
        # Multi-query search
        queries = [
            f"{domain} company overview",
            f"{domain} funding revenue",
            f"{domain} technology stack",
            f"{domain} employees team size"
        ]
        
        all_results = []
        for q in queries[:3]:  # Limit to avoid rate limits
            results = DDGS().text(q, max_results=2)
            all_results.extend(results)
        
        content = "\n\n".join([r.get("body", "") for r in all_results])
        
        prompt = f"""Create comprehensive company intelligence report for {domain}:

Data:
{content[:4000]}

Include:
- Company overview
{"- Funding & revenue" if include_funding else ""}
{"- Technology stack" if include_tech_stack else ""}
{"- Team size & key employees" if include_employees else ""}
- Recent news

Format as structured report (under 400 words)."""

        response = model.generate_content(prompt)
        
        return {
            "domain": domain,
            "intelligence_report": response.text,
            "sources": [r.get("href") for r in all_results[:5]]
        }
    except Exception as e:
        raise Exception(f"Company intelligence failed: {str(e)}")
