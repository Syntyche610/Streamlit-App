import os
import json
import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval


OPENAI_API_KEY = os.getenv("api_key")
if not OPENAI_API_KEY:
    st.error("⚠️ Défini la variable d'environnement OPENAI_API_KEY avant de lancer.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-4.1-mini"


if "student_profile" not in st.session_state:
    st.session_state.student_profile = {
        "interests": None,
        "favorite_subjects": None,
        "personality": None,
        "work_style": None,
        "career_goals": None,
        "limitations": None
    }

if "scores" not in st.session_state:
    st.session_state.scores = {
        "analytical": 0,
        "social": 0,
        "creative": 0,
        "practical": 0, 
    }

if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []



def ask_your_bot(system, user):
    response = client.chat.completions.create(
        model= "gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )

    return response.choices[0].message.content



def build_adaptive_quiz(profile):
    BASE_QUIZ = [
        {
            "q": "Quand tu es face à un problème difficile, ta première réaction est plutôt de :\n1) L'analyser en détail\n2) Imaginer des solutions originales\n3) Demander de l'aide pour comprendre les autres points de vue\n4) Tester directement plusieurs solutions",
            "map": {1:"analytique",2:"creatif",3:"social",4:"pratique"}
        },
        {
            "q": "Parmi ces activités, laquelle t'attire le plus ?\n1) Manipuler des chiffres/données\n2) Créer, écrire, imaginer\n3) Aider les autres directement\n4) Fabriquer/réparer des choses",
            "map": {1:"analytique",2:"creatif",3:"social",4:"pratique"}
        },
        {
            "q": "Dans ta future carrière, qu'est-ce qui compte le plus ?\n1) Stabilité / bon salaire\n2) Impact sur les autres\n3) Liberté créative\n4) Résultats concrets & rapides",
            "map": {1:"organisationnel",2:"social",3:"creatif",4:"pratique"}
        },
        {
            "q": "À l'école, quelles matières préfères-tu ?\n1) Maths/physique\n2) Français/arts/histoire\n3) SVT/sciences humaines\n4) Techno / travaux pratiques",
            "map": {1:"analytique",2:"creatif",3:"social",4:"pratique"}
        },
        {
            "q": "Le genre de réussite qui te ressemble :\n1) Construire une solution technique complexe\n2) Créer une œuvre ou un concept original\n3) Améliorer la vie de quelqu'un\n4) Concevoir/produire quelque chose de concret",
            "map": {1:"analytique",2:"creatif",3:"social",4:"pratique"}
        }
    ]
    
    return BASE_QUIZ

def score_quiz(answers, quiz_questions):
    scores = {"analytique":0,"creatif":0,"social":0,"pratique":0,"organisationnel":0}
    for ans, q in zip(answers, quiz_questions):
        try:
            choice = int(ans.strip())
        except Exception:
            continue

        tag = q["map"][choice]

        if tag:
            scores[tag] = scores.get(tag,0) + 1

    return scores



def personalized_suggestions(profile, scores, filieres_json):
    system = f"""
        Tu es un conseiller d'orientation professionnel pour futurs étudiants.
        Tu donnes des propositions de filières et de metiers en te basant sur le profil de l'utilisateur, les scores du quiz et les informations du fichier JSON si nécéssaire.
    """
    user = f"""
        Voici le profil de l'utilisateur : {profile}.
        Voici les scores du quiz : {scores}.
        Voici les filières disponibles : {filieres_json}.

        Donne 3 filières + 3 métiers adaptés au profil,
        avec une explication personnalisée.
        Pas de réponses générales.
    """
    return ask_your_bot(system, user)



def load_filieres(path="jobs.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Impossible de charger {path} : {e}")
        return []

filieres_data = load_filieres("filieres.json")



# Interface Streamlit

# st.subheader("Profil détecté")
# st.session_state.student_profile

# st.markdown("---")
st.title("Quiz")

with st.sidebar:
    st.title("Quiz")


if not st.session_state.quiz_active:
    if st.button("Démarrer le quiz"):
        st.session_state.quiz_active = True
        st.session_state.quiz_answers = []
        
        st.session_state.quiz_questions = build_adaptive_quiz(st.session_state.student_profile)
        st.rerun()
else:
    question_index = len(st.session_state.quiz_answers)
    quiz_questions = st.session_state.quiz_questions

    if question_index < len(quiz_questions):
        st.markdown(f"**Question {question_index+1} / {len(quiz_questions)}**")
        st.write(quiz_questions[question_index]["q"])

        choice = st.radio("Choisi ta réponse: ", ['1', '2', '3', '4'], key=f"choice_{question_index}", index=None)

        if st.button("Valider", key=f"ok_{question_index}"):
            if choice:
                st.session_state.quiz_answers.append(choice)
                st.rerun()
    else:
        scores = score_quiz(st.session_state.quiz_answers, quiz_questions)
        st.markdown("### Résultats du quiz (scores)")
        st.write(scores)

        if st.button("Recommandation de filières"):
            with st.spinner("Génération en cours..."):
                recom = personalized_suggestions(st.session_state.student_profile, scores, filieres_data)
                st.markdown("### Recommandation détaillée")
                st.write(recom)

        if st.button("Recommencer le quiz"):
            st.session_state.quiz_active = False
            st.session_state.quiz_answers = []
            st.rerun()