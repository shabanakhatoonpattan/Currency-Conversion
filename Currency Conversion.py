import streamlit as st
import requests
import pandas as pd
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="AI-Powered Currency Converter", page_icon="💱")
st.title("💹 Predictive Currency Converter (AI/ML)")

# ---- Fetch supported currencies ----
@st.cache_data
def get_supported_currencies():
    url = "https://api.frankfurter.app/currencies"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data:
            return list(data.keys())
        else:
            return ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"]
    except:
        return ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"]

currencies = get_supported_currencies()

# ---- User Inputs ----
col1, col2 = st.columns(2)
from_currency = col1.selectbox("From Currency", currencies, index=currencies.index("USD") if "USD" in currencies else 0)
to_currency = col2.selectbox("To Currency", currencies, index=currencies.index("INR") if "INR" in currencies else 0)
amount = st.number_input("Amount", min_value=0.0, value=1.0, step=1.0)

future_date = st.date_input(
    "Predict for date (optional)",
    min_value=datetime.date.today(),
    max_value=datetime.date.today() + datetime.timedelta(days=30),
    value=datetime.date.today()
)

# ---- Functions ----
def get_current_rate(from_curr, to_curr):
    """Get current exchange rate from Frankfurter API"""
    url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        rate = data["rates"][to_curr]
        return rate
    except:
        return None

@st.cache_data
def get_historical_rates(from_curr, to_curr, days=60):
    """Get historical rates for prediction"""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)
    url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={from_curr}&to={to_curr}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        rates = pd.DataFrame.from_dict(data["rates"], orient="index")
        rates.index = pd.to_datetime(rates.index)
        rates = rates.sort_index()
        return rates
    except:
        return None

def predict_rate(rates, future_date):
    rates = rates.reset_index()
    rates["day_num"] = (rates["index"] - rates["index"].min()).dt.days
    X = rates[["day_num"]].values
    y = rates[to_currency].values
    model = LinearRegression()
    model.fit(X, y)
    future_day_num = (future_date - rates["index"].min().date()).days
    predicted_rate = model.predict(np.array([[future_day_num]]))[0]
    return predicted_rate

# ---- Button Action ----
if st.button("Convert / Predict"):
    if amount <= 0:
        st.warning("Please enter an amount greater than 0.")
    else:
        # Step 1: Show current rate
        current_rate = get_current_rate(from_currency, to_currency)
        if current_rate:
            current_amount = amount * current_rate
            st.success(f"💰 Current rate: 1 {from_currency} = {current_rate:.4f} {to_currency}")
            st.success(f"💰 {amount} {from_currency} ≈ {current_amount:.2f} {to_currency} (current)")
        else:
            st.error("Failed to fetch current rate.")
        
        # Step 2: Predict future if date is not today
        if future_date > datetime.date.today():
            historical_rates = get_historical_rates(from_currency, to_currency)
            if historical_rates is not None and not historical_rates.empty:
                predicted_rate = predict_rate(historical_rates, future_date)
                predicted_amount = amount * predicted_rate
                st.info(f"🔮 Predicted rate on {future_date}: 1 {from_currency} ≈ {predicted_rate:.4f} {to_currency}")
                st.info(f"💰 {amount} {from_currency} ≈ {predicted_amount:.2f} {to_currency} (predicted)")
            else:
                st.warning("Unable to fetch historical data for prediction.")
