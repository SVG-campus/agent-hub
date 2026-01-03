import asyncio
import os
from cdp import CdpClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("🔑 Creating CDP Server Wallet (using cdp-sdk)\n")
    
    # Check credentials
    api_key_id = os.getenv("CDP_API_KEY_ID", "")
    api_key_secret = os.getenv("CDP_API_KEY_SECRET", "")
    
    if not api_key_id or not api_key_secret:
        print("❌ Missing CDP credentials in .env!")
        return

    print("✅ CDP credentials found")
    print("🏗️  Initializing CDP client...")

    try:
        # Initialize CDP Client
        # It automatically reads CDP_API_KEY_ID and CDP_API_KEY_SECRET from env
        async with CdpClient() as cdp:
            
            print("📝 Creating EVM account on Base Sepolia...")
            
            # Create Account
            account = await cdp.evm.create_account()
            wallet_address = account.address
            
            print(f"\n✅ Account created!")
            print(f"\n💰 Wallet Address:")
            print(f"   {wallet_address}")
            
            # Request Faucet (USDC)
            print(f"\n🚰 Requesting testnet USDC...")
            
            # Note: The SDK documentation says request_faucet returns a transaction hash string
            faucet_hash = await cdp.evm.request_faucet(
                address=wallet_address,
                network="base-sepolia",
                token="usdc"  # Request USDC
            )
            
            print(f"✅ Faucet requested!")
            print(f"🔗 TX: https://sepolia.basescan.org/tx/{faucet_hash}")
            
            # Update .env
            print(f"\n📋 Updating .env file...")
            
            # Read current .env
            try:
                with open(".env", "r") as f:
                    env_contents = f.read()
            except FileNotFoundError:
                env_contents = ""
            
            # Update SERVER_WALLET_ADDRESS
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
            
            print(f"✅ Saved to .env: SERVER_WALLET_ADDRESS={wallet_address}")
            print(f"\n🎉 Setup complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
