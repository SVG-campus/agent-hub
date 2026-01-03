"""Payment verification system for x402 protocol"""
from web3 import Web3
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Use public Base Sepolia RPC
RPC_URL = os.getenv("RPC_URL", "https://sepolia.base.org")
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

class PaymentVerifier:
    """Verifies USDC payments on Base Sepolia"""
    
    def __init__(self, expected_recipient: str):
        self.expected_recipient = Web3.to_checksum_address(expected_recipient)
    
    def verify_payment(self, tx_hash: str, expected_amount_usd: float) -> dict:
        """
        Verify a USDC payment transaction
        
        Args:
            tx_hash: Transaction hash to verify
            expected_amount_usd: Expected payment amount in USD
            
        Returns:
            dict with verification result
        """
        try:
            # Get transaction receipt
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            
            if not receipt:
                return {
                    "verified": False,
                    "error": "Transaction not found or not confirmed"
                }
            
            # Check if transaction succeeded
            if receipt['status'] != 1:
                return {
                    "verified": False,
                    "error": "Transaction failed"
                }
            
            # Parse USDC transfer event
            # Transfer event signature: Transfer(address,address,uint256)
            transfer_topic = Web3.keccak(text="Transfer(address,address,uint256)").hex()
            
            usdc_transfer = None
            for log in receipt['logs']:
                if log['address'].lower() == USDC_CONTRACT.lower():
                    if log['topics'][0].hex() == transfer_topic:
                        # Found USDC transfer
                        from_addr = "0x" + log['topics'][1].hex()[-40:]
                        to_addr = "0x" + log['topics'][2].hex()[-40:]
                        amount = int(log['data'].hex(), 16)
                        
                        usdc_transfer = {
                            "from": Web3.to_checksum_address(from_addr),
                            "to": Web3.to_checksum_address(to_addr),
                            "amount": amount / 1_000_000  # USDC has 6 decimals
                        }
                        break
            
            if not usdc_transfer:
                return {
                    "verified": False,
                    "error": "No USDC transfer found in transaction"
                }
            
            # Verify recipient
            if usdc_transfer["to"] != self.expected_recipient:
                return {
                    "verified": False,
                    "error": f"Payment sent to wrong address. Expected {self.expected_recipient}, got {usdc_transfer['to']}"
                }
            
            # Verify amount (allow 0.01 USDC tolerance for rounding)
            if abs(usdc_transfer["amount"] - expected_amount_usd) > 0.01:
                return {
                    "verified": False,
                    "error": f"Incorrect amount. Expected ${expected_amount_usd}, got ${usdc_transfer['amount']}"
                }
            
            return {
                "verified": True,
                "from": usdc_transfer["from"],
                "to": usdc_transfer["to"],
                "amount": usdc_transfer["amount"],
                "tx_hash": tx_hash,
                "block_number": receipt['blockNumber']
            }
            
        except Exception as e:
            return {
                "verified": False,
                "error": f"Verification error: {str(e)}"
            }
