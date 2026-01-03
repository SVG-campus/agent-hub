// verifier/app/page.tsx
'use client';
import { OnchainKitProvider } from '@coinbase/onchainkit';
import { Checkout, CheckoutButton } from '@coinbase/onchainkit/checkout';

export default function PaymentPage() {
  return (
    <OnchainKitProvider 
      apiKey={process.env.NEXT_PUBLIC_ONCHAINKIT_API_KEY} 
      chain={base}
    >
      <Checkout productId="your_product_id_from_cdp_dashboard">
         <CheckoutButton coinbaseBranded={true} />
      </Checkout>
    </OnchainKitProvider>
  );
}
