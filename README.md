# 🏦 Case técnico de Sistema Inteligente de Atendimento Bancário

## 📋 Visão Geral do Projeto

O projeto é um case para a Tech for Humans, empresa de consultoria em tecnologia, especializado em produtos de Inteligência Artificial. Ele se trata de um sistema avançado de atendimento ao cliente baseado em agentes de IA especializados. Desenvolvido para demonstrar a capacidade de sistemas multi-agentes em ambientes bancários, oferece uma experiência fluida e natural de atendimento ao cliente através de múltiplos agents com responsabilidades bem definidas.

### Objetivos Principais
- ✅ Implementar um sistema de autenticação seguro
- ✅ Oferecer consulta e solicitação de aumento de limite de crédito
- ✅ Realizar entrevistas financeiras estruturadas para recalcular scores
- ✅ Fornecer cotações de moedas em tempo real
- ✅ Garantir experiência de atendimento contínua e transparente
- ✅ Manter dados seguros em base de dados CSV

## 🛠️ Stack Tecnológica

| Tecnologia | Função | Por que essa escolha? |
|---|---|---|
| **Python 3.8+** | Linguagem principal | Ecossistema maduro para IA, vasta comunidade e bibliotecas especializadas em NLP e agentes |
| **LangChain** | Framework de agentes | Abstrai a complexidade de orquestração multi-agente, oferecendo gerenciamento de mensagens, histórico de conversa e integração nativa com diversos LLMs |
| **Google Gemini** | Modelo de linguagem (LLM) | API gratuita e acessível via `langchain-google-genai`, com boa capacidade de compreensão e geração de texto em português |
| **Streamlit** | Interface do usuário | Permite criar uma interface de chat conversacional rica com poucas linhas de código, ideal para prototipação rápida |
| **Pandas** | Manipulação de dados | Leitura, escrita e consulta eficiente em arquivos CSV que servem como base de dados do sistema |
| **Pydantic** | Validação de dados | Garante tipagem e validação robusta dos dados trafegados entre agentes e tools |
| **Requests** | Chamadas HTTP | Comunicação com a API de câmbio (exchangerate-api.com) para cotações em tempo real |
| **python-dotenv** | Configuração | Gerenciamento seguro de variáveis de ambiente e chaves de API |

### Por que essa stack?

A combinação **LangChain + Google Gemini** foi escolhida por facilitar a construção de um sistema **multi-agente** com responsabilidades bem separadas. O LangChain fornece a infraestrutura para criar agentes especializados (triagem, crédito, entrevista, câmbio) que se comunicam de forma transparente, enquanto o Gemini atua como o "cérebro" de cada agente, interpretando intenções e gerando respostas naturais.

O **Streamlit** encaixa-se perfeitamente no desafio ao oferecer uma interface de chat pronta para uso, permitindo foco total na lógica dos agentes em vez de desenvolvimento frontend. O uso de **CSV + Pandas** como persistência simplifica a demonstração sem sacrificar a funcionalidade, mantendo o projeto leve e fácil de executar localmente.

## 🏗️ Arquitetura do Sistema

### Agentes Especializados

#### 1. **Agente de Triagem (Triage Agent)**
- **Responsabilidade**: Autenticação de clientes e triagem inicial
- **Fluxo**:
  1. Saudação inicial
  2. Coleta de CPF (validação de formato)
  3. Coleta de data de nascimento
  4. Validação contra base de dados (clientes.csv)
  5. Redirecionamento para agente apropriado
- **Tratamento de Erros**: Até 3 tentativas de autenticação

#### 2. **Agente de Crédito (Credit Agent)**
- **Responsabilidade**: Consulta e aumento de limite de crédito
- **Funcionalidades**:
  - Consultar limite de crédito atual
  - Processar solicitação de aumento
  - Validar limite contra score do cliente (tabela score_limite.csv)
  - Registrar solicitações (solicitacoes_aumento_limite.csv)
  - Aprovar/Rejeitar baseado em análise de score

#### 3. **Agente de Entrevista de Crédito (Credit Interview Agent)**
- **Responsabilidade**: Entrevista financeira para atualizar score
- **Perguntas Coletadas**:
  1. Renda mensal
  2. Tipo de emprego (formal/autônomo/desempregado)
  3. Despesas fixas mensais
  4. Número de dependentes
  5. Existência de dívidas ativas

#### 4. **Agente de Câmbio (Exchange Agent)**
- **Responsabilidade**: Consulta de cotação de moedas em tempo real
- **Moedas Suportadas**: USD, EUR, GBP, JPY, CAD, AUD
- **Fonte**: exchangerate-api.com (API gratuita)

## 🎯 Funcionalidades Implementadas

- ✅ Autenticação segura de clientes com validação de CPF e data de nascimento
- ✅ Limite de 3 tentativas de autenticação com mensagens claras
- ✅ Consulta de limite de crédito em tempo real
- ✅ Solicitação de aumento de limite com registro persistente
- ✅ Validação automática baseada em score creditício
- ✅ Entrevista financeira estruturada (5 questões)
- ✅ Cálculo de score usando fórmula ponderada
- ✅ Atualização persistente de score na base de dados
- ✅ Consulta de cotação de moedas (USD, EUR, GBP, JPY, CAD, AUD)
- ✅ Interface Streamlit intuitiva com chat conversacional
- ✅ Histórico completo de conversa
- ✅ Estatísticas de conversa
- ✅ Tratamento robusto de erros e exceções
- ✅ Experiência transparente entre agentes (cliente não percebe mudanças)

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+
- Chave de API da OpenAI

### Instalação

```bash
# Clone o repositório
git clone https://github.com/mateusgomes6/bank-agent.git
cd bank-agent

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com sua chave de API do Google
```

### Execução

**Interface Streamlit (Recomendada)**:
```bash
streamlit run ui/streamlit_app.py
```

**Teste via CLI**:
```bash
python -m src.main
```

## 📂 Estrutura de Pastas

```
bank-agent/
├── README.md
├── requirements.txt
├── .env
├── src/
│   ├── main.py
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── triage_agent.py
│   │   ├── credit_agent.py
│   │   ├── credit_interview_agent.py
│   │   ├── exchange_agent.py
│   │   └── agent_router.py
│   ├── tools/
│   │   ├── auth_tools.py
│   │   ├── csv_tools.py
│   │   ├── score_tools.py
│   │   └── exchange_tools.py
│   ├── utils/
│   │   ├── config.py
│   │   └── constants.py
│   └── data/
│       ├── clientes.csv
│       ├── score_limite.csv
│       └── solicitacoes_aumento_limite.csv
├── ui/
│   └── streamlit_app.py
└── tests/
    ├── test_agents.py
    └── test_tools.py
```
