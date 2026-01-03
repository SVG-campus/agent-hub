import os
import google.generativeai as genai
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"))


async def generate_content(
    topic: str,
    content_type: str = "article",
    tone: str = "professional",
    word_count: int = 500,
    keywords: Optional[List[str]] = None
) -> dict:
    """Generate content with Gemini"""
    try:
        keyword_instruction = ""
        if keywords:
            keyword_instruction = f"Include keywords: {', '.join(keywords)}"
        
        prompts = {
            "article": f"Write a {word_count}-word {tone} article about {topic}. {keyword_instruction}",
            "post": f"Write a {tone} social media post about {topic} (~{word_count} chars). {keyword_instruction}",
            "email": f"Write a {tone} email about {topic} (~{word_count} words). {keyword_instruction}",
            "ad": f"Write a {tone} ad copy for {topic} (~{word_count} words). {keyword_instruction}"
        }
        
        prompt = prompts.get(content_type, prompts["article"])
        response = model.generate_content(prompt)
        content = response.text
        
        return {
            "content": content,
            "word_count": len(content.split()),
            "type": content_type,
            "tone": tone,
            "keywords_used": keywords or []
        }
    except Exception as e:
        raise Exception(f"Content generation failed: {str(e)}")


async def seo_optimize(content: str, target_keywords: List[str], level: str = "standard") -> dict:
    """Optimize content for SEO with Gemini"""
    try:
        prompt = f"""Optimize this content for SEO targeting keywords: {', '.join(target_keywords)}

Original content:
{content[:2000]}

Provide optimized version with keywords naturally integrated. Keep similar length."""

        response = model.generate_content(prompt)
        
        return {
            "optimized_content": response.text,
            "target_keywords": target_keywords,
            "optimization_level": level
        }
    except Exception as e:
        raise Exception(f"SEO optimization failed: {str(e)}")


async def summarize_content(text: Optional[str] = None, urls: Optional[List[str]] = None, max_length: int = 200) -> dict:
    """Summarize text or web pages with Gemini"""
    try:
        content_to_summarize = text or ""
        
        if urls:
            from app.services.scraper import scrape_url
            for url in urls[:3]:
                try:
                    scraped = await scrape_url(url)
                    content_to_summarize += f"\n\n{scraped.get('text', '')}"
                except:
                    pass
        
        if not content_to_summarize:
            return {"summary": "No content provided.", "original_length": 0, "summary_length": 0}
        
        prompt = f"Summarize in {max_length} words or less:\n\n{content_to_summarize[:5000]}"
        response = model.generate_content(prompt)
        summary = response.text
        
        return {
            "summary": summary,
            "original_length": len(content_to_summarize.split()),
            "summary_length": len(summary.split()),
            "compression_ratio": round(len(summary) / max(len(content_to_summarize), 1), 2)
        }
    except Exception as e:
        raise Exception(f"Summarization failed: {str(e)}")


async def translate_content(text: str, target_lang: str, source_lang: Optional[str] = None) -> dict:
    """Translate text with Gemini"""
    try:
        source_instruction = f"from {source_lang}" if source_lang else "automatically detecting source"
        prompt = f"Translate this text {source_instruction} to {target_lang}:\n\n{text}"
        
        response = model.generate_content(prompt)
        
        return {
            "original": text,
            "translated": response.text,
            "source_language": source_lang or "auto",
            "target_language": target_lang
        }
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")
