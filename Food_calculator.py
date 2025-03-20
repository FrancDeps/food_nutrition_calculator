import streamlit as st
import requests
import json
from datetime import datetime

# Configura GitHub
GITHUB_TOKEN = "TUO_PERSONAL_ACCESS_TOKEN"  # 🔴 Sostituiscilo con il tuo token GitHub
GITHUB_REPO = "FrancDeps/food_nutrition_calculator"
GITHUB_FOLDER = "daily_logs"  # Cartella dove salvare i file
TODAY_DATE = datetime.today().strftime("%Y-%m-%d")  # Genera il nome del file (YYYY-MM-DD.json)
GITHUB_FILE_PATH = f"{GITHUB_FOLDER}/{TODAY_DATE}.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

# Livelli di attività fisica e fabbisogno calorico
calorie_reference = {
    "Uomo": {"Sedentario": 2000, "Moderatamente Attivo": 2500, "Attivo": 2800},
    "Donna": {"Sedentario": 1700, "Moderatamente Attivo": 2100, "Attivo": 2500}
}

# Funzione per scaricare i dati giornalieri da GitHub
def carica_dati_giornalieri():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return json.loads(requests.get(data["download_url"]).text), data["sha"]
    else:
        return {}, None  # Se il file non esiste, restituisce un dizionario vuoto

# Funzione per aggiornare i dati giornalieri su GitHub
def aggiorna_dati_giornalieri(nuovi_dati, sha):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    dati_json = json.dumps(nuovi_dati, indent=4)
    payload = {
        "message": f"Aggiornamento dati giornalieri {TODAY_DATE}",
        "content": json.dumps(dati_json).encode("utf-8").decode("unicode_escape"),
        "sha": sha
    }
    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        st.success("✅ File aggiornato con successo su GitHub!")
    else:
        st.error(f"Errore nell'aggiornamento: {response.text}")

# Carica i dati giornalieri
dati_giornalieri, sha = carica_dati_giornalieri()

# Interfaccia Streamlit
st.title("🍏 Tracker Nutrizionale Giornaliero")

# 📌 Scelta del genere
genere = st.radio("Seleziona il tuo genere:", ["Uomo", "Donna"])

# 📌 Scelta del livello di attività fisica
livello_attivita = st.selectbox("Seleziona il tuo livello di attività fisica:", 
                                ["Sedentario", "Moderatamente Attivo", "Attivo"])

# 📌 Calcolo fabbisogno calorico
calorie_target = calorie_reference[genere][livello_attivita]

# Input per inserire un alimento
alimento = st.text_input("Inserisci il nome dell'alimento:")
quantita = st.number_input("Inserisci la quantità in grammi:", min_value=1, value=100)

if st.button("Aggiungi alimento"):
    if alimento:
        alimento = alimento.lower()
        if alimento in dati_giornalieri:
            dati_giornalieri[alimento]["quantita"] += quantita
        else:
            dati_giornalieri[alimento] = {"quantita": quantita}

        # Aggiorna il file su GitHub
        aggiorna_dati_giornalieri(dati_giornalieri, sha)
    else:
        st.error("⚠️ Inserisci un nome valido per l'alimento.")

# 📊 Mostra i dati della giornata
st.header(f"📅 Dati nutrizionali del {TODAY_DATE}")

totale_calorie = sum(v["quantita"] for v in dati_giornalieri.values())  # Somma calorie consumate

if dati_giornalieri:
    for alimento, info in dati_giornalieri.items():
        st.write(f"**{alimento.capitalize()}**: {info['quantita']}g")
else:
    st.info("Nessun alimento registrato oggi.")

# 🔥 Calcolo del deficit o surplus calorico
bilancio = calorie_target - totale_calorie

st.header("⚖️ Bilancio calorico giornaliero")
if bilancio > 0:
    st.info(f"🔥 Sei in **deficit calorico** di **{bilancio} kcal**.")
elif bilancio < 0:
    st.warning(f"⚠️ Sei in **surplus calorico** di **{abs(bilancio)} kcal**.")
else:
    st.success("✅ Hai raggiunto il tuo fabbisogno calorico esatto!")




















