import streamlit as st
import requests

st.set_page_config(page_title="💱 Real-Time Currency Converter", layout="centered")
st.title("💱 Real-Time Currency Converter")

# Fetch supported symbols from the API (only once)
@st.cache_data(ttl=3600)
def get_supported_currencies():
    url = "https://api.exchangerate.host/symbols"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    return list(data["symbols"].keys())

# Fetch live rates for a given base
@st.cache_data(ttl=600)
def get_exchange_rates(base_currency="USD"):
    url = f"https://api.exchangerate.host/latest?base={base_currency}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "rates" not in data:
        raise ValueError("Rates not found in response.")
    return data

# --- UI Inputs ---
currencies = get_supported_currencies()
col1, col2, col3 = st.columns(3)

with col1:
    from_currency = st.selectbox("From Currency", currencies, index=currencies.index("USD"))
with col2:
    to_currency = st.selectbox("To Currency", currencies, index=currencies.index("INR"))
with col3:
    amount = st.number_input("Amount to Convert", min_value=0.0, value=1.0, step=0.1)

if st.button("Convert"):
    try:
        data = get_exchange_rates(from_currency)
        rate = data["rates"].get(to_currency)
        if not rate:
            st.error(f"Currency '{to_currency}' not found in rates data.")
        else:
            result = amount * rate
            st.success(f"{amount:.2f} {from_currency} = {result:.2f} {to_currency}")
            st.caption(f"Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
