import streamlit as st 
import requests
import json
import base64
import matplotlib.pyplot as plt
from datetime import datetime

# GitHub Configuration
GITHUB_TOKEN1 = "ghp_tKJMlnBlpxtk75K"
GITHUB_TOKEN2 = "bmWQNjJTIW40HeV1jGcrg"
GITHUB_TOKEN = GITHUB_TOKEN1 + GITHUB_TOKEN2 #token è il codice segreto di github che mi permette di lavorare con github
GITHUB_REPO = "FrancDeps/food_nutrition_calculator" 
GITHUB_FOLDER = "daily_logs" #cartella dove salvo i dati giornalieri
TODAY_DATE = datetime.today().strftime("%Y-%m-%d") #prende la data attuale con il formato year month day. 
GITHUB_FILE_PATH = f"{GITHUB_FOLDER}/{TODAY_DATE}.json" #percorso che fa la data, directory, deve trovare il nome del file di oggi.
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}" #creazioni di nuovi file li può fare con api, usato per modificare i file giornlaieri. 

# Load Food Database from JSON File
def load_food_database():
    try:
        with open("nutritional_data.json", "r") as file: #as file: dichiarazione del oggetto (file)
            food_list = json.load(file) #legge e tutto il file lo carica nella variabile food list
            return {item["name"]: item for item in food_list}  # ritorna e lo converte in dizionario, del tipo "pollo" => {grassi,proteine,carboidrati}
    except FileNotFoundError:
        st.error("❌ Error: `nutritional_data.json` not found. Make sure the file is in the project folder.")
        return {} #assegan il valore alla funzione

food_database = load_food_database() #salvare la lista degli alimenti sotto il nome food_database, 

# Load daily data from GitHub
def load_daily_data():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} #per instaurare una connessione con API di github dal mio codice che ci permettera di lavorare su GIthub
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200: #se la richeista va a buon fine, compie l'operazione
        data = response.json()
        decoded_content = base64.b64decode(data["content"]).decode("utf-8") # è un decoding
        return json.loads(decoded_content), data["sha"]
    else:
        return {}, None #altrimenti da NONE. 

# Update daily data on GitHub
def update_daily_data(new_data, sha):    #funzione che si occupa di aggiornare il file di oggi 
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}  #identico a quello sopra, per instaurare connesione con API
    json_data = json.dumps(new_data, indent=4) #salva in formato json gli alimenti consumati durante la giornata
    encoded_data = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")

    payload = {    #contenuto che viene inviato a github
        "message": f"Updated daily log {TODAY_DATE}",
        "content": encoded_data,
        "sha": sha if sha else ""
    }

    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)  #invia il payload con i dati aggiornati e aspetta la risposta da github
    if response.status_code in [200, 201]: #controlla che ci sia una risposta positiva
        st.success("✅ File successfully updated on GitHub!")

# Initialize session state #serve per salvare dati tra i vari aggiornamenti della pagina se la ricarichiamo
if "daily_data" not in st.session_state: #se non è caricata nei dati di questa sessione si va a caricare  load_daily_data
    st.session_state.daily_data, st.session_state.sha = load_daily_data()

# Streamlit Interface
st.title(" Daily Nutrition Tracker")

# 📌 Select gender and activity level
gender = st.radio("Select your gender:", ["Male", "Female"]) #tipo di bottone (uomo, donna, trans)
activity_level = st.selectbox("Select your activity level:", ["Sedentary", "Moderately Active", "Very Active"]) #menu a tendina

# 📌 Select goal
goal = st.selectbox("What is your goal?", ["Weight Loss", "Muscle Gain", "Endurance Training", "Ketogenic Diet"])

# 📌 Input to add food item
food_item = st.text_input("Enter food name (e.g., rice, apple, chicken):").lower() #.lower = lower case, tutte le maiuscole diventano minuscole, 
quantity = st.number_input("Enter quantity in grams:", min_value=1, value=100)

if st.button("Add Food"):
    if food_item in food_database:
        if food_item in st.session_state.daily_data: #se il food item è nella sessione e  ne aggiungo un'ulteriore quantità questa viene sommata a quella precedente
            st.session_state.daily_data[food_item]["quantity"] += quantity
        else:
            st.session_state.daily_data[food_item] = {"quantity": quantity} #altrimenti mette la quantità, (non ho mai messo l'item prima, quel giorn0)

        update_daily_data(st.session_state.daily_data, st.session_state.sha) #salva dentro github i cambiamenti nel Jason
        st.rerun()
    else:
        st.error("⚠️ Food not found in the database. Please check the spelling.") #se non c'è mi ritorna questo erroe con questo segnale

# 📊 Display daily food log
st.header(f"📅 Daily Nutrition Data for {TODAY_DATE}")

if st.session_state.daily_data:
    for food, info in list(st.session_state.daily_data.items()): #per ogni cibo salvato oggi lui crea due colonne 1, c'è il nome del cibo e in colonna 2 il bottone per rimuovere l'item
        col1, col2 = st.columns([4, 1]) #proporzione delle colonne 80% colonna 1 e 20% collona 2
        with col1:
            st.write(f"**{food.capitalize()}**: {info.get('quantity', 0)}g") #
        with col2:
            if st.button(f"❌ Remove {food}", key=f"remove_{food}"):
                del st.session_state.daily_data[food]
                update_daily_data(st.session_state.daily_data, st.session_state.sha)
                st.rerun()
else:
    st.info("No food recorded today.")

# 📊 Calculate Macronutrient Distribution & Total Calories
macronutrient_totals = {"Carbohydrates": 0, "Proteins": 0, "Fats": 0} #partenza da 0 dei macro 
total_calories = 0  

for food, info in st.session_state.daily_data.items():  #somma totale C P G di tutti gli ingredienti
    if food in food_database:
        quantity = info["quantity"] / 100  

        macronutrient_totals["Carbohydrates"] += food_database[food].get("Carbohydrates", 0) * quantity
        macronutrient_totals["Proteins"] += food_database[food].get("Proteins", 0) * quantity
        macronutrient_totals["Fats"] += food_database[food].get("Fats", 0) * quantity 

# Calcolo delle calorie totali
total_calories = (
    macronutrient_totals["Carbohydrates"] * 4 +
    macronutrient_totals["Proteins"] * 4 +
    macronutrient_totals["Fats"] * 9
)

# Display total calories
st.header("🔥 Total Calories Consumed Today")
st.subheader(f"**{total_calories:.0f} kcal**") #per far funzionare la funzione all interno della stringa venga visulizzato il totale dell calorie

# 📌 Compare total calorie intake with recommended daily intake
caloric_needs = {
    "Male": {"Sedentary": 1900, "Moderately Active": 2300, "Very Active": 2800},
    "Female": {"Sedentary": 1500, "Moderately Active": 1900, "Very Active": 2400}
}

recommended_calories = caloric_needs[gender][activity_level] #lista di list relative al gender e al livello di attività 

st.header("⚖️ Caloric Balance Status")
st.subheader(f"Recommended daily intake for a **{gender}, {activity_level}**: **{recommended_calories} kcal**") #f qui e prima mi serve per poter printare variabili in una stringa

if total_calories < recommended_calories:
    st.warning(f"⚠️ You are in a **caloric deficit** of **{recommended_calories - total_calories} kcal**.")
elif total_calories > recommended_calories:
    st.warning(f"⚠️ You are in a **caloric surplus** of **{total_calories - recommended_calories} kcal**.")

    # Funny personalized warning for surplus
    goal_messages = {
        "Weight Loss": "Zio… dovevi perdere peso, non sfondare il frigo! 🥲",
        "Muscle Gain": "Ok massa… ma così ti esplodono i bicipiti e il fegato 💪🍕",
        "Endurance Training": "Stai preparando la maratona o un buffet all you can eat? 🏃‍♂️🍩",
        "Ketogenic Diet": "Zio, è la *keto*, non il *cheat day* 😵🥓"
    }

    st.markdown(
        f"""
        <div style='text-align: center; padding: 20px; border: 5px dashed red; border-radius: 20px; background-color: #fff3f3;'>
            <h1 style='color: red; font-size: 60px; animation: blinker 1s linear infinite;'>💥 STAI SGRAVANDO FRA 💥</h1>
            <h2 style='color: orange; font-size: 26px;'>{goal_messages.get(goal)}</h2>
        </div>
        <style>
            @keyframes blinker {{
                50% {{ opacity: 0; }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.success("✅ Your calorie intake matches your estimated needs!")

# 📊 Calculate Macronutrient Distribution
macronutrient_totals = {"Carbohydrates": 0, "Proteins": 0, "Fats": 0}

for food, info in st.session_state.daily_data.items():
    if food in food_database:
        quantity = info["quantity"] / 100 #Normalize the quantity based on the values ​​per 100g
        for macro in macronutrient_totals:
            macronutrient_totals[macro] += food_database[food][macro] * quantity #Per ogni macronutriente (Carboidrati, Proteine, Grassi), prende il valore per 100g dal database e lo moltiplica per quantity per ottenere i grammi effettivi consumati.

macronutrient_percentages = {"Carbohydrates": 0, "Proteins": 0, "Fats": 0}
total_macros = sum(macronutrient_totals.values())
if total_macros > 0:
    macronutrient_percentages = {k: round((v / total_macros) * 100, 1) for k, v in macronutrient_totals.items()}

    st.header("📊 Macronutrient Distribution")

    fig, ax = plt.subplots()
    ax.pie(macronutrient_percentages.values(), labels=macronutrient_percentages.keys(), autopct='%1.1f%%',
           startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.warning("⚠️ No food added yet. Please enter food items to see macronutrient distribution.")

# 📌 Compare macronutrient intake with target range based on goal
st.header(f"📈 Macronutrient Comparison for **{goal}**") #accordinf to the selected goal the user will see (Weight Loss,Muscle Gain,Endurance Training or Ketogenic Diet)

macronutrient_ranges = {
    "Weight Loss": {"Carbohydrates": (20, 40), "Proteins": (30, 40), "Fats": (30, 40)},
    "Muscle Gain": {"Carbohydrates": (45, 55), "Proteins": (20, 30), "Fats": (20, 30)},
    "Endurance Training": {"Carbohydrates": (55, 65), "Proteins": (15, 20), "Fats": (20, 25)},
    "Ketogenic Diet": {"Carbohydrates": (5, 10), "Proteins": (20, 25), "Fats": (65, 75)}
}

for macro, percent in macronutrient_percentages.items():
    min_range, max_range = macronutrient_ranges[goal][macro]
    if percent < min_range:
        st.warning(
            f"⚠️ **{macro}** intake **{percent}%**: Too LOW compared to the target range **{min_range}-{max_range}%**.")
    elif percent > max_range:
        st.warning(
            f"⚠️ **{macro}** intake **{percent}%**: Too HIGH compared to the target range **{min_range}-{max_range}%**.")
    else:
        st.success(f"✅ **{macro}** intake **{percent}%**: **WITHIN** the target range **{min_range}-{max_range}%**.")


