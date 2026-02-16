# Score Calculation Weights
SCORE_WEIGHTS = {
    "peso_renda": 30,
    "peso_emprego": {
        "formal": 300,
        "autônomo": 200,
        "desempregado": 0
    },
    "peso_dependentes": {
        0: 100,
        1: 80,
        2: 60,
        "3+": 30
    },
    "peso_dividas": {
        "sim": -100,
        "não": 100
    }
}

# Messages
MESSAGES = {
    "greeting": "Bem-vindo ao Banco Ágil! Como posso ajudá-lo hoje?",
    "auth_failed": "Desculpe, não consegui autenticar suas informações.",
    "auth_success": "Ótimo! Você foi autenticado com sucesso.",
    "max_attempts": "Você excedeu o limite de tentativas de autenticação. O atendimento será encerrado.",
    "farewell": "Obrigado pela preferência no Banco Ágil. Até logo!"
}

# Employment Types
EMPLOYMENT_TYPES = ["formal", "autônomo", "desempregado"]

# Dependencies Categories
DEPENDENTS_CATEGORIES = {
    0: 0,
    1: 1,
    2: 2,
    "3+": "3+"
}

# Debt Status
DEBT_STATUS = ["sim", "não"]
