from pydantic import BaseModel
from typing import Optional, List

class ResearchRequest(BaseModel):
    query: str
    depth: str = "standard"  # standard, deep, comprehensive
    max_sources: int = 5

class LeadGenRequest(BaseModel):
    industry: str
    location: Optional[str] = None
    company_size: Optional[str] = None
    job_titles: Optional[List[str]] = None
    count: int = 10

class ContentGenRequest(BaseModel):
    topic: str
    content_type: str = "article"  # article, post, email, ad
    tone: str = "professional"
    word_count: int = 500
    keywords: Optional[List[str]] = None

class CompetitiveRequest(BaseModel):
    company_domain: str
    analysis_type: str = "full"  # full, pricing, features, marketing

class SeoOptimizeRequest(BaseModel):
    content: str
    target_keywords: List[str]
    optimization_level: str = "standard"

class SummarizeRequest(BaseModel):
    text: Optional[str] = None
    urls: Optional[List[str]] = None
    max_length: int = 200

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None

class MonitorRequest(BaseModel):
    keywords: List[str]
    sources: List[str] = ["web", "social", "news"]
    frequency: str = "daily"

class SentimentRequest(BaseModel):
    text: str
    detailed: bool = False
