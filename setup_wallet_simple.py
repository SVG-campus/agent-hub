from eth_account import Account
import os

print("🔑 Creating Simple EOA Wallet\n")

# Generate new account
account = Account.create()

wallet_address = account.address
private_key = account.key.hex()

print(f"✅ Wallet created!")
print(f"\n💰 Wallet Address:")
print(f"   {wallet_address}")
print(f"\n🔐 Private Key (KEEP SECRET!):")
print(f"   {private_key}")

# Update .env
with open(".env", "r") as f:
    env_contents = f.read()

if "SERVER_WALLET_ADDRESS=" in env_contents:
    lines = env_contents.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("SERVER_WALLET_ADDRESS="):
            new_lines.append(f"SERVER_WALLET_ADDRESS={wallet_address}")
        elif line.startswith("SERVER_WALLET_PRIVATE_KEY="):
            new_lines.append(f"SERVER_WALLET_PRIVATE_KEY={private_key}")
        else:
            new_lines.append(line)
    env_contents = "\n".join(new_lines)
    
    # Add private key if not exists
    if "SERVER_WALLET_PRIVATE_KEY=" not in env_contents:
        env_contents += f"\nSERVER_WALLET_PRIVATE_KEY={private_key}\n"
else:
    env_contents += f"\nSERVER_WALLET_ADDRESS={wallet_address}\n"
    env_contents += f"SERVER_WALLET_PRIVATE_KEY={private_key}\n"

with open(".env", "w") as f:
    f.write(env_contents)

print(f"\n✅ Saved to .env")
print(f"\n🚰 Get testnet USDC:")
print(f"   1. Go to: https://portal.cdp.coinbase.com/products/faucets")
print(f"   2. Network: Base Sepolia")
print(f"   3. Token: USDC")
print(f"   4. Address: {wallet_address}")
print(f"   5. Click 'Claim'")
