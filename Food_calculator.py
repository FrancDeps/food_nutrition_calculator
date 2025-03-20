import streamlit as st
import requests
import json
import base64
import matplotlib.pyplot as plt
from datetime import datetime

# GitHub Configuration
GITHUB_TOKEN1 = "ghp_tKJMlnBlpxtk75K"
GITHUB_TOKEN2 = "bmWQNjJTIW40HeV1jGcrg"  # 🔴 Replace with your GitHub token
GITHUB_TOKEN = GITHUB_TOKEN1 + GITHUB_TOKEN2
GITHUB_REPO = "FrancDeps/food_nutrition_calculator"
GITHUB_FOLDER = "daily_logs"
TODAY_DATE = datetime.today().strftime("%Y-%m-%d")
GITHUB_FILE_PATH = f"{GITHUB_FOLDER}/{TODAY_DATE}.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

# Load Food Database from JSON File
@st.cache_data
def load_food_database():
    try:
        with open("nutritional_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("❌ Error: `nutritional_data.json` not found. Please add the file to the project folder.")
        return {}

food_database = load_food_database()

# Load daily data from GitHub
def load_daily_data():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            decoded_content = base64.b64decode(data["content"]).decode("utf-8")
            return json.loads(decoded_content), data.get("sha")
        except (json.JSONDecodeError, KeyError):
            st.error("⚠️ Error reading data from GitHub. The file may be corrupted.")
            return {}, None
    elif response.status_code == 404:
        return {}, None  # File does not exist, return empty data
    else:
        st.error(f"❌ GitHub API error {response.status_code}: Unable to load data.")
        return {}, None

# Update daily data on GitHub
def update_daily_data(new_data, sha):
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    json_data = json.dumps(new_data, indent=4)
    encoded_data = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": f"Updated daily log {TODAY_DATE}",
        "content": encoded_data,
        "sha": sha if sha else ""
    }
    
    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        st.success("✅ Daily log successfully updated on GitHub!")
    else:
        st.error(f"❌ Error updating GitHub file: {response.status_code}. Please try again.")

# Initialize session state
if "daily_data" not in st.session_state:
    st.session_state.daily_data, st.session_state.sha = load_daily_data()

# Streamlit Interface
st.title("🍏 Daily Nutrition Tracker")

# 📌 User Inputs
gender = st.radio("Select your gender:", ["Male", "Female"])
activity_level = st.selectbox("Select your activity level:", ["Sedentary", "Moderately Active", "Very Active"])
goal = st.selectbox("What is your goal?", ["Weight Loss", "Muscle Gain", "Endurance Training", "Ketogenic Diet"])

# 📌 Add Food Input
food_item = st.text_input("Enter food name (e.g., rice, apple, chicken):").lower().strip()
quantity = st.number_input("Enter quantity in grams:", min_value=1, value=100)

if st.button("Add Food"):
    if food_item in food_database:
        if food_item in st.session_state.daily_data:
            st.session_state.daily_data[food_item]["quantity"] += quantity
        else:
            st.session_state.daily_data[food_item] = {"quantity": quantity}
        update_daily_data(st.session_state.daily_data, st.session_state.sha)
        st.experimental_rerun()
    else:
        st.error("⚠️ Food not found in the database. Please check spelling or update the database.")

# 📊 Display Daily Food Log
st.header(f"📅 Daily Nutrition Data for {TODAY_DATE}")
if st.session_state.daily_data:
    for food, info in list(st.session_state.daily_data.items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{food.capitalize()}**: {info['quantity']}g")
        with col2:
            if st.button(f"❌ Remove {food}", key=f"remove_{food}"):
                if food in st.session_state.daily_data:
                    del st.session_state.daily_data[food]
                    update_daily_data(st.session_state.daily_data, st.session_state.sha)
                    st.experimental_rerun()
else:
    st.info("No food recorded today.")

# 📊 Macronutrient Calculation
macronutrient_totals = {"Carbohydrates": 0, "Proteins": 0, "Fats": 0}

for food, info in st.session_state.daily_data.items():
    if food in food_database:
        quantity = info["quantity"] / 100
        for macro in macronutrient_totals:
            macronutrient_totals[macro] += food_database[food].get(macro, 0) * quantity

total_macros = sum(macronutrient_totals.values())
macronutrient_percentages = {k: round((v / total_macros) * 100, 1) if total_macros > 0 else 0 for k, v in macronutrient_totals.items()}

if total_macros > 0:
    st.header("📊 Macronutrient Distribution")
    fig, ax = plt.subplots()
    ax.pie(macronutrient_percentages.values(), labels=macronutrient_percentages.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.warning("⚠️ No food added yet. Please enter food items to see macronutrient distribution.")



















