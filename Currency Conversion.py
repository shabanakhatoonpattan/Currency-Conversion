import streamlit as st
import requests
import pandas as pd
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI-Powered Predictive Currency Converter", page_icon="💱")
st.title("💹 Predictive Currency Converter (AI/ML)")

# --- Fetch supported currencies ---
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

# --- User Inputs ---
col1, col2 = st.columns(2)
from_currency = col1.selectbox("From Currency", currencies, index=currencies.index("USD") if "USD" in currencies else 0)
to_currency = col2.selectbox("To Currency", currencies, index=currencies.index("INR") if "INR" in currencies else 0)
amount = st.number_input("Amount", min_value=0.0, value=1.0, step=1.0)

future_date = st.date_input(
    "Predict for date", 
    min_value=datetime.date.today(),
    max_value=datetime.date.today() + datetime.timedelta(days=30),
    value=datetime.date.today()
)

# --- Fetch historical rates ---
@st.cache_data
def get_historical_rates(from_curr, to_curr, days=60):
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

# --- Predict future rate ---
def predict_rate(rates, future_date):
    rates = rates.reset_index()
    rates["day_num"] = (rates["index"] - rates["index"].min()).dt.days
    X = rates[["day_num"]].values
    y = rates[to_currency].values
    model = LinearRegression()
    model.fit(X, y)
    # Predict future
    future_day_num = (future_date - rates["index"].min().date()).days
    predicted_rate = model.predict(np.array([[future_day_num]]))[0]
    return predicted_rate, model

# --- Button ---
if st.button("Predict & Convert"):
    if amount > 0:
        rates = get_historical_rates(from_currency, to_currency)
        if rates is not None and not rates.empty:
            pred_rate, model = predict_rate(rates, future_date)
            converted_amount = amount * pred_rate
            st.success(f"Predicted rate on {future_date}: 1 {from_currency} = {pred_rate:.4f} {to_currency}")
            st.success(f"💰 {amount} {from_currency} ≈ {converted_amount:.2f} {to_currency} (predicted)")

            # Plot historical + predicted
            plt.figure(figsize=(10,4))
            plt.plot(rates.index, rates[to_currency], label="Historical Rate")
            future_dates = pd.date_range(rates.index.min(), future_date)
            future_days = np.array([(d.date() - rates.index.min().date()).days for d in future_dates]).reshape(-1,1)
            future_preds = model.predict(future_days)
            plt.plot(future_dates, future_preds, label="Predicted Trend", linestyle="--")
            plt.xlabel("Date")
            plt.ylabel(f"Rate ({from_currency} → {to_currency})")
            plt.legend()
            st.pyplot(plt)
        else:
            st.error("Failed to fetch historical data.")
    else:
        st.warning("Please enter amount > 0.")
