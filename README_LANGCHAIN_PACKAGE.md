# LangChain Agent Hub Tool

Official LangChain integration for [Hour.IT Agent Hub](https://web-production-4833.up.railway.app) - a crypto-native AI service marketplace.

## Installation

```bash
pip install langchain-agent-hub
```

## Quick Start

```python
from langchain_agent_hub import AgentHubTool

# Initialize tool
tool = AgentHubTool()

# Call a service (will return payment instructions if unpaid)
result = tool._run(
    service="sentiment",
    params={"text": "I love AI agents!"}
)

# After sending USDC payment, retry with transaction hash
result = tool._run(
    service="sentiment",
    params={"text": "I love AI agents!"},
    payment_tx="0xYourTransactionHash"
)

print(result)
```

## Available Services

| Service | Price | Endpoint |
|---------|-------|----------|
| Sentiment Analysis | $0.05 | `sentiment` |
| Translation | $0.05 | `translate` |
| Summarization | $0.08 | `summarize` |
| Web Scraping | $0.15 | `scrape` |
| Data Extraction | $0.10 | `extract` |

[See all 18 services](https://web-production-4833.up.railway.app/docs)

## Payment Details

- **Network**: Base Mainnet (Chain ID 8453)
- **Currency**: USDC
- **Protocol**: x402

## License

MIT License
