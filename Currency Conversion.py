import streamlit as st
import requests

st.set_page_config(page_title="Realtime Currency Converter", page_icon="💱")

st.title("💱 Realtime Currency Converter")

# ---- Function to get supported currencies ----
@st.cache_data
def get_supported_currencies():
    url = "https://api.exchangerate.host/latest"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("rates"):
            return list(data["rates"].keys())
        else:
            st.warning("⚠️ Unable to fetch currency list, using fallback set.")
            return ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"]
    except Exception as e:
        st.error(f"Error fetching currency list: {e}")
        return ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"]

# ---- Function to get exchange rate ----
def convert_currency(amount, from_currency, to_currency):
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("result") is not None:
            return data["result"]
        else:
            st.error("API error: Rates not found in response.")
            return None
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None

# ---- UI ----
currencies = get_supported_currencies()

col1, col2 = st.columns(2)
from_currency = col1.selectbox("From Currency", currencies, index=currencies.index("USD") if "USD" in currencies else 0)
to_currency = col2.selectbox("To Currency", currencies, index=currencies.index("INR") if "INR" in currencies else 0)
amount = st.number_input("Enter Amount", min_value=0.0, step=1.0)

if st.button("Convert"):
    if amount > 0:
        result = convert_currency(amount, from_currency, to_currency)
        if result is not None:
            st.success(f"💰 {amount} {from_currency} = {result:.2f} {to_currency}")
    else:
        st.warning("Please enter an amount greater than 0.")
