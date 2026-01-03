import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("🔑 Creating CDP Server Wallet\n")
    
    # Check credentials
    api_key_id = os.getenv("CDP_API_KEY_ID", "")
    api_key_secret = os.getenv("CDP_API_KEY_SECRET", "")
    
    if not api_key_id or not api_key_secret:
        print("❌ Missing CDP credentials in .env!")
        print("\n1. Go to: https://portal.cdp.coinbase.com/")
        print("2. Create API key")
        print("3. Add to .env:")
        print("   CDP_API_KEY_ID=your_key_id")
        print("   CDP_API_KEY_SECRET=your_key_secret")
        return
    
    try:
        # Correct import for coinbase-cdp-sdk
        from coinbase.cdp import Cdp
        
        print("✅ CDP SDK loaded")
        
        # Configure CDP
        Cdp.configure(api_key_id, api_key_secret)
        
        print("✅ CDP client initialized")
        print("�� Creating server wallet on Base Sepolia...")
        
        # Create wallet
        wallet = await Cdp.create_wallet(network_id="base-sepolia")
        
        wallet_address = wallet.default_address.address_id
        
        print(f"\n✅ Server wallet created!")
        print(f"\n💰 Wallet Address:")
        print(f"   {wallet_address}")
        
        # Request faucet
        print(f"\n🚰 Requesting testnet USDC...")
        
        faucet_tx = await wallet.faucet()
        
        print(f"✅ Faucet requested!")
        print(f"🔗 TX: https://sepolia.basescan.org/tx/{faucet_tx.transaction_hash}")
        
        # Save wallet data
        wallet_data = wallet.export_data()
        
        with open("wallet_data.json", "w") as f:
            import json
            json.dump(wallet_data.to_dict(), f, indent=2)
        
        print(f"\n💾 Wallet data saved to wallet_data.json")
        
        # Update .env
        print(f"\n📋 Updating .env...")
        
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
        print(f"\n⚠️  IMPORTANT: Keep wallet_data.json secure!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nRun: pip install coinbase-cdp-sdk")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\nError type: {type(e).__name__}")

asyncio.run(main())
