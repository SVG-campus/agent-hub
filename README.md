# Agent Hub Scraper

**Live**: https://agent-hub-s8xo.onrender.com

## Pricing
- **Stripe**: $0.001/call (API Key)
- **Crypto**: 0.01 USDC (x402, Base chain)

## MCP Tool
```json
{
  "name": "scrape_url",
  "description": "Structured web scraping",
  "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
}

***

## **Register on MCP Directories (Copy-Paste)**

**1. [MCP Market](pplx://action/navigate/SawmEwPF79I)**:
Name: Agent Hub Scraper
URL: https://agent-hub-s8xo.onrender.com
Capabilities: web_scraping, x402_payments, stripe_metered


**2. [AI Agent Store](pplx://action/navigate/IMfyBQN4f5A)**:
Category: Developer Tools
Name: Agent Hub (Pay-Per-Scrape)
Description: Reliable scraping for agents. Stripe or USDC.
URL: https://agent-hub-s8xo.onrender.com


***

## **Run Tests NOW + Share Results**

```bash
# 1. Agent test
curl -X POST https://agent-hub-s8xo.onrender.com/v1/scrape -H "Content-Type: application/json" -d '{"url": "https://github.com"}' -v | grep -E "(402|0xF0)"

# 2. Human test  
curl -X POST https://agent-hub-s8xo.onrender.com/v1/scrape -H "Content-Type: application/json" -H "X-API-Key: sk_live_test" -d '{"url": "https://github.com"}'

# 3. Status
curl https://agent-hub-s8xo.onrender.com/
Expected:
1. 402 + wallet address
2. Scraped GitHub data  
3. {"status": "online"}

