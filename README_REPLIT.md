# Hour.IT Agent Hub - AI Services with Crypto Payments

[![Run on Repl.it](https://replit.com/badge/github/your-username/agent-hub)](https://replit.com/@your-username/agent-hub)

## 🚀 What is this?

A production-ready AI agent payment system that accepts **USDC on Base Mainnet** for 18 premium AI services.

## 💰 Services Available

| Service | Price | Description |
|---------|-------|-------------|
| Sentiment Analysis | $0.05 | Analyze text emotion |
| Translation | $0.05 | 100+ languages |
| Summarization | $0.08 | Condense long content |
| Web Scraping | $0.15 | Extract webpage data |
| Data Extraction | $0.10 | Structured data from URLs |
| Research | $0.30 | Deep topic research |
| Content Generation | $0.20 | AI-written articles |
| Code Review | $0.50 | Security & performance check |
| SEO Optimization | $0.15 | Keyword optimization |
| SWOT Analysis | $0.75 | Business strategy |
| Competitive Analysis | $1.50 | Market positioning |
| Lead Generation | $2.00 | B2B contact discovery |

## 🧪 Quick Start

```python
import requests

# 1. Call any service
response = requests.post(
    "https://web-production-4833.up.railway.app/agent/sentiment",
    json={"text": "I love AI agents!"}
)

# 2. Get payment instructions (402 response)
payment_info = response.json()
print(f"Send {payment_info['detail']['amount_usd']} USDC to:")
print(payment_info['detail']['instructions']['step_1'])

# 3. After sending USDC, retry with tx hash
response = requests.post(
    "https://web-production-4833.up.railway.app/agent/sentiment",
    json={"text": "I love AI agents!"},
    headers={"PAYMENT-SIGNATURE": "0xYourTransactionHash"}
)

result = response.json()
print(result)
```

## 📚 API Documentation

Full interactive docs: [https://web-production-4833.up.railway.app/docs](https://web-production-4833.up.railway.app/docs)

## 🔗 Links

- **OpenAPI Spec**: [/openapi.json](https://web-production-4833.up.railway.app/openapi.json)
- **Pricing**: [/payment/pricing](https://web-production-4833.up.railway.app/payment/pricing)
- **GitHub**: [your-repo-url]
- **OpenAI GPT**: [Link to your GPT]

## 🔐 Payment Details

- **Network**: Base Mainnet (Chain ID: 8453)
- **Currency**: USDC (0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913)
- **Payment Wallet**: 0xDE8A632E7386A919b548352e0CB57DaCE566BbB5

## 🛠️ Tech Stack

- FastAPI (Python)
- Google Gemini AI
- Web3.py (Payment verification)
- Base Mainnet (L2 Ethereum)
- Railway (Deployment)

## 📦 Installation

```bash
pip install requests web3 python-dotenv
```

## 🌟 Use Cases

1. **AI Agents**: Programmatic access to premium AI services
2. **Automation**: Pay-per-use API integration
3. **Crypto Natives**: On-chain payment verification
4. **Developers**: Build paid AI features into apps

## 🤝 Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](LICENSE)
