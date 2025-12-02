import streamlit as st

st.set_page_config(page_title="Orientation IA", page_icon="🎓")

st.title("🎓 Ton Guide d'Orientation Intelligent")

st.markdown("""
    Bienvenue ! 👋  
    Tu es ici pour trouver la filière qui te ressemble vraiment.

    Notre assistant utilise l'IA pour analyser :  
    - ta personnalité  
    - tes préférences  
    - ta façon d'apprendre  
    - ce que tu aimes (et ce que tu n'aimes pas)  

    À partir de tes réponses, il construit ton **profil d'orientation** et te propose :  
    - 🧠 un **quiz intelligent**  
    - 🎯 une **recommandation personnalisée**  
    - 💬 ou simplement une **conversation pour explorer tes options**

    ### Pourquoi l'essayer ?
    - C'est rapide  
    - C'est simple  
    - C'est personnalisé  
    - Et surtout, c'est fait pour t'aider à y voir clair

    **Prêt(e) à commencer ?**

""")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.page_link("pages/1_Chat.py", label="🚀 Commencer l'orientation")