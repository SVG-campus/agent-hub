import os
from typing import Dict
from ddgs import DDGS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"))


async def swot_analysis(subject: str, industry: str, include_recommendations: bool = True) -> Dict:
    """Generate SWOT analysis"""
    try:
        # Search for data
        results = DDGS().text(f"{subject} {industry} analysis strengths weaknesses", max_results=5)
        content = "\n\n".join([r.get("body", "") for r in results])
        
        prompt = f"""Create comprehensive SWOT analysis for:

Subject: {subject}
Industry: {industry}

Data:
{content[:3000]}

Provide:
- Strengths (5 points)
- Weaknesses (5 points)
- Opportunities (5 points)
- Threats (5 points)
{"- Strategic recommendations" if include_recommendations else ""}

Format as structured report."""

        response = model.generate_content(prompt)
        
        return {
            "subject": subject,
            "industry": industry,
            "swot_analysis": response.text,
            "includes_recommendations": include_recommendations
        }
    except Exception as e:
        raise Exception(f"SWOT analysis failed: {str(e)}")


async def trend_forecast(topic: str, timeframe: str = "12m", include_data: bool = True) -> Dict:
    """Forecast market trends"""
    try:
        results = DDGS().text(f"{topic} trends forecast 2026 2027", max_results=8)
        content = "\n\n".join([r.get("body", "") for r in results])
        
        prompt = f"""Forecast trends for: {topic}

Timeframe: {timeframe}

Data:
{content[:4000]}

Provide:
- Current state analysis
- Predicted trends (next {timeframe})
- Growth opportunities
- Risk factors
{"- Supporting data/statistics" if include_data else ""}

Format as forecast report (under 400 words)."""

        response = model.generate_content(prompt)
        
        return {
            "topic": topic,
            "timeframe": timeframe,
            "forecast": response.text,
            "generated_at": "2026-01-02"
        }
    except Exception as e:
        raise Exception(f"Trend forecast failed: {str(e)}")


async def code_review(code: str, language: str, check_security: bool = True, 
                       check_performance: bool = True) -> Dict:
    """AI-powered code review"""
    try:
        checks = []
        if check_security:
            checks.append("security vulnerabilities")
        if check_performance:
            checks.append("performance issues")
        
        # FIX: Use escaped format without triple backticks inside f-string
        prompt = f"""Review this {language} code for {', '.join(checks)}:

CODE TO REVIEW:
{code[:3000]}

Provide:
1. Overall code quality (1-10)
2. Issues found (with severity)
3. Specific recommendations
4. Refactoring suggestions

Format as code review report."""

        response = model.generate_content(prompt)
        
        return {
            "language": language,
            "code_length": len(code),
            "review": response.text,
            "checks_performed": {
                "security": check_security,
                "performance": check_performance
            }
        }
    except Exception as e:
        raise Exception(f"Code review failed: {str(e)}")
