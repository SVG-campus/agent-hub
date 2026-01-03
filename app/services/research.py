import os
import json
from typing import Dict, List
from tavily import TavilyClient
import openai
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

async def deep_research(query: str, depth: str = "standard", max_sources: int = 5) -> Dict:
    """
    Perform deep web research with multiple sources
    """
    try:
        # 1. Search with Tavily
        search_depth = "advanced" if depth == "deep" else "basic"
        search_results = tavily_client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_sources
        )
        
        # 2. Extract sources and content
        sources = []
        content_chunks = []
        
        for result in search_results.get('results', []):
            sources.append({
                "title": result.get('title', ''),
                "url": result.get('url', ''),
                "score": result.get('score', 0)
            })
            content_chunks.append(result.get('content', ''))
        
        # 3. Synthesize with GPT-4
        combined_content = "\n\n".join(content_chunks[:5])
        
        synthesis_prompt = f"""Based on the following research sources, provide a comprehensive answer to: "{query}"

Research Sources:
{combined_content}

Provide:
1. A clear, well-structured answer
2. Key insights
3. Confidence level (0-100%)

Format as JSON with keys: answer, insights, confidence"""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a research analyst providing accurate, well-sourced answers."},
                {"role": "user", "content": synthesis_prompt}
            ],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return {
            "answer": result.get("answer", ""),
            "insights": result.get("insights", []),
            "sources": sources,
            "confidence": result.get("confidence", 80),
            "depth": depth
        }
        
    except Exception as e:
        raise Exception(f"Research failed: {str(e)}")


async def competitive_analysis(domain: str, analysis_type: str = "full") -> Dict:
    """
    Analyze competitor: pricing, features, marketing, traffic
    """
    try:
        # Search for competitor info
        queries = [
            f"{domain} pricing plans features",
            f"{domain} customer reviews complaints",
            f"{domain} marketing strategy traffic",
            f"alternatives to {domain}"
        ]
        
        all_results = []
        for query in queries:
            results = tavily_client.search(query=query, max_results=3)
            all_results.extend(results.get('results', []))
        
        # Synthesize competitive intelligence
        content = "\n\n".join([r.get('content', '') for r in all_results])
        
        prompt = f"""Analyze competitor {domain} based on this intelligence:

{content}

Provide JSON with:
- pricing_strategy: their pricing model and tiers
- key_features: main product features
- strengths: what they do well
- weaknesses: gaps and opportunities
- market_position: how they position themselves
- alternatives: top 3 competitors"""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a competitive intelligence analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        return {
            "domain": domain,
            "analysis": analysis,
            "sources": [{"url": r.get('url'), "title": r.get('title')} for r in all_results[:5]]
        }
        
    except Exception as e:
        raise Exception(f"Competitive analysis failed: {str(e)}")


async def market_intelligence(topic: str, timeframe: str = "30d") -> Dict:
    """
    Get market trends and intelligence on a topic
    """
    try:
        query = f"{topic} trends news insights {timeframe}"
        results = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=10
        )
        
        content = "\n\n".join([r.get('content', '') for r in results.get('results', [])])
        
        prompt = f"""Analyze market intelligence for: {topic}

Data:
{content}

Provide JSON with:
- market_size: current market size and growth
- key_trends: top 3-5 trends
- opportunities: market opportunities
- threats: potential risks
- key_players: major companies/products
- forecast: short-term outlook"""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a market research analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        intelligence = json.loads(response.choices[0].message.content)
        
        return {
            "topic": topic,
            "timeframe": timeframe,
            "intelligence": intelligence,
            "updated_at": "2026-01-02"
        }
        
    except Exception as e:
        raise Exception(f"Market intelligence failed: {str(e)}")
