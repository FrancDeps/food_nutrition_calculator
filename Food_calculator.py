import streamlit as st
import requests
import json
import base64
import matplotlib.pyplot as plt
from datetime import datetime

# Function to calculate macronutrient distribution
def calculate_macros(food_data):
    """Simulated function to calculate macronutrients. Replace this with real food database."""
    macros = {"Carbohydrates": 0, "Proteins": 0, "Fats": 0}
    
    # Dummy values per 100g (Replace this with real data from a food database)
    food_macros = {
        "chicken": {"Carbohydrates": 0, "Proteins": 31, "Fats": 3},
        "rice": {"Carbohydrates": 28, "Proteins": 2.7, "Fats": 0.3},
        "salmon": {"Carbohydrates": 0, "Proteins": 20, "Fats": 13},
        "avocado": {"Carbohydrates": 9, "Proteins": 2, "Fats": 15}
    }

    for food, details in food_data.items():
        quantity = details["quantity"] / 100  # Convert to per 100g
        if food in food_macros:
            for macro in macros:
                macros[macro] += food_macros[food][macro] * quantity

    return macros

# Load daily data
daily_data, sha = load_daily_data()

# Calculate macronutrient intake
macronutrient_consumed = calculate_macros(daily_data)

# 📊 Pie Chart of Macronutrient Distribution
st.header("📊 Macronutrient Distribution")

if sum(macronutrient_consumed.values()) > 0:
    fig, ax = plt.subplots()
    ax.pie(macronutrient_consumed.values(), labels=macronutrient_consumed.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("No food data available for macronutrient calculation.")

