import streamlit as st
import asyncio
from dotenv import load_dotenv
from agent_create import create_portfolio_agent
from agents import Runner

# Configuration Streamlit
st.set_page_config(
    page_title="Portfolio Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Charger les variables d'environnement
load_dotenv(override=True)

# Titre et description
st.title("🤖 Portfolio Assistant")
st.markdown(
    "Posez des questions sur mes compétences, expériences, projets et formations. "
    "L'agent IA interrogera ma base de données vectorielle pour vous répondre."
)

# Initialiser l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialiser l'agent
if "agent" not in st.session_state:
    try:
        st.session_state.agent = create_portfolio_agent()
        st.session_state.agent_ready = True
    except Exception as e:
        st.session_state.agent_ready = False
        st.error(f"❌ Erreur lors de l'initialisation de l'agent: {e}")

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accepter l'input utilisateur
if prompt := st.chat_input("Posez votre question sur mon portfolio..."):
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Afficher le message utilisateur dans le chat
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Afficher la réponse de l'agent
    if st.session_state.agent_ready:
        with st.chat_message("assistant"):
            with st.spinner("🤔 Réflexion en cours..."):
                try:
                    # Exécuter l'agent de manière asynchrone
                    result = asyncio.run(
                        Runner.run(st.session_state.agent, prompt)
                    )
                    response = result.final_output
                    st.markdown(response)
                    
                    # Ajouter la réponse à l'historique
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    error_message = f"❌ Erreur lors de l'appel à l'agent: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
    else:
        st.error("❌ L'agent n'est pas prêt. Vérifiez votre configuration.")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()

with col2:
    st.markdown("*Portfolio Assistant v1.0*")

with col3:
    st.markdown("💡 Alimenté par OpenAI + Upstash Vector")
