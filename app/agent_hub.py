from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cdp import Cdp, Wallet
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Official CDP SDK
Cdp.configure(
    api_key_name=os.getenv("CDP_API_KEY_ID"),  # "8e634077..."
    private_key=os.getenv("CDP_API_KEY_SECRET")  # "VrVbjv7H2K..."
)

app = FastAPI(title="Agent Hub API 🚀")

class CreateWalletRequest(BaseModel):
    network: str = "base-mainnet"

@app.post("/agent/wallet")
async def create_agent_wallet(req: CreateWalletRequest):
    """Create new agent wallet."""
    try:
        wallet = Wallet.create(network_id=req.network)
        return {
            "success": True,
            "wallet_id": wallet.id,
            "address": wallet.default_address.address_id,
            "network": req.network
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/agent/b
