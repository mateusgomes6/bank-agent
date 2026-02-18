"""Streamlit UI for Banco Ágil."""
import streamlit as st
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import BancoAgilApp


# Page configuration
st.set_page_config(
    page_title="Banco Ágil - Sistema de Atendimento",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stChatMessage[data-testid="chatAvatarIcon-user"] {
        background-color: #e3f2fd;
    }
    .stChatMessage[data-testid="chatAvatarIcon-assistant"] {
        background-color: #f3e5f5;
    }
    h1 {
        color: #1976d2;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "app" not in st.session_state:
    st.session_state.app = BancoAgilApp()
    st.session_state.messages = []
    st.session_state.conversation_started = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("🏦 Banco Ágil")
st.subheader("Sistema de Atendimento Inteligente ao Cliente")

# Sidebar
with st.sidebar:
    st.header("Informações")
    
    if st.session_state.conversation_started:
        st.info(f"✅ Status: Conversa ativa")
        
        if st.session_state.app.router.is_authenticated():
            st.success(f"🔐 Autenticado")
            cpf = st.session_state.app.router.get_authenticated_cpf()
            st.text(f"CPF: {cpf}")
        else:
            st.warning("🔓 Não autenticado")
    else:
        st.info("📝 Conversa não iniciada")
    
    st.divider()
    
    # Statistics
    if st.session_state.chat_history:
        summary = st.session_state.app.get_conversation_summary()
        st.subheader("Estatísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mensagens", summary.get("total_messages", 0))
        with col2:
            st.metric("Duração", f"{summary.get('duration_seconds', 0):.0f}s")
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nova Conversa", use_container_width=True):
            st.session_state.app.reset()
            st.session_state.conversation_started = False
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📥 Exportar Log", use_container_width=True):
            history = st.session_state.app.get_conversation_history()
            st.download_button(
                label="Baixar",
                data=str(history),
                file_name="conversa_banco_agil.txt",
                mime="text/plain"
            )
    
    st.divider()
    st.caption("Banco Ágil v1.0")
    st.caption("Sistema de Atendimento com Agentes de IA")

# Main chat interface
container = st.container()

# Display chat history
with container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

# Input area
if st.session_state.conversation_started:
    # Chat input
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Display user message
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        
        # Add to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Process with agent
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            message_placeholder.markdown("⏳ Processando...")
            
            try:
                # Run async function
                response = asyncio.run(st.session_state.app.process_user_input(prompt))
                
                message_placeholder.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Check if conversation ended
                if not st.session_state.app.is_conversation_active():
                    st.info("Conversa encerrada. Clique em 'Nova Conversa' para começar novamente.")
                
            except Exception as e:
                error_msg = f"❌ Erro ao processar: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
else:
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶️ Iniciar Conversa", use_container_width=True, type="primary"):
            try:
                # Start conversation
                greeting = asyncio.run(st.session_state.app.start_conversation())
                
                st.session_state.conversation_started = True
                st.session_state.chat_history = [
                    {"role": "assistant", "content": greeting}
                ]
                st.rerun()
            
            except Exception as e:
                st.error(f"Erro ao iniciar conversa: {str(e)}")
    
    # Welcome message
    st.info("""
    ### 👋 Bem-vindo ao Banco Ágil!
    
    Este é um sistema inteligente de atendimento bancário que oferece:
    
    - **🔐 Autenticação Segura**: Verificação de CPF e data de nascimento
    - **💳 Consulta de Crédito**: Informações sobre seu limite de crédito
    - **📈 Aumento de Limite**: Solicite aumento de crédito de forma fácil
    - **📊 Entrevista de Crédito**: Atualize seu score financeiro
    - **💱 Cotação de Moedas**: Consulte taxas de câmbio em tempo real
    
    **Clique em "Iniciar Conversa" para começar!**
    """)
    
    # Demo credentials
    with st.expander("📋 Dados para Teste"):
        st.markdown("""
        Você pode usar as seguintes credenciais para testar:
        
        | CPF | Data Nascimento | Nome |
        |-----|-----------------|------|
        | 12345678901 | 1990-05-15 | João Silva |
        | 98765432100 | 1988-12-20 | Maria Santos |
        | 55544433322 | 1995-07-10 | Pedro Oliveira |
        """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        © 2026 Banco Ágil - Sistema de Atendimento Inteligente<br>
        <small>Powered by LangChain + Google Gemini</small>
    </div>
""", unsafe_allow_html=True)
