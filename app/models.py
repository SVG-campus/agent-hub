from pydantic import BaseModel
from typing import Optional, List, Dict

# Original models
class ScrapeRequest(BaseModel):
    url: str

class ResearchRequest(BaseModel):
    query: str
    depth: str = "standard"
    max_sources: int = 5

class LeadGenRequest(BaseModel):
    industry: str
    location: Optional[str] = None
    company_size: Optional[str] = None
    job_titles: Optional[List[str]] = None
    count: int = 10

class ContentGenRequest(BaseModel):
    topic: str
    content_type: str = "article"
    tone: str = "professional"
    word_count: int = 500
    keywords: Optional[List[str]] = None

class CompetitiveRequest(BaseModel):
    company_domain: str
    analysis_type: str = "full"

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

# Tier 1: Data Intelligence
class SentimentRequest(BaseModel):
    text: str
    detailed: bool = False
    language: Optional[str] = "en"

class DataExtractionRequest(BaseModel):
    url: str
    schema: Optional[Dict] = None
    format: str = "json"

class EmailFinderRequest(BaseModel):
    domain: str
    role: Optional[str] = None
    verify: bool = False

class CompanyIntelRequest(BaseModel):
    domain: str
    include_funding: bool = True
    include_tech_stack: bool = True
    include_employees: bool = True

# Tier 2: Content at Scale
class BulkContentRequest(BaseModel):
    topics: List[str]
    content_type: str = "article"
    tone: str = "professional"
    word_count: int = 500

class SocialScheduleRequest(BaseModel):
    topic: str
    platforms: List[str]
    posts_per_day: int = 2
    duration_days: int = 7

class EmailCampaignRequest(BaseModel):
    product: str
    target_audience: str
    goal: str = "sales"
    num_emails: int = 5

# Tier 3: Advanced Analysis
class SWOTRequest(BaseModel):
    subject: str
    industry: str
    include_recommendations: bool = True

class TrendForecastRequest(BaseModel):
    topic: str
    timeframe: str = "12m"
    include_data: bool = True

class CodeReviewRequest(BaseModel):
    code: str
    language: str
    check_security: bool = True
    check_performance: bool = True
