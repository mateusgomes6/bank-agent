"""Authentication tools."""
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from src.tools.csv_tools import get_cliente_by_cpf


def validate_cpf_format(cpf: str) -> bool:
    """Validate CPF format (11 digits)."""
    cpf_clean = cpf.replace("-", "").replace(".", "")
    return len(cpf_clean) == 11 and cpf_clean.isdigit()


def validate_date_format(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def authenticate_client(cpf: str, data_nascimento: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Authenticate a client using CPF and birth date.
    Returns (success: bool, client_data: dict or None)
    """
    # Validate formats
    if not validate_cpf_format(cpf):
        return False, None
    
    if not validate_date_format(data_nascimento):
        return False, None
    
    # Remove CPF formatting for comparison
    cpf_clean = cpf.replace("-", "").replace(".", "")
    
    # Get client from database
    cliente = get_cliente_by_cpf(cpf_clean)
    
    if not cliente:
        return False, None
    
    # Verify birth date
    if str(cliente.get('data_nascimento')).strip() == data_nascimento.strip():
        return True, cliente
    
    return False, None


def format_cpf_for_display(cpf: str) -> str:
    """Format CPF for display (XXX.XXX.XXX-XX)."""
    cpf_clean = cpf.replace("-", "").replace(".", "")
    return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:11]}"
