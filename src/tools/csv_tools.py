"""Tools for reading and writing CSV files."""
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.utils.config import CLIENTES_CSV, SCORE_LIMITE_CSV, SOLICITACOES_CSV


def read_csv(file_path: str) -> pd.DataFrame:
    """Read a CSV file and return as DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    # Read CPF as string to avoid type mismatch
    return pd.read_csv(file_path, dtype={'cpf': str, 'cpf_cliente': str})


def write_csv(file_path: str, data: pd.DataFrame) -> bool:
    """Write DataFrame to CSV file."""
    try:
        data.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False


def append_to_csv(file_path: str, new_row: Dict[str, Any]) -> bool:
    """Append a new row to CSV file."""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            df = pd.read_csv(file_path)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        
        return write_csv(file_path, df)
    except Exception as e:
        print(f"Error appending to CSV: {e}")
        return False


def get_cliente_by_cpf(cpf: str) -> Optional[Dict[str, Any]]:
    """Retrieve client data by CPF."""
    try:
        df = read_csv(CLIENTES_CSV)
        # Ensure CPF is string for comparison
        df['cpf'] = df['cpf'].astype(str)
        cliente = df[df['cpf'] == str(cpf)]

        if cliente.empty:
            return None

        return cliente.iloc[0].to_dict()
    except Exception as e:
        print(f"Error retrieving client: {e}")
        return None


def update_cliente_score(cpf: str, new_score: float) -> bool:
    """Update client's credit score."""
    try:
        df = read_csv(CLIENTES_CSV)
        df['cpf'] = df['cpf'].astype(str)
        mask = df['cpf'] == str(cpf)

        if not mask.any():
            return False

        df.loc[mask, 'score'] = new_score
        return write_csv(CLIENTES_CSV, df)
    except Exception as e:
        print(f"Error updating score: {e}")
        return False


def create_credit_limit_request(cpf: str, limite_atual: float, novo_limite: float, status: str = "pendente") -> bool:
    """Create a new credit limit increase request."""
    try:
        new_request = {
            'cpf_cliente': cpf,
            'data_hora_solicitacao': datetime.now().isoformat(),
            'limite_atual': limite_atual,
            'novo_limite_solicitado': novo_limite,
            'status_pedido': status
        }
        
        return append_to_csv(SOLICITACOES_CSV, new_request)
    except Exception as e:
        print(f"Error creating request: {e}")
        return False


def get_score_limits() -> Optional[pd.DataFrame]:
    """Get score limit table for credit approval."""
    try:
        return read_csv(SCORE_LIMITE_CSV)
    except Exception as e:
        print(f"Error reading score limits: {e}")
        return None


def update_credit_limit_request_status(cpf: str, new_status: str) -> bool:
    """Update the status of a credit limit request."""
    try:
        df = read_csv(SOLICITACOES_CSV)
        
        # Get the most recent request for this CPF
        cpf_requests = df[df['cpf_cliente'] == cpf]
        if cpf_requests.empty:
            return False
        
        # Update the last (most recent) request
        last_request_idx = cpf_requests.index[-1]
        df.loc[last_request_idx, 'status_pedido'] = new_status
        
        return write_csv(SOLICITACOES_CSV, df)
    except Exception as e:
        print(f"Error updating request status: {e}")
        return False


def get_client_latest_request(cpf: str) -> Optional[Dict[str, Any]]:
    """Get the latest credit limit request for a client."""
    try:
        df = read_csv(SOLICITACOES_CSV)
        cpf_requests = df[df['cpf_cliente'] == cpf]
        
        if cpf_requests.empty:
            return None
        
        return cpf_requests.iloc[-1].to_dict()
    except Exception as e:
        print(f"Error retrieving latest request: {e}")
        return None
