"""COMPLETE test of ALL 18 Agent Hub services - LOCAL VERSION"""
import requests
import json

API_URL = "http://localhost:8000"  # LOCAL TESTING

def test_service(endpoint, payload, service_name):
    print(f"\n{'='*70}")
    print(f"🧪 Testing: {service_name}")
    print(f"{'='*70}")
    print(f"�� Endpoint: {endpoint}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=30)
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}\n")
        return False
    
    if response.status_code == 200:
        print("✅ Success!")
        result = response.json()
        print(f"📊 Result Preview: {str(result)[:300]}...\n")
        return True
    
    if response.status_code == 503:
        print(f"⚠️  Service Unavailable: {response.json().get('detail', 'Unknown error')}\n")
        return False
    
    if response.status_code == 500:
        print(f"❌ Server Error: {response.json().get('detail', 'Unknown error')}\n")
        return False
    
    print(f"❌ Unexpected status: {response.status_code} - {response.text[:200]}\n")
    return False

def main():
    print("\n" + "="*70)
    print("🚀 AGENT HUB - LOCAL TEST (All 18 Services)")
    print("="*70)
    print(f"🌐 Testing against: {API_URL}")
    print(f"🧪 TEST_MODE: No payments required")
    print("="*70)
    
    # Test ALL 18 services
    tests = [
        # Tier 1: Core & Data (8 services)
        ("/agent/sentiment", {"text": "AI agents paying for services is revolutionary!"}, "1. Sentiment Analysis"),
        ("/agent/translate", {"text": "Hello world", "target_language": "es"}, "2. Translation"),
        ("/agent/summarize", {"text": "AI agents can autonomously pay for API services using cryptocurrency on blockchain networks."}, "3. Summarization"),
        ("/agent/extract", {"url": "https://example.com", "extraction_schema": {"title": "string"}}, "4. Data Extraction"),
        ("/agent/scrape", {"url": "https://example.com"}, "5. Web Scraping"),
        ("/agent/email-finder", {"domain": "example.com", "role": "ceo"}, "6. Email Finder"),
        ("/agent/company-intel", {"domain": "example.com", "include_funding": True}, "7. Company Intelligence"),
        ("/agent/code-review", {"code": "def hello():\n    print('world')", "language": "python"}, "8. Code Review"),
        
        # Tier 2: Research & Content (5 services)
        ("/agent/research", {"query": "AI agent payments", "max_sources": 3}, "9. Research"),
        ("/agent/content-gen", {"topic": "AI Automation", "word_count": 200}, "10. Content Generation"),
        ("/agent/seo-optimize", {"content": "AI agents are powerful", "target_keywords": ["AI", "automation"]}, "11. SEO Optimization"),
        ("/agent/social-schedule", {"topic": "AI agents", "platforms": ["twitter"], "posts_per_day": 2, "duration_days": 3}, "12. Social Media Scheduling"),
        ("/agent/email-campaign", {"product": "AI Platform", "target_audience": "developers", "goal": "signups", "num_emails": 3}, "13. Email Campaign"),
        
        # Tier 3: Advanced Business (5 services)
        ("/agent/lead-gen", {"industry": "technology", "job_titles": ["CTO"], "count": 5}, "14. Lead Generation"),
        ("/agent/competitive-analysis", {"company_domain": "example.com"}, "15. Competitive Analysis"),
        ("/agent/swot", {"subject": "AI Agents", "industry": "Technology"}, "16. SWOT Analysis"),
        ("/agent/trend-forecast", {"topic": "AI adoption", "timeframe": "2025"}, "17. Trend Forecasting"),
        ("/agent/bulk-content", {"topics": ["AI", "Blockchain"], "content_type": "blog", "word_count": 500}, "18. Bulk Content Generation"),
    ]
    
    results = []
    for endpoint, payload, name in tests:
        try:
            success = test_service(endpoint, payload, name)
            results.append((name, "✅ SUCCESS" if success else "❌ FAILED"))
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            results.append((name, f"❌ ERROR"))
    
    print("\n" + "="*70)
    print("📊 COMPLETE TEST SUMMARY")
    print("="*70)
    for name, status in results:
        print(f"{status:20} | {name}")
    
    print("\n" + "="*70)
    print(f"�� Successful Tests: {sum(1 for _, s in results if '✅' in s)}/{len(results)}")
    print("="*70)

if __name__ == "__main__":
    main()
