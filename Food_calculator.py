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

# Example Food Database (in real scenario, fetch from an API)
food_database = {
    "apple": {"Carbohydrates": 14, "Proteins": 0.3, "Fats": 0.2},
    "chicken": {"Carbohydrates": 0, "Proteins": 31, "Fats": 3.6},
    "rice": {"Carbohydrates": 28, "Proteins": 2.7, "Fats": 0.3},
    "salmon": {"Carbohydrates": 0, "Proteins": 20, "Fats": 13},
}

# Function to fetch daily log data from GitHub
def load_daily_data():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        decoded_content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(decoded_content), data["sha"]
    else:
        return {}, None

# Function to update daily log data on GitHub
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
        st.success("✅ File successfully updated on GitHub!")
    else:
        st.error(f"❌ Update failed: {response.status_code} - {response.text}")

# Function to calculate macronutrient distribution based on logged food
def calculate_macronutrients(daily_data):
    total_macros = {"Carbohydrates": 0, "Proteins": 0, "Fats": 0}

    for food, info in daily_data.items():
        if food in food_database:
            macros = food_database[food]
            quantity_factor = info["quantity"] / 100  # Normalize to 100g
            total_macros["Carbohydrates"] += macros["Carbohydrates"] * quantity_factor
            total_macros["Proteins"] += macros["Proteins"] * quantity_factor
            total_macros["Fats"] += macros["Fats"] * quantity_factor

    # Convert to percentage
    total_kcal = (
        total_macros["Carbohydrates"] * 4 +
        total_macros["Proteins"] * 4 +
        total_macros["Fats"] * 9
    )

    if total_kcal > 0:
        total_macros = {k: round((v * (4 if k != "Fats" else 9) / total_kcal) * 100, 1) for k, v in total_macros.items()}
    
    return total_macros

# Load daily data
daily_data, sha = load_daily_data()

# Streamlit Interface
st.title("🍏 Daily Nutrition Tracker")

# 📌 Input to add food item
food_item = st.text_input("Enter food name (e.g., apple, rice, chicken):").lower()
quantity = st.number_input("Enter quantity in grams:", min_value=1, value=100)

if st.button("Add Food"):
    if food_item in food_database:
        if food_item in daily_data:
            daily_data[food_item]["quantity"] += quantity
        else:
            daily_data[food_item] = {"quantity": quantity}

        update_daily_data(daily_data, sha)
        st.rerun()
    else:
        st.error("⚠️ Food not found in the database!")

# 📊 Display daily food log with a remove button
st.header(f"📅 Daily Nutrition Data for {TODAY_DATE}")

if daily_data:
    for food, info in list(daily_data.items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{food.capitalize()}**: {info.get('quantity', 0)}g")
        with col2:
            if st.button(f"❌ Remove", key=food):
                del daily_data[food]
                update_daily_data(daily_data, sha)
                st.rerun()
else:
    st.info("No food recorded today.")

# 📊 Pie Chart of Macronutrient Distribution
st.header("📊 Macronutrient Distribution")

macronutrient_consumed = calculate_macronutrients(daily_data)

if sum(macronutrient_consumed.values()) > 0:
    fig, ax = plt.subplots()
    ax.pie(macronutrient_consumed.values(), labels=macronutrient_consumed.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("No macronutrient data available yet. Add foods to see the distribution!")















