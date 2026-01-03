import os
from typing import Dict, List
from ddgs import DDGS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"))

def search_web_free(query: str, max_results: int = 5) -> List[Dict]:
    """Free web search using ddgs"""
    print(f"🔍 Searching for: {query}")
    try:
        # CORRECT API: Pass query as first positional argument
        results = DDGS().text(query, max_results=max_results)
        
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "content": r.get("body", ""),
                "score": 0.8
            })
        
        print(f"✅ Found {len(formatted)} results")
        return formatted
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []


async def deep_research(query: str, depth: str = "standard", max_sources: int = 5) -> Dict:
    """Deep web research"""
    try:
        search_results = search_web_free(query, max_results=max_sources)
        
        if not search_results:
            # Fallback to AI knowledge
            try:
                response = model.generate_content(f"Answer this query: {query}")
                return {
                    "answer": response.text,
                    "insights": ["Answered from AI knowledge (search unavailable)"],
                    "sources": [],
                    "confidence": 60,
                    "depth": "knowledge-fallback"
                }
            except:
                return {
                    "answer": "No results found.",
                    "insights": [],
                    "sources": [],
                    "confidence": 0,
                    "depth": depth
                }
        
        sources = [{"title": r["title"], "url": r["url"], "score": r["score"]} for r in search_results]
        content_text = "\n\n".join([f"Source: {r['title']}\n{r['content']}" for r in search_results])
        
        prompt = f"""Based on these sources, answer: "{query}"

Sources:
{content_text[:5000]}

Provide clear answer with insights (under 300 words)."""

        response = model.generate_content(prompt)
        
        return {
            "answer": response.text,
            "insights": [f"Source {i+1}: {s['title']}" for i, s in enumerate(sources[:3])],
            "sources": sources,
            "confidence": 85,
            "depth": depth
        }
        
    except Exception as e:
        raise Exception(f"Research failed: {str(e)}")


async def competitive_analysis(domain: str, analysis_type: str = "full") -> Dict:
    """Analyze competitor"""
    try:
        queries = [f"{domain} pricing", f"{domain} reviews", f"alternatives to {domain}"]
        
        all_results = []
        for q in queries:
            all_results.extend(search_web_free(q, max_results=2))
        
        if not all_results:
            return {"domain": domain, "analysis": {"summary": "No data found."}, "sources": []}
        
        content = "\n\n".join([r.get("content", "") for r in all_results])
        prompt = f"""Analyze {domain}:\n\n{content[:3000]}\n\nBrief analysis: pricing, features, position, competitors."""
        
        response = model.generate_content(prompt)
        
        return {
            "domain": domain,
            "analysis": {"summary": response.text},
            "sources": [{"url": r["url"], "title": r["title"]} for r in all_results[:5]]
        }
        
    except Exception as e:
        raise Exception(f"Competitive analysis failed: {str(e)}")


async def market_intelligence(topic: str, timeframe: str = "30d") -> Dict:
    """Market trends"""
    try:
        results = search_web_free(f"{topic} trends news 2026", max_results=8)
        
        if not results:
            return {"topic": topic, "timeframe": timeframe, "intelligence": {"summary": "No data found."}, "updated_at": "2026-01-02"}
        
        content = "\n\n".join([r.get("content", "") for r in results])
        prompt = f"""Market intelligence: {topic}\n\n{content[:3000]}\n\nBrief: trends, opportunities, players."""
        
        response = model.generate_content(prompt)
        
        return {
            "topic": topic,
            "timeframe": timeframe,
            "intelligence": {"summary": response.text},
            "updated_at": "2026-01-02"
        }
        
    except Exception as e:
        raise Exception(f"Market intelligence failed: {str(e)}")
