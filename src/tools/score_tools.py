"""Score calculation and management tools."""
from typing import Dict, Tuple, Optional
from src.utils.constants import SCORE_WEIGHTS
from src.tools.csv_tools import (
    get_cliente_by_cpf, 
    update_cliente_score,
    get_score_limits
)


def calculate_credit_score(
    renda_mensal: float,
    tipo_emprego: str,
    despesas_fixas: float,
    num_dependentes: int,
    tem_dividas: str
) -> float:
    """
    Calculate credit score using weighted formula.
    Score range: 0-1000
    """
    # Validate inputs
    if renda_mensal <= 0 or despesas_fixas < 0:
        return 0
    
    if tipo_emprego not in SCORE_WEIGHTS["peso_emprego"]:
        tipo_emprego = "desempregado"
    
    # Normalize dependents category
    dependents_key = num_dependentes if num_dependentes in SCORE_WEIGHTS["peso_dependentes"] else "3+"
    
    # Normalize debt status
    divida_key = "sim" if tem_dividas.lower() in ["sim", "yes", "true", "s"] else "não"
    
    # Calculate components
    income_ratio = min((renda_mensal / (despesas_fixas + 1)) * SCORE_WEIGHTS["peso_renda"], 1000)
    employment_score = SCORE_WEIGHTS["peso_emprego"][tipo_emprego]
    dependents_score = SCORE_WEIGHTS["peso_dependentes"][dependents_key]
    debt_score = SCORE_WEIGHTS["peso_dividas"][divida_key]
    
    # Sum all components
    total_score = income_ratio + employment_score + dependents_score + debt_score
    
    # Normalize to 0-1000 range
    score = max(0, min(1000, total_score))
    
    return round(score, 2)


def check_credit_limit_approval(cpf: str, novo_limite: float) -> Tuple[bool, str]:
    """
    Check if the requested credit limit is approved based on client's score.
    Returns (approved: bool, message: str)
    """
    # Get client info
    cliente = get_cliente_by_cpf(cpf)
    if not cliente:
        return False, "Cliente não encontrado."
    
    client_score = cliente.get('score', 0)
    
    # Get score limits table
    score_limits = get_score_limits()
    if score_limits is None:
        return False, "Erro ao acessar tabela de limites de score."
    
    # Find applicable limit range
    for _, row in score_limits.iterrows():
        if row['score_minimo'] <= client_score <= row['score_maximo']:
            limite_minimo = row['limite_minimo']
            limite_maximo = row['limite_maximo']
            
            if limite_minimo <= novo_limite <= limite_maximo:
                return True, f"Crédito aprovado! Novo limite: R$ {novo_limite:.2f}"
            else:
                return False, f"Limite solicitado fora do permitido. Máximo para seu score: R$ {limite_maximo:.2f}"
    
    return False, "Seu score não permite este limite de crédito."


def update_score_in_database(cpf: str, new_score: float) -> Tuple[bool, str]:
    """Update client's score in the database."""
    try:
        if update_cliente_score(cpf, new_score):
            return True, f"Score atualizado com sucesso! Novo score: {new_score}"
        else:
            return False, "Erro ao atualizar score."
    except Exception as e:
        return False, f"Erro ao atualizar score: {str(e)}"


def get_client_score(cpf: str) -> Optional[float]:
    """Get client's current credit score."""
    try:
        cliente = get_cliente_by_cpf(cpf)
        if cliente:
            return cliente.get('score', None)
        return None
    except Exception as e:
        print(f"Error getting client score: {e}")
        return None
