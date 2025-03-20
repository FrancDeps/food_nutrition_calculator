import streamlit as st
import requests
import json
import base64
import matplotlib.pyplot as plt
from datetime import datetime

# Configura GitHub
GITHUB_TOKEN1 = "ghp_tKJMlnBlpxtk75K"
GITHUB_TOKEN2 = "bmWQNjJTIW40HeV1jGcrg"  # 🔴 Sostituiscilo con il tuo token GitHub
GITHUB_TOKEN = GITHUB_TOKEN1 + GITHUB_TOKEN2
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

# Linee guida OMS per i macronutrienti (in %)
oms_macros = {"Carboidrati": 50, "Proteine": 20, "Grassi": 30}

# Funzione per scaricare i dati giornalieri da GitHub
def carica_dati_giornalieri():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        contenuto_decodificato = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(contenuto_decodificato), data["sha"]
    else:
        return {}, None  # Se il file non esiste, restituisce un dizionario vuoto

# Funzione per aggiornare i dati giornalieri su GitHub
def aggiorna_dati_giornalieri(nuovi_dati, sha):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Converti il dizionario in JSON
    dati_json = json.dumps(nuovi_dati, indent=4)

    # Codifica in Base64
    dati_base64 = base64.b64encode(dati_json.encode("utf-8")).decode("utf-8")

    # Prepara il payload corretto per GitHub
    payload = {
        "message": f"Aggiornamento dati giornalieri {TODAY_DATE}",
        "content": dati_base64,  # Usa il contenuto in Base64
        "sha": sha if sha else ""  # Se il file non esiste, lascia vuoto
    }

    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        st.success("✅ File aggiornato con successo su GitHub!")
    else:
        st.error(f"❌ Errore nell'aggiornamento: {response.status_code} - {response.text}")

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

# 📊 Mostra i dati della giornata con bottone per rimuovere alimenti
st.header(f"📅 Dati nutrizionali del {TODAY_DATE}")

totale_calorie = sum(v["quantita"] for v in dati_giornalieri.values())  # Somma calorie consumate

if dati_giornalieri:
    for alimento, info in list(dati_giornalieri.items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{alimento.capitalize()}**: {info['quantita']}g")
        with col2:
            if st.button(f"❌ Rimuovi", key=alimento):
                del dati_giornalieri[alimento]
                aggiorna_dati_giornalieri(dati_giornalieri, sha)
                st.rerun()  # Ricarica l'interfaccia dopo la rimozione
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

# 📊 Grafico a torta della distribuzione dei macronutrienti
st.header("📊 Distribuzione dei Macronutrienti")

# Simuliamo i macronutrienti consumati (questo va sostituito con i dati reali se disponibili)
macronutrienti_consumati = {
    "Carboidrati": 55,  # Valori d'esempio
    "Proteine": 18,
    "Grassi": 27
}

# Creazione del grafico a torta
fig, ax = plt.subplots()
ax.pie(macronutrienti_consumati.values(), labels=macronutrienti_consumati.keys(), autopct='%1.1f%%', startangle=90)
ax.axis("equal")  # Mantiene il grafico circolare

st.pyplot(fig)

# 📌 Confronto con le linee guida dell'OMS
st.header("📈 Confronto con le Linee Guida OMS")

for macro, percent in macronutrienti_consumati.items():
    diff = percent - oms_macros[macro]
    if diff > 0:
        st.warning(f"⚠️ Hai consumato **{abs(diff)}%** in più di **{macro}** rispetto alle linee guida OMS.")
    elif diff < 0:
        st.info(f"🔹 Hai consumato **{abs(diff)}%** in meno di **{macro}** rispetto alle linee guida OMS.")
    else:
        st.success(f"✅ Il tuo consumo di **{macro}** è perfettamente in linea con le linee guida OMS!")









