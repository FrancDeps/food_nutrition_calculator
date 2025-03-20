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
GITHUB_FOLDER = "daily_logs"  # Folder where files will be saved
TODAY_DATE = datetime.today().strftime("%Y-%m-%d")  # Generate file name (YYYY-MM-DD.json)
GITHUB_FILE_PATH = f"{GITHUB_FOLDER}/{TODAY_DATE}.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

# Caloric ranges based on gender and activity level
calorie_ranges = {
    "Male": {
        "Sedentary": "∼2,000-2,200 kcal",
        "Moderately Active": "∼2,400-2,600 kcal",
        "Very Active": "∼2,800-3,200 kcal"
    },
    "Female": {
        "Sedentary": "∼1,600-1,800 kcal",
        "Moderately Active": "∼2,000-2,200 kcal",
        "Very Active": "∼2,400-2,600 kcal"
    }
}

# Macronutrient percentage ranges based on goals
macronutrient_goals = {
    "Weight Loss": {"Carbohydrates": (20, 40), "Proteins": (30, 40), "Fats": (30, 40)},
    "Muscle Gain": {"Carbohydrates": (45, 55), "Proteins": (20, 30), "Fats": (20, 30)},
    "Endurance Training": {"Carbohydrates": (55, 65), "Proteins": (15, 20), "Fats": (20, 25)},
    "Ketogenic Diet": {"Carbohydrates": (5, 10), "Proteins": (20, 25), "Fats": (65, 75)}
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
        return {}, None  # Returns an empty dictionary if the file doesn't exist

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

# Load daily data
daily_data, sha = load_daily_data()

# Streamlit Interface
st.title("🍏 Daily Nutrition Tracker")

# 📌 Select gender and activity level
gender = st.radio("Select your gender:", ["Male", "Female"])
activity_level = st.selectbox("Select your activity level:", 
                              ["Sedentary", "Moderately Active", "Very Active"])

# 📌 Select goal
goal = st.selectbox("What is your goal?", 
                    ["Weight Loss", "Muscle Gain", "Endurance Training", "Ketogenic Diet"])

# 📌 Display caloric range based on gender and activity level
calorie_target_range = calorie_ranges[gender][activity_level]
st.info(f"🔥 **Estimated daily caloric needs:** {calorie_target_range}")

# 📌 Input to add food item
food_item = st.text_input("Enter food name:")
quantity = st.number_input("Enter quantity in grams:", min_value=1, value=100)

if st.button("Add Food"):
    if food_item:
        food_item = food_item.lower()
        if food_item in daily_data:
            daily_data[food_item]["quantity"] += quantity
        else:
            daily_data[food_item] = {"quantity": quantity}

        update_daily_data(daily_data, sha)
        st.rerun()  # Refresh the UI after adding food
    else:
        st.error("⚠️ Please enter a valid food name.")

# 📊 Display daily food log with a remove button
st.header(f"📅 Daily Nutrition Data for {TODAY_DATE}")

if daily_data:
    for food, info in list(daily_data.items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{food.capitalize()}**: {info.get('quantity', 0)}g")  # ✅ FIX APPLIED
        with col2:
            if st.button(f"❌ Remove", key=food):
                del daily_data[food]
                update_daily_data(daily_data, sha)
                st.rerun()
else:
    st.info("No food recorded today.")
# 📊 Interactive Pie Chart of Macronutrient Distribution
st.header("📊 Macronutrient Distribution")

def compute_macronutrient_totals(daily_data):
    total_macros = {"Carbohydrates": 0, "Proteins": 0, "Fats": 0}
    for food, info in daily_data.items():
        macros = info.get("macronutrients", {"Carbohydrates": 0, "Proteins": 0, "Fats": 0})
        for macro, value in macros.items():
            total_macros[macro] += value * info["quantity"] / 100
    return total_macros

total_macronutrients = compute_macronutrient_totals(daily_data)

total_sum = sum(total_macronutrients.values())
if total_sum > 0:
    percentages = {macro: (value / total_sum) * 100 for macro, value in total_macronutrients.items()}
    fig, ax = plt.subplots()
    ax.pie(
        percentages.values(),
        labels=percentages.keys(),
        autopct='%1.1f%%',
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("No data available. Add food to see macronutrient distribution.")

# 📌 Compare macronutrient intake with target range based on goal
st.header(f"📈 Macronutrient Comparison for **{goal}**")

for macro, percent in total_macronutrients.items():  # 🔄 USARE total_macronutrients
    min_range, max_range = macronutrient_goals[goal][macro]
    percent = (percent / total_sum) * 100 if total_sum > 0 else 0  # Convert to percentage

    if percent < min_range:
        st.warning(f"⚠️ **{macro}** intake **{percent:.1f}%**: Too LOW compared to the target range **{min_range}-{max_range}%**.")
    elif percent > max_range:
        st.warning(f"⚠️ **{macro}** intake **{percent:.1f}%**: Too HIGH compared to the target range **{min_range}-{max_range}%**.")
    else:
        st.success(f"✅ **{macro}** intake **{percent:.1f}%**: **WITHIN** the target range **{min_range}-{max_range}%**.")


















