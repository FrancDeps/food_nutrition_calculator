# food_nutrition_calculator

import streamlit as st  # Libreria per l'interfaccia grafica
import pandas as pd  # Libreria per la gestione dei dati
import matplotlib.pyplot as plt  # Libreria per i grafici
import json  # Libreria per il salvataggio dei dati
import requests  # Libreria per API request

# File JSON per salvare i dati
DATA_FILE = "nutritional_data.json"

# Funzione per caricare dati salvati

def carica_dati():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Funzione per salvare dati

def salva_dati(dati):
    with open(DATA_FILE, "w") as file:
        json.dump(dati, file, indent=4)

# Caricamento del database alimentare locale
data = carica_dati()

# Funzione per ottenere dati nutrizionali da API

def ottieni_dati_alimento(alimento):
    API_URL = f"https://api.edamam.com/api/food-database/v2/parser?ingr={alimento}&app_id=YOUR_APP_ID&app_key=YOUR_APP_KEY"
    response = requests.get(API_URL)
    if response.status_code == 200:
        risultato = response.json()
        if "parsed" in risultato and len(risultato["parsed"]) > 0:
            nutrienti = risultato["parsed"][0]["food"]["nutrients"]
            return {
                "calorie": nutrienti.get("ENERC_KCAL", 0),
                "proteine": nutrienti.get("PROCNT", 0),
                "carboidrati": nutrienti.get("CHOCDF", 0),
                "grassi": nutrienti.get("FAT", 0)
            }
    return None

# Interfaccia utente
st.title("🍽️ Calcolatore Nutrizionale con API e Salvataggio Dati")

alimento = st.text_input("Inserisci un alimento")

if st.button("Aggiungi al database"):
    if alimento:
        dati_nutrizionali = ottieni_dati_alimento(alimento)
        if dati_nutrizionali:
            data[alimento] = dati_nutrizionali
            salva_dati(data)
            st.success(f"{alimento.capitalize()} aggiunto con successo!")
        else:
            st.error("Dati non disponibili per questo alimento.")
    else:
        st.error("Inserisci un alimento valido.")

# Selezione multipla di alimenti
alimenti_scelti = st.multiselect("Seleziona gli alimenti", list(data.keys()))

dati_risultati = []
tot_calorie, tot_proteine, tot_carboidrati, tot_grassi = 0, 0, 0, 0

for alimento in alimenti_scelti:
    grammi = st.number_input(f"Inserisci la quantità (g) per {alimento}", min_value=1, value=100, key=alimento)
    if alimento in data:
        calorie = (data[alimento]["calorie"] / 100) * grammi
        proteine = (data[alimento]["proteine"] / 100) * grammi
        carboidrati = (data[alimento]["carboidrati"] / 100) * grammi
        grassi = (data[alimento]["grassi"] / 100) * grammi
        
        tot_calorie += calorie
        tot_proteine += proteine
        tot_carboidrati += carboidrati
        tot_grassi += grassi
        dati_risultati.append([alimento, grammi, calorie, proteine, carboidrati, grassi])

if dati_risultati:
    df = pd.DataFrame(dati_risultati, columns=["Alimento", "Grammi", "Calorie", "Proteine", "Carboidrati", "Grassi"])
    st.write("### 📊 Valori Nutrizionali per i pasti selezionati:")
    st.dataframe(df.style.format({"Calorie": "{:.2f}", "Proteine": "{:.2f}", "Carboidrati": "{:.2f}", "Grassi": "{:.2f}"}))
    
    st.write("### 🔹 Totale della giornata:")
    st.write(f"- **Calorie:** {tot_calorie:.2f} kcal")
    st.write(f"- **Proteine:** {tot_proteine:.2f} g")
    st.write(f"- **Carboidrati:** {tot_carboidrati:.2f} g")
    st.write(f"- **Grassi:** {tot_grassi:.2f} g")
    
    fig, ax = plt.subplots()
    labels = ["Proteine", "Carboidrati", "Grassi"]
    valori = [tot_proteine, tot_carboidrati, tot_grassi]
    ax.pie(valori, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
    ax.set_title("Distribuzione Macronutrienti")
    st.pyplot(fig)
