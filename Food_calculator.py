import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Caricare i dati dal file JSON (puoi sostituirlo con il tuo dataset)
import json

with open("food_data.json", "r") as f:
    food_data = json.load(f)

df = pd.DataFrame(food_data)

# Inizializzare lo stato della sessione per la lista di alimenti selezionati
if "selected_foods" not in st.session_state:
    st.session_state.selected_foods = []

# Titolo dell'app
st.title("Macronutrienti per Alimenti Selezionati")

# Selettore multiplo di alimenti
selected_foods = st.multiselect("Seleziona gli alimenti", df["name"].tolist(), default=st.session_state.selected_foods)

# Aggiornare la selezione nello stato della sessione
st.session_state.selected_foods = selected_foods

# Filtrare il dataframe con gli alimenti selezionati
filtered_df = df[df["name"].isin(st.session_state.selected_foods)]

# Calcolare i macronutrienti totali
if not filtered_df.empty:
    total_protein = filtered_df["protein"].sum()
    total_carbs = filtered_df["carbs"].sum()
    total_fat = filtered_df["fat"].sum()

    # Creare il grafico a torta
    fig, ax = plt.subplots()
    labels = ["Proteine", "Carboidrati", "Grassi"]
    values = [total_protein, total_carbs, total_fat]
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Per mantenere il grafico proporzionato

    # Mostrare i risultati e il grafico
    st.write(f"**Proteine Totali:** {total_protein}g")
    st.write(f"**Carboidrati Totali:** {total_carbs}g")
    st.write(f"**Grassi Totali:** {total_fat}g")
    st.pyplot(fig)
else:
    st.write("Seleziona almeno un alimento per visualizzare il grafico.")













