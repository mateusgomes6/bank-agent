import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-pro")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# File Paths
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "src", "data")

CLIENTES_CSV = os.path.join(DATA_DIR, "clientes.csv")
SCORE_LIMITE_CSV = os.path.join(DATA_DIR, "score_limite.csv")
SOLICITACOES_CSV = os.path.join(DATA_DIR, "solicitacoes_aumento_limite.csv")

# Authentication
MAX_AUTH_ATTEMPTS = int(os.getenv("MAX_AUTH_ATTEMPTS", "3"))

# Agent Configuration
AGENTS_CONFIG = {
    "triage": {
        "name": "Agente de Triagem",
        "description": "Realiza autenticação e triagem de clientes"
    },
    "credit": {
        "name": "Agente de Crédito",
        "description": "Gerencia consultas e aumento de limite de crédito"
    },
    "interview": {
        "name": "Agente de Entrevista de Crédito",
        "description": "Realiza entrevista para atualizar score de crédito"
    },
    "exchange": {
        "name": "Agente de Câmbio",
        "description": "Fornece cotações de moedas"
    }
}
