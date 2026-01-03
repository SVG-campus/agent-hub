import os
import asyncio
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("🔑 Creating CDP Server Wallet via API\n")
    
    api_key_id = os.getenv("CDP_API_KEY_ID", "")
    api_key_secret = os.getenv("CDP_API_KEY_SECRET", "")
    
    if not api_key_id or not api_key_secret:
        print("❌ Missing CDP credentials!")
        return
    
    print("✅ Found credentials")
    
    # CDP API endpoint
    base_url = "https://api.cdp.coinbase.com/platform"
    
    async with httpx.AsyncClient() as client:
        # Authenticate
        auth = (api_key_id, api_key_secret)
        
        print("📝 Creating wallet...")
        
        # Create wallet
        response = await client.post(
            f"{base_url}/v1/wallets",
            auth=auth,
            json={
                "wallet": {
                    "network_id": "base-sepolia"
                }
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        wallet_data = response.json()
        wallet_id = wallet_data["id"]
        
        print(f"✅ Wallet created: {wallet_id}")
        
        # Get wallet address
        response = await client.get(
            f"{base_url}/v1/wallets/{wallet_id}/addresses",
            auth=auth
        )
        
        if response.status_code == 200:
            addresses = response.json()
            if addresses.get("data"):
                wallet_address = addresses["data"][0]["address_id"]
                
                print(f"\n💰 Wallet Address:")
                print(f"   {wallet_address}")
                
                # Request faucet
                print(f"\n🚰 Requesting testnet USDC...")
                
                faucet_response = await client.post(
                    f"{base_url}/v1/wallets/{wallet_id}/faucet",
                    auth=auth,
                    json={}
                )
                
                if faucet_response.status_code == 200:
                    print(f"✅ Faucet requested!")
                else:
                    print(f"⚠️  Faucet status: {faucet_response.status_code}")
                
                # Update .env
                with open(".env", "r") as f:
                    env_contents = f.read()
                
                if "SERVER_WALLET_ADDRESS=" in env_contents:
                    lines = env_contents.split("\n")
                    new_lines = []
                    for line in lines:
                        if line.startswith("SERVER_WALLET_ADDRESS="):
                            new_lines.append(f"SERVER_WALLET_ADDRESS={wallet_address}")
                        else:
                            new_lines.append(line)
                    env_contents = "\n".join(new_lines)
                else:
                    env_contents += f"\nSERVER_WALLET_ADDRESS={wallet_address}\n"
                
                with open(".env", "w") as f:
                    f.write(env_contents)
                
                print(f"✅ Saved to .env")
                print(f"\n🎉 CDP Server Wallet ready!")

asyncio.run(main())
