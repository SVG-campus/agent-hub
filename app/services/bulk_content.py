import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"))


async def bulk_generate_content(topics: List[str], content_type: str = "article", 
                                  tone: str = "professional", word_count: int = 500) -> Dict:
    """Generate multiple pieces of content at once"""
    try:
        generated = []
        
        for topic in topics[:10]:  # Limit to 10 per batch
            prompt = f"Write a {word_count}-word {tone} {content_type} about: {topic}"
            
            response = model.generate_content(prompt)
            
            generated.append({
                "topic": topic,
                "content": response.text,
                "word_count": len(response.text.split())
            })
        
        return {
            "generated_count": len(generated),
            "content": generated,
            "batch_settings": {
                "content_type": content_type,
                "tone": tone,
                "target_word_count": word_count
            }
        }
    except Exception as e:
        raise Exception(f"Bulk content generation failed: {str(e)}")


async def generate_social_schedule(topic: str, platforms: List[str], 
                                     posts_per_day: int = 2, duration_days: int = 7) -> Dict:
    """Generate social media content schedule"""
    try:
        total_posts = posts_per_day * duration_days * len(platforms)
        
        prompt = f"""Create a {duration_days}-day social media content calendar for: {topic}

Requirements:
- {posts_per_day} posts per day
- Platforms: {', '.join(platforms)}
- Mix of content types (educational, promotional, engaging)
- Include hashtags and best posting times

Format as day-by-day schedule with post content."""

        response = model.generate_content(prompt)
        
        return {
            "topic": topic,
            "schedule": response.text,
            "total_posts": total_posts,
            "platforms": platforms,
            "duration_days": duration_days
        }
    except Exception as e:
        raise Exception(f"Social schedule generation failed: {str(e)}")


async def generate_email_campaign(product: str, target_audience: str, 
                                    goal: str = "sales", num_emails: int = 5) -> Dict:
    """Generate complete email campaign"""
    try:
        prompt = f"""Create a {num_emails}-email campaign for:

Product: {product}
Audience: {target_audience}
Goal: {goal}

Include:
- Email subjects
- Email bodies (200-300 words each)
- CTAs
- Optimal sending schedule
- A/B testing suggestions

Format as Email 1, Email 2, etc."""

        response = model.generate_content(prompt)
        
        return {
            "product": product,
            "target_audience": target_audience,
            "goal": goal,
            "campaign": response.text,
            "num_emails": num_emails
        }
    except Exception as e:
        raise Exception(f"Email campaign generation failed: {str(e)}")
