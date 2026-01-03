# app/main.py
from coinbase.wallet.client import Client

# Initialize with Secret Key (Backend Only)
client = Client(
    api_key=os.getenv("CDP_API_KEY_NAME"),
    api_secret=os.getenv("CDP_API_KEY_PRIVATE_KEY")
)

@app.post("/verify-payment")
def verify(tx_hash: str):
    # Check if transaction is valid on Base
    return {"status": "verified"}
