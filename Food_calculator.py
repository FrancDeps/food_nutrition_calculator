
import streamlit as st
import requests
import json
from datetime import datetime

# Configura GitHub
GITHUB_TOKEN = "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"  # 🔴 Sostituiscilo con il tuo token GitHub
GITHUB_REPO = "FrancDeps/food_nutrition_calculator"
GITHUB_FOLDER = "daily_logs"  # Cartella dove salvare i file
TODAY_DATE = datetime.today().strftime("%Y-%m-%d")  # Genera il nome del file (YYYY-MM-DD.json)
GITHUB_FILE_PATH = f"{GITHUB_FOLDER}/{TODAY_DATE}.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

# Funzione per scaricare i dati giornalieri da GitHub
def carica_dati_giornalieri():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return json.loads(requests.get(data["download_url"]).text), data["sha"]
    else:
        return {}, None  # Se il file non esiste, restituisce un dizionario vuoto

# Funzione per aggiornare i dati giornalieri su GitHub
def aggiorna_dati_giornalieri(nuovi_dati, sha):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
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

# Mostra i dati della giornata
st.header(f"📅 Dati nutrizionali del {TODAY_DATE}")
if dati_giornalieri:
    for alimento, info in dati_giornalieri.items():
        st.write(f"**{alimento.capitalize()}**: {info['quantita']}g")
else:
    st.info("Nessun alimento registrato oggi.")


