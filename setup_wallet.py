import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def create_wallet():
    """Create a CDP wallet using the SDK"""
    
    print("🔑 Creating Server Wallet for x402 Payments\n")
    
    # Check CDP credentials
    api_key_id = os.getenv("CDP_API_KEY_ID", "")
    api_key_secret = os.getenv("CDP_API_KEY_SECRET", "")
    
    if not api_key_id or not api_key_secret:
        print("❌ CDP API credentials not found!")
        print("\n📝 Get credentials:")
        print("1. Go to: https://portal.cdp.coinbase.com/")
        print("2. Click 'API Keys' → 'Create API Key'")
        print("3. Save the credentials")
        print("4. Add to .env:")
        print("   CDP_API_KEY_ID=your_key_id")
        print("   CDP_API_KEY_SECRET=your_key_secret")
        return
    
    try:
        # Import CDP SDK
        from cdp import CdpClient
        from web3 import Web3
        
        print("✅ Found CDP credentials")
        print("🏗️  Initializing CDP client...")
        
        # Initialize CDP
        cdp = CdpClient(
            api_key_id=api_key_id,
            api_key_secret=api_key_secret
        )
        
        print("📝 Creating EOA account on Base Sepolia...")
        
        # Create EOA (Externally Owned Account)
        account = await cdp.evm.create_account()
        
        wallet_address = account.address
        
        print(f"\n✅ Wallet created successfully!")
        print(f"\n💰 Your Wallet Address:")
        print(f"   {wallet_address}")
        
        # Save to .env file
        print(f"\n�� Updating .env file...")
        
        # Read current .env
        with open(".env", "r") as f:
            env_contents = f.read()
        
        # Update or add SERVER_WALLET_ADDRESS
        if "SERVER_WALLET_ADDRESS=" in env_contents:
            # Replace existing
            lines = env_contents.split("\n")
            new_lines = []
            for line in lines:
                if line.startswith("SERVER_WALLET_ADDRESS="):
                    new_lines.append(f"SERVER_WALLET_ADDRESS={wallet_address}")
                else:
                    new_lines.append(line)
            env_contents = "\n".join(new_lines)
        else:
            # Add new
            env_contents += f"\nSERVER_WALLET_ADDRESS={wallet_address}\n"
        
        # Write back
        with open(".env", "w") as f:
            f.write(env_contents)
        
        print(f"✅ Added to .env: SERVER_WALLET_ADDRESS={wallet_address}")
        
        print(f"\n🚰 Next: Get testnet USDC")
        print(f"   1. Go to: https://portal.cdp.coinbase.com/products/faucets")
        print(f"   2. Select Network: Base Sepolia")
        print(f"   3. Select Token: USDC")
        print(f"   4. Paste address: {wallet_address}")
        print(f"   5. Click 'Claim'")
        print(f"\n🎉 Setup complete!")
        
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("\nInstall required packages:")
        print("pip install coinbase-cdp-sdk web3 eth-account")
    except Exception as e:
        print(f"❌ Error creating wallet: {e}")
        print("\n📝 Manual wallet creation:")
        print("1. Use MetaMask extension")
        print("2. Create new wallet")
        print("3. Switch to Base Sepolia network:")
        print("   - Network: Base Sepolia")
        print("   - RPC: https://sepolia.base.org")
        print("   - Chain ID: 84532")
        print("4. Copy your address")
        print("5. Add to .env: SERVER_WALLET_ADDRESS=0x...")

# Run async function
if __name__ == "__main__":
    asyncio.run(create_wallet())
