# Agent Hub Semantic Kernel Plugin

Integrate Agent Hub crypto-native AI services into Microsoft Semantic Kernel.

## Overview

Access 18 premium AI services with USDC cryptocurrency payments on Base Mainnet.

## Services

- AnalyzeSentiment - $0.05
- Translate - $0.05
- Research - $0.30
- ScrapeWeb - $0.15
- GenerateContent - $0.20
- ReviewCode - $0.50

Plus 12 more services available.

## Installation

Copy AgentHubPlugin.cs to your project:

dotnet add package Microsoft.SemanticKernel
dotnet add package System.Net.Http.Json

## Usage

using Microsoft.SemanticKernel;

var builder = Kernel.CreateBuilder();
builder.Plugins.AddFromType<AgentHubPlugin>();
var kernel = builder.Build();

var result = await kernel.InvokeAsync(
    "AgentHub",
    "AnalyzeSentiment",
    new() { ["text"] = "I love AI!" }
);

## Payment Flow

1. First call returns payment instructions
2. Send USDC to provided wallet on Base Mainnet
3. Retry with transaction hash in paymentTx parameter

## Details

- Network: Base Mainnet (Chain ID 8453)
- Currency: USDC
- Wallet: 0xDE8A632E7386A919b548352e0CB57DaCE566BbB5
- API: https://web-production-4833.up.railway.app

## License

MIT
