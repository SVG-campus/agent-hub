import os
import openai
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_content(
    topic: str,
    content_type: str = "article",
    tone: str = "professional",
    word_count: int = 500,
    keywords: Optional[List[str]] = None
) -> dict:
    """
    Generate SEO-optimized content
    """
    try:
        keyword_instruction = ""
        if keywords:
            keyword_instruction = f"Include these keywords naturally: {', '.join(keywords)}"
        
        prompts = {
            "article": f"Write a {word_count}-word {tone} article about {topic}. {keyword_instruction}",
            "post": f"Write a {tone} social media post about {topic} ({word_count} chars max). {keyword_instruction}",
            "email": f"Write a {tone} email about {topic} (~{word_count} words). {keyword_instruction}",
            "ad": f"Write a {tone} ad copy for {topic} (~{word_count} words). {keyword_instruction}"
        }
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are an expert {content_type} writer with SEO expertise."},
                {"role": "user", "content": prompts.get(content_type, prompts["article"])}
            ],
            temperature=0.7,
            max_tokens=word_count * 2
        )
        
        content = response.choices[0].message.content
        
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
    """
    Optimize content for SEO
    """
    try:
        prompt = f"""Optimize this content for SEO targeting keywords: {', '.join(target_keywords)}

Original content:
{content}

Provide:
1. Optimized content with keywords naturally integrated
2. SEO score (0-100)
3. Suggestions for improvement
4. Meta title and description

Return as JSON."""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an SEO expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        
        return {
            "optimized_content": result,
            "target_keywords": target_keywords,
            "optimization_level": level
        }
        
    except Exception as e:
        raise Exception(f"SEO optimization failed: {str(e)}")


async def summarize_content(text: Optional[str] = None, urls: Optional[List[str]] = None, max_length: int = 200) -> dict:
    """
    Summarize text or web pages
    """
    try:
        content_to_summarize = text or ""
        
        if urls:
            from app.services.scraper import scrape_url
            for url in urls[:3]:  # Limit to 3 URLs
                scraped = await scrape_url(url)
                content_to_summarize += f"\n\n{scraped.get('text', '')}"
        
        prompt = f"Summarize the following in {max_length} words or less:\n\n{content_to_summarize[:5000]}"
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a summarization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_length * 2
        )
        
        summary = response.choices[0].message.content
        
        return {
            "summary": summary,
            "original_length": len(content_to_summarize.split()),
            "summary_length": len(summary.split()),
            "compression_ratio": round(len(summary) / len(content_to_summarize), 2)
        }
        
    except Exception as e:
        raise Exception(f"Summarization failed: {str(e)}")


async def translate_content(text: str, target_lang: str, source_lang: Optional[str] = None) -> dict:
    """
    Translate text to target language
    """
    try:
        source_instruction = f"from {source_lang}" if source_lang else "automatically detecting source language"
        
        prompt = f"Translate this text {source_instruction} to {target_lang}:\n\n{text}"
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        translation = response.choices[0].message.content
        
        return {
            "original": text,
            "translated": translation,
            "source_language": source_lang or "auto",
            "target_language": target_lang
        }
        
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")
