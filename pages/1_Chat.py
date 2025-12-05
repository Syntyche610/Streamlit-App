import json
import streamlit as st
from openai import OpenAI


# Charger le fichier json sur Streamlit

def load_file(path="filieres.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Impossible de charger {path} : {e}")
        return []

file = load_file()


# Gérer les sessions

if "profile" not in st.session_state:
    st.session_state.profile = {
        "interests": None,
        "favorite_subjects": None,
        "personality": None,
        "work_style": None,
        "limitations": None
    }

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Coucouu 👋 Je suis ton conseiller d'orientation. Dis moi, c'est quoi tes centres d'intérêts ?"}]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "show_final_options" not in st.session_state:
    st.session_state.options = False

if "mode" not in st.session_state:
    st.session_state.mode = ""

if "options" not in st.session_state:
    st.session_state.options = False



# Formulaire d'inscription



# Formulaire de connexion

# if not st.session_state.authenticated:
#     with st.form(key="Formulaire de connexion", clear_on_submit=True, border=False, enter_to_submit=True):
#         username = st.text_input("Nom d'utilisateur: ")
#         password = st.text_input("Mot de passe: ", type="password")

#         submit = st.form_submit_button("Connexion")
    
#     if submit:
#         if password == st.secrets.password:
#             st.session_state.authenticated = True
#             st.success(f"{username} est connecté.")
#             st.rerun()
#         else:
#             st.error("Mot de passe incorrect !")
# else:
#     st.title("Page d'acceuil.")



# Connecter openai
OPENAI_KEY = st.secrets["api_key"]
if not OPENAI_KEY:
    st.error("⚠️ Défini la variable d'environnement OPENAI_API_KEY avant de lancer.")
    st.stop()

client = OpenAI(api_key=OPENAI_KEY)



# Fonction qui appelle l'agent AI

def ask_your_bot(system, user):
    response = client.chat.completions.create(
        model= "gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )

    return response.choices[0].message.content



# Fonction qui détecte les champs vide du profil

def missing_fields(profile):
    return [key for key, value in profile.items() if value is None]



# Fonction qui pose des questions pour remplir le profil

def targeted_questions(profile):
    missing = missing_fields(profile)

    system = f"""
        Tu es un conseiller d'orientation pour nouveaux bacheliers. 
        On te donne le profil partiellement rempli et le dernier message de l'utilisateur. 
        Ta tâche : formuler UNE QUESTION courte et très ciblée pour remplir un seul champ manquant du profil. 
        Ne fais aucune recommandation.
    """

    user = f"""
        Profil actuel de l'étudiant: {profile}

        Valeurs manquantes: {missing}

        Ta mission :
        - Pose UNE seule question.
        - Elle doit être courte, claire.
        - Elle doit viser précisément un élément manquant.
        - Elle doit se baser sur ce que l'étudiant vient de dire.
        - Ne fais AUCUNE recommandation pour le moment.

        Règles :
        1. Détection d'incertitude :
        - Si l'utilisateur dit "je ne sais pas", "aucune idée", "je suis perdu(e)", etc.
        - Tu poses une question plus simple, guidée, et toujours liée à l'orientation.
        - Tu proposes toujours 2 ou 3 options concrètes.

        2. Détection du hors-sujet :
        - Si le message n'a aucun lien avec les études, l'orientation ou les intérêts scolaires
        - Tu n'y réponds pas directement.
        - Tu ramènes l'utilisateur vers le thème par une question simple.
    """

    return ask_your_bot(system, user)



# Fonction qui met à jour le profil de l'utilisateur en fonction des réponses

def update_profile(message):

    def analyze_user_message(message):

        system = f"""
            Tu es un assistant d'orientation pour étudiants qui extrait des infos de profil étudiant.
            Analyse le texte de l'utilisateur et rends un JSON strict.
            
            Mets à jour uniquement les champs suivants si tu détectes une information :
            - interests
            - favorite_subjects 
            - personality
            - work_style
            - limitations
        """

        user = f"""
            Analyse ce message de l'utilisateur : "{message}"

            Ta réponse doit être STRICTEMENT un JSON valide, sans texte autour.

            Format attendu :
            {{
                "interests": ...,
                "favorite_subjects": ...,
                "personality": ...,
                "work_style": ...,
                "limitations": ...
            }}
        """

        response = ask_your_bot(system, user)

        raw = response.strip()
        
        import json, re
        
        try:

            data = json.loads(raw)
        except json.JSONDecodeError:
            json_str = re.search(r'\{.*\}', raw, flags=re.S).group(0)
            data = json.loads(json_str)

        return data
    

    data = analyze_user_message(message)
    print(f"Data: {data}")

    profile = st.session_state.profile

    for key, value in data.items():
        if value is not None:
            profile[key] = value
    
    print(f"Profile: {profile}\n")



# Fonction qui recommande les filières en fonction du profil et du fichier JSON

def personalized_suggestions(profile, filieres_json):
    system = f"""
        Tu es un conseiller d'orientation professionnel pour futurs étudiants.
        Tu donnes des propositions de filières et de metiers en te basant sur le profil de l'utilisateur et les informations du fichier JSON si nécéssaire.
    """
    user = f"""
        Voici le profil de l'utilisateur : {profile}.
        Voici les filières disponibles : {filieres_json}.

        Donne 3 filières + 3 métiers adaptés au profil,
        avec une explication personnalisée.
        Pas de réponses générales.
    """
    return ask_your_bot(system, user)



# Interface Streamlit
st.title("Chat")

with st.sidebar:
    st.title("Chat")
    

cont = st.container(height=600)


with st.spinner("Patiente un instant..."):
    if user_input := st.chat_input("Écris ici..."):

        update_profile(user_input)

        missing = missing_fields(st.session_state.profile)

        if missing:
            reply = targeted_questions(st.session_state.profile)
            # st.session_state.messages.append({"role": "assistant", "content": reply})

        else:
            reply = "Super, j'ai tout ce qu'il me faut ! Tu veux que je te propose un quiz personnalisé pour affiner ta filière idéale ? 🙂"
            st.session_state.options = True

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": reply})


if st.session_state.options:
    col1, col2 = st.columns(2)

    st.write("#### Choisis une option:")

    with col1:
        if st.button("Quiz", key='q'):
            st.switch_page("pages/2_Quiz.py")

    with col2:
        if st.button("Recommandation de filières", key='recom'):
            with st.spinner("Génération en cours..."):
                recom = personalized_suggestions(st.session_state.profile, file)
                st.session_state.mode = "recommend"

if st.session_state.mode == "recommend":
    st.session_state.messages.append({"role": "assistant", "content": recom})

for message in st.session_state.messages:
    cont.chat_message(message["role"]).write(message["content"])