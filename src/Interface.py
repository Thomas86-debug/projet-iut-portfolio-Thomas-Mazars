import streamlit as st
import asyncio
from dotenv import load_dotenv
from agent_create import create_portfolio_agent_with_style
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

# Définir les styles de personnalité
PERSONALITY_STYLES = {
    "Professionnel 💼": {
        "emoji": "💼",
        "instruction": "Tu es un assistant professionnel et formel.",
        "description": "Réponses formelles et professionnelles"
    },
    "Pirate 🏴‍☠️": {
        "emoji": "🏴‍☠️",
        "instruction": "Tu parles comme un pirate des Caraïbes ! Utilise des expressions comme 'Moussaillon', 'Sacrebleu', 'Matelot'. Termine souvent par 'Arrr !'",
        "description": "Ahoy ! Parlons comme un vrai pirate"
    },
    "Hôtesse de l'air ✈️": {
        "emoji": "✈️",
        "instruction": "Tu parles comme une hôtesse de l'air chaleureuse et accueillante. Utilise des expressions comme 'Bienvenue à bord', 'Pour votre confort', 'N'hésitez pas'.",
        "description": "Bienvenue à bord, service impeccable"
    },
    "Style Anime ✨": {
        "emoji": "✨",
        "instruction": "Tu parles comme un personnage d'anime enthousiaste ! Utilise des expressions comme 'Sugoi !', 'Kawaii !', 'Ganbatte !', des émojis ✨💫🌟",
        "description": "Kawaii ~ Enthousiaste et énergique !"
    },
    "Squid Game 🎮": {
        "emoji": "🎮",
        "instruction": "Tu parles avec le ton mystérieux et dramatique de Squid Game. Reste poli mais ajoute une ambiance de compétition et de tension.",
        "description": "Bienvenue au jeu... Ambiance mystérieuse"
    }
}

# Initialiser le state pour le style choisi
if "style_selected" not in st.session_state:
    st.session_state.style_selected = False
    st.session_state.current_style = None

# PAGE 1 : Choix du style (avant le chat)
if not st.session_state.style_selected:
    st.title("🎭 Choisissez votre style d'assistant")
    st.markdown("Sélectionnez comment vous souhaitez que votre assistant réponde :")
    
    st.markdown("---")
    
    # Afficher les styles sous forme de colonnes
    cols = st.columns(2)
    
    for idx, (style_name, style_info) in enumerate(PERSONALITY_STYLES.items()):
        col = cols[idx % 2]
        
        with col:
            # Créer une carte cliquable pour chaque style
            with st.container():
                st.markdown(f"### {style_info['emoji']} {style_name.replace(style_info['emoji'], '').strip()}")
                st.markdown(f"*{style_info['description']}*")
                
                if st.button(f"Choisir ce style", key=style_name, use_container_width=True):
                    st.session_state.current_style = style_name
                    st.session_state.style_selected = True
                    st.session_state.messages = []
                    st.rerun()
                
                st.markdown("---")

# PAGE 2 : Interface de chat (après avoir choisi le style)
else:
    # En-tête avec le style choisi
    current_style_info = PERSONALITY_STYLES[st.session_state.current_style]
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.title(f"{current_style_info['emoji']} Portfolio Assistant")
        st.markdown(f"**Style actuel** : {st.session_state.current_style}")
    
    with col3:
        if st.button("🔄 Changer de style", use_container_width=True):
            st.session_state.style_selected = False
            st.session_state.messages = []
            if "agent" in st.session_state:
                del st.session_state.agent
            st.rerun()
    
    # Description
    st.markdown(
        "Posez des questions sur mes compétences, expériences, projets et formations. "
        "L'agent IA interrogera ma base de données vectorielle pour vous répondre."
    )
    
    st.markdown("---")
    
    # Initialiser l'historique des messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialiser l'agent avec le style sélectionné
    if "agent" not in st.session_state:
        try:
            style_instruction = PERSONALITY_STYLES[st.session_state.current_style]["instruction"]
            st.session_state.agent = create_portfolio_agent_with_style(style_instruction)
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
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        st.markdown("*💡 Alimenté par OpenAI + Upstash Vector*")
