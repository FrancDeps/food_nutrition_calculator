import json
import streamlit as st
import matplotlib.pyplot as plt

# File di input (database alimenti pre-esistente)
file_input = "nutritional_data.json"
# File di output (alimenti cercati e salvati dall'utente)
file_output = "searched_foods.json"

# Funzione per caricare dati da un file JSON
def carica_dati(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Funzione per salvare dati in un file JSON
def salva_dati(file_path, dati):
    with open(file_path, "w") as file:
        json.dump(dati, file, indent=4)

# Carica i dati dal file di input (database originale)
dati_nutrizionali = carica_dati(file_input)
# Carica i dati dal file di output (storico degli alimenti cercati)
storico_alimenti = carica_dati(file_output)

# Inizializza i valori totali
tot_calorie = 0
tot_proteine = 0
tot_carboidrati = 0
tot_grassi = 0

# Funzione per ottenere i valori nutrizionali proporzionati alla quantità
def ottieni_nutrienti(alimento, quantita, dati_originali, dati_storico, file_output):
    alimento = alimento.lower()
    if alimento in dati_originali:
        valori_base = dati_originali[alimento]
        proporzione = quantita / 100  # Per adattare ai grammi specificati
        
        valori = {
            "calorie": valori_base["calorie"] * proporzione,
            "proteine": valori_base["proteine"] * proporzione,
            "carboidrati": valori_base["carboidrati"] * proporzione,
            "grassi": valori_base["grassi"] * proporzione,
            "quantita": quantita
        }
        
        dati_storico[alimento] = valori  # Salva nel file di storico
        salva_dati(file_output, dati_storico)
        return valori
    else:
        return None

# Streamlit UI
st.title("Nutritional Tracker")

alimento = st.text_input("Inserisci il nome dell'alimento:")
quantita = st.number_input("Inserisci la quantità in grammi:", min_value=1, value=100)

if st.button("Aggiungi alimento"):
    if alimento:
        valori = ottieni_nutrienti(alimento, quantita, dati_nutrizionali, storico_alimenti, file_output)
        if valori:
            st.success(f"Aggiunto {quantita}g di {alimento}")
        else:
            st.error("Alimento non trovato nel database.")

# Calcola i totali
for alimento, valori in storico_alimenti.items():
    tot_calorie += valori["calorie"]
    tot_proteine += valori["proteine"]
    tot_carboidrati += valori["carboidrati"]
    tot_grassi += valori["grassi"]

# Mostra i totali
st.header("Totale valori nutrizionali")
st.write(f"**Totale Calorie:** {tot_calorie:.2f} kcal")
st.write(f"**Totale Proteine:** {tot_proteine:.2f} g")
st.write(f"**Totale Carboidrati:** {tot_carboidrati:.2f} g")
st.write(f"**Totale Grassi:** {tot_grassi:.2f} g")

# Grafico a torta con Streamlit
st.header("Distribuzione Macronutrienti")
st.pyplot(plt.figure(figsize=(6, 6)))
labels = ["Proteine", "Carboidrati", "Grassi"]
values = [tot_proteine, tot_carboidrati, tot_grassi]
plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=["blue", "orange", "red"])
st.pyplot()

# Confronto con benchmark calorico
benchmark_calorie = 2000
surplus_deficit = tot_calorie - benchmark_calorie
st.header("Confronto con benchmark calorico")
if surplus_deficit > 0:
    st.warning(f"Sei in surplus calorico di {surplus_deficit:.2f} kcal.")
elif surplus_deficit < 0:
    st.info(f"Sei in deficit calorico di {abs(surplus_deficit):.2f} kcal.")
else:
    st.success("Sei esattamente a 2000 kcal.")

    
