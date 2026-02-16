"""Tools for currency exchange rates."""
import requests
from typing import Optional, Dict, Tuple
from datetime import datetime


def get_exchange_rate(currency: str = "USD") -> Optional[Dict[str, any]]:
    """
    Get current exchange rate for specified currency.
    Uses exchangerate-api.com free tier.
    """
    try:
        # Using free API that doesn't require authentication
        url = f"https://api.exchangerate-api.com/v4/latest/BRL"
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        rates = data.get('rates', {})
        
        if currency == "USD":
            rate = rates.get('USD')
            if rate:
                return {
                    "moeda": "USD",
                    "taxa": 1 / rate if rate > 0 else None,  # BRL to USD
                    "timestamp": datetime.now().isoformat(),
                    "origem": "BRL"
                }
        elif currency == "EUR":
            rate = rates.get('EUR')
            if rate:
                return {
                    "moeda": "EUR",
                    "taxa": 1 / rate if rate > 0 else None,
                    "timestamp": datetime.now().isoformat(),
                    "origem": "BRL"
                }
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in exchange rate: {e}")
        return None


def format_exchange_rate(exchange_data: Dict) -> str:
    """Format exchange rate data for display."""
    if not exchange_data:
        return "Desculpe, não foi possível obter a cotação no momento."
    
    moeda = exchange_data.get('moeda', 'N/A')
    taxa = exchange_data.get('taxa', 'N/A')
    
    if taxa == 'N/A':
        return f"Cotação para {moeda} não disponível."
    
    return f"1 BRL = {taxa:.4f} {moeda}"


def get_multiple_rates(currencies: list = ["USD", "EUR"]) -> Dict[str, any]:
    """Get exchange rates for multiple currencies."""
    rates = {}
    for currency in currencies:
        rate = get_exchange_rate(currency)
        if rate:
            rates[currency] = rate
    
    return rates
