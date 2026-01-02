def validate_api_key(key: str) -> bool:
    # For MVP: any key starting with 'sk_' is valid
    # Production: validate against Stripe customer or your DB
    return key and key.startswith('sk_')
