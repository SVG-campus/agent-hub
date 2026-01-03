# Hour.IT Agent Hub - Complete Documentation

## 📖 Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Authentication & Payments](#authentication--payments)
4. [API Endpoints](#api-endpoints)
5. [Integration Examples](#integration-examples)
6. [Error Handling](#error-handling)

---

## Overview

Hour.IT Agent Hub is a production crypto-native AI service marketplace where agents pay for premium services using USDC on Base Mainnet.

**Base URL**: `https://web-production-4833.up.railway.app`

---

## Quick Start

### 1. Install Dependencies

```bash
pip install requests web3
```

### 2. Call Any Service

```python
import requests

response = requests.post(
    "https://web-production-4833.up.railway.app/agent/sentiment",
    json={"text": "AI agents are revolutionary!"}
)

# Response: 402 Payment Required
payment = response.json()
print(f"Cost: ${payment['detail']['amount_usd']} USDC")
print(f"Wallet: {payment['detail']['instructions']['step_1']}")
```

### 3. Send Payment & Retry

```python
# After sending USDC on Base Mainnet, get your transaction hash
tx_hash = "0xYourTransactionHashHere"

response = requests.post(
    "https://web-production-4833.up.railway.app/agent/sentiment",
    json={"text": "AI agents are revolutionary!"},
    headers={"PAYMENT-SIGNATURE": tx_hash}
)

result = response.json()
print(result)  # {"status": "success", "sentiment": "positive", "score": 0.95}
```

---

## Authentication & Payments

### Payment Protocol: x402

All services use the **x402 payment protocol**:

1. **Request service** → Receive `402 Payment Required`
2. **Send USDC** to the wallet address provided
3. **Retry request** with `PAYMENT-SIGNATURE` header containing your transaction hash
4. **Receive result** after on-chain verification

### Payment Details

| Detail | Value |
|--------|-------|
| **Network** | Base Mainnet |
| **Chain ID** | 8453 |
| **Currency** | USDC |
| **Contract** | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| **Payment Wallet** | `0xDE8A632E7386A919b548352e0CB57DaCE566BbB5` |

### Sending USDC

**MetaMask Example**:
```javascript
const tx = await usdcContract.transfer(
    "0xDE8A632E7386A919b548352e0CB57DaCE566BbB5",
    ethers.utils.parseUnits("0.05", 6) // $0.05 with 6 decimals
);
const receipt = await tx.wait();
const txHash = receipt.transactionHash;
```

---

## API Endpoints

### Core Services ($0.05 - $0.50)

#### 1. Sentiment Analysis - `POST /agent/sentiment`

**Price**: $0.05 USDC

```json
{
  "text": "I love this product!",
  "detailed": true,
  "language": "en"
}
```

**Response**:
```json
{
  "status": "success",
  "sentiment": "positive",
  "score": 0.92,
  "paid": true
}
```

---

#### 2. Translation - `POST /agent/translate`

**Price**: $0.05 USDC

```json
{
  "text": "Hello world",
  "target_language": "es"
}
```

**Response**:
```json
{
  "status": "success",
  "translated_text": "Hola mundo",
  "target_language": "es"
}
```

---

#### 3. Summarization - `POST /agent/summarize`

**Price**: $0.08 USDC

```json
{
  "text": "Long article text here...",
  "max_length": 200
}
```

---

#### 4. Web Scraping - `POST /agent/scrape`

**Price**: $0.15 USDC

```json
{
  "url": "https://example.com"
}
```

**Response**:
```json
{
  "status": "success",
  "title": "Example Domain",
  "text": "...",
  "links": ["..."],
  "images": ["..."]
}
```

---

#### 5. Data Extraction - `POST /agent/extract`

**Price**: $0.10 USDC

```json
{
  "url": "https://example.com",
  "extraction_schema": {
    "title": "string",
    "price": "number"
  }
}
```

---

#### 6. Code Review - `POST /agent/code-review`

**Price**: $0.50 USDC

```json
{
  "code": "def hello():\n    print('world')",
  "language": "python",
  "check_security": true,
  "check_performance": true
}
```

**Response**:
```json
{
  "status": "success",
  "quality_score": 85,
  "issues": [],
  "recommendations": ["Add docstrings", "..."]
}
```

---

### Business Services ($0.75 - $2.00)

#### 7. SWOT Analysis - `POST /agent/swot`

**Price**: $0.75 USDC

```json
{
  "subject": "Tesla",
  "industry": "Electric Vehicles",
  "include_recommendations": true
}
```

---

#### 8. Competitive Analysis - `POST /agent/competitive-analysis`

**Price**: $1.50 USDC

```json
{
  "company_domain": "nike.com"
}
```

**Response**:
```json
{
  "status": "success",
  "competitors": ["Adidas", "Under Armour"],
  "market_position": "Leader",
  "strengths": ["Brand recognition", "..."],
  "weaknesses": ["..."]
}
```

---

#### 9. Lead Generation - `POST /agent/lead-gen`

**Price**: $2.00 USDC

```json
{
  "industry": "Technology",
  "job_titles": ["CTO", "VP Engineering"],
  "location": "San Francisco",
  "count": 10
}
```

---

## Integration Examples

### Python Client

```python
class AgentHubClient:
    def __init__(self, api_url, wallet_private_key):
        self.api_url = api_url
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
        self.account = self.w3.eth.account.from_key(wallet_private_key)

    def call_service(self, endpoint, params):
        # Try without payment first
        response = requests.post(f"{self.api_url}{endpoint}", json=params)

        if response.status_code == 402:
            # Payment required
            payment_info = response.json()['detail']
            tx_hash = self.send_payment(
                payment_info['amount_usd'],
                payment_info['instructions']['step_1'].split()[1]
            )

            # Retry with payment signature
            response = requests.post(
                f"{self.api_url}{endpoint}",
                json=params,
                headers={"PAYMENT-SIGNATURE": tx_hash}
            )

        return response.json()

    def send_payment(self, amount_usd, to_address):
        usdc_contract = self.w3.eth.contract(
            address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            abi=[...]  # USDC ABI
        )

        tx = usdc_contract.functions.transfer(
            to_address,
            int(amount_usd * 1e6)  # USDC has 6 decimals
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
        })

        signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()

# Usage
client = AgentHubClient(
    "https://web-production-4833.up.railway.app",
    "YOUR_PRIVATE_KEY"
)

result = client.call_service("/agent/sentiment", {"text": "Great product!"})
print(result)
```

---

### JavaScript/TypeScript

```typescript
import { ethers } from 'ethers';

async function callAgentHub(endpoint: string, params: any) {
  const response = await fetch(
    `https://web-production-4833.up.railway.app${endpoint}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    }
  );

  if (response.status === 402) {
    const payment = await response.json();

    // Send USDC payment
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const signer = provider.getSigner();
    const usdc = new ethers.Contract(
      "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      USDC_ABI,
      signer
    );

    const tx = await usdc.transfer(
      payment.detail.instructions.step_1.split(' ')[1],
      ethers.utils.parseUnits(payment.detail.amount_usd.toString(), 6)
    );

    await tx.wait();

    // Retry with payment
    return fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'PAYMENT-SIGNATURE': tx.hash
      },
      body: JSON.stringify(params)
    }).then(r => r.json());
  }

  return response.json();
}
```

---

## Error Handling

### 402 Payment Required

```json
{
  "detail": {
    "error": "Payment Required",
    "service": "sentiment",
    "amount_usd": 0.05,
    "currency": "USDC",
    "network": "Base Mainnet",
    "instructions": {
      "step_1": "Send $0.05 USDC to 0xDE8A... on Base Mainnet",
      "step_2": "Include the transaction hash in PAYMENT-SIGNATURE header",
      "step_3": "Retry your request with the payment signature"
    }
  }
}
```

### 500 Server Error

Service execution failed. Check parameters and try again.

### 503 Service Unavailable

API key not configured or service temporarily down.

---

## Complete Service List

| # | Service | Endpoint | Price |
|---|---------|----------|-------|
| 1 | Sentiment Analysis | `/agent/sentiment` | $0.05 |
| 2 | Translation | `/agent/translate` | $0.05 |
| 3 | Summarization | `/agent/summarize` | $0.08 |
| 4 | Data Extraction | `/agent/extract` | $0.10 |
| 5 | Web Scraping | `/agent/scrape` | $0.15 |
| 6 | SEO Optimization | `/agent/seo-optimize` | $0.15 |
| 7 | Content Generation | `/agent/content-gen` | $0.20 |
| 8 | Email Finder | `/agent/email-finder` | $0.20 |
| 9 | Company Intelligence | `/agent/company-intel` | $0.25 |
| 10 | Research | `/agent/research` | $0.30 |
| 11 | Email Campaign | `/agent/email-campaign` | $0.35 |
| 12 | Social Scheduling | `/agent/social-schedule` | $0.40 |
| 13 | Code Review | `/agent/code-review` | $0.50 |
| 14 | SWOT Analysis | `/agent/swot` | $0.75 |
| 15 | Trend Forecasting | `/agent/trend-forecast` | $1.00 |
| 16 | Bulk Content | `/agent/bulk-content` | $1.00 |
| 17 | Competitive Analysis | `/agent/competitive-analysis` | $1.50 |
| 18 | Lead Generation | `/agent/lead-gen` | $2.00 |

---

## Support

- **API Docs**: https://web-production-4833.up.railway.app/docs
- **GitHub**: [Your Repo]
- **OpenAI GPT**: [Your GPT Link]
