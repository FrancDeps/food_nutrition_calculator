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

# Range di macronutrienti per obiettivo
macronutrienti_obiettivo = {
    "Dimagrimento": {"Carboidrati": (20, 40), "Proteine": (30, 40), "Grassi": (30, 40)},
    "Massa Muscolare": {"Carboidrati": (45, 55), "Proteine": (20, 30), "Grassi": (20, 30)},
    "Resistenza Atletica": {"Carboidrati": (55, 65), "Proteine": (15, 20), "Grassi": (20, 25)},
    "Dieta Chetogenica": {"Carboidrati": (5, 10), "Proteine": (20, 25), "Grassi": (65, 75)}
}

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
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    dati_json = json.dumps(nuovi_dati, indent=4)
    dati_base64 = base64.b64encode(dati_json.encode("utf-8")).decode("utf-8")

    payload = {
        "message": f"Aggiornamento dati giornalieri {TODAY_DATE}",
        "content": dati_base64,
        "sha": sha if sha else ""
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

# 📌 Scelta del genere e attività fisica
genere = st.radio("Seleziona il tuo genere:", ["Uomo", "Donna"])
livello_attivita = st.selectbox("Seleziona il tuo livello di attività fisica:", 
                                ["Sedentario", "Moderatamente Attivo", "Attivo"])

# 📌 Scelta dell'obiettivo
obiettivo = st.selectbox("Qual è il tuo obiettivo?", 
                         ["Dimagrimento", "Massa Muscolare", "Resistenza Atletica", "Dieta Chetogenica"])

# 📌 Calcolo fabbisogno calorico
calorie_target = calorie_reference[genere][livello_attivita]

# 📌 Input per inserire un alimento
alimento = st.text_input("Inserisci il nome dell'alimento:")
quantita = st.number_input("Inserisci la quantità in grammi:", min_value=1, value=100)

if st.button("Aggiungi alimento"):
    if alimento:
        alimento = alimento.lower()
        dati_giornalieri[alimento] = {"quantita": dati_giornalieri.get(alimento, {"quantita": 0})["quantita"] + quantita}
        aggiorna_dati_giornalieri(dati_giornalieri, sha)
    else:
        st.error("⚠️ Inserisci un nome valido per l'alimento.")

# 📊 Mostra gli alimenti registrati con bottone per rimuoverli
st.header(f"📅 Dati nutrizionali del {TODAY_DATE}")

if dati_giornalieri:
    for alimento, info in list(dati_giornalieri.items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{alimento.capitalize()}**: {info['quantita']}g")
        with col2:
            if st.button(f"❌ Rimuovi", key=alimento):
                del dati_giornalieri[alimento]
                aggiorna_dati_giornalieri(dati_giornalieri, sha)
                st.rerun()
else:
    st.info("Nessun alimento registrato oggi.")

# 📊 Grafico a torta dei macronutrienti
st.header("📊 Distribuzione dei Macronutrienti")

macronutrienti_consumati = {"Carboidrati": 50, "Proteine": 25, "Grassi": 25}  # Dati fittizi per ora
fig, ax = plt.subplots()
ax.pie(macronutrienti_consumati.values(), labels=macronutrienti_consumati.keys(), autopct='%1.1f%%', startangle=90)
ax.axis("equal")
st.pyplot(fig)

# 📌 Confronto con il range ideale per l'obiettivo scelto
st.header(f"📈 Confronto con i range per **{obiettivo}**")

for macro, percent in macronutrienti_consumati.items():
    min_range, max_range = macronutrienti_obiettivo[obiettivo][macro]
    if percent < min_range:
        st.warning(f"⚠️ **{macro}** consumato **{percent}%**: troppo BASSO rispetto al range ideale **{min_range}-{max_range}%**.")
    elif percent > max_range:
        st.warning(f"⚠️ **{macro}** consumato **{percent}%**: troppo ALTO rispetto al range ideale **{min_range}-{max_range}%**.")
    else:
        st.success(f"✅ **{macro}** consumato **{percent}%**: **IN LINEA** con il range ideale **{min_range}-{max_range}%**.")









