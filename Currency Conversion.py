import streamlit as st
import requests

st.set_page_config(page_title="💱 Real-Time Currency Converter", layout="centered")
st.title("💱 Real-Time Currency Converter")

# List of valid currency codes
CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "SGD", "CHF", "CNY"]

@st.cache_data(ttl=600)
def get_exchange_rates(base_currency="USD"):
    """Fetch live exchange rates for a given base currency."""
    url = f"https://api.exchangerate.host/latest?base={base_currency}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "rates" not in data:
            raise ValueError("Rates not found in response.")
        return data
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# --- UI inputs
col1, col2, col3 = st.columns(3)
with col1:
    from_currency = st.selectbox("From Currency", CURRENCIES, index=0)
with col2:
    to_currency = st.selectbox("To Currency", CURRENCIES, index=3)
with col3:
    amount = st.number_input("Amount to Convert:", min_value=0.0, value=1.0, step=0.1, format="%.2f")

if st.button("Convert"):
    data = get_exchange_rates(from_currency)
    if not data:
        st.error("Unable to fetch exchange rates. Please try again later.")
    else:
        rates = data["rates"]
        if to_currency in rates:
            rate = rates[to_currency]
            converted = amount * rate
            st.success(f"{amount:.2f} {from_currency} = {converted:.2f} {to_currency}")
            st.caption(f"Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
        else:
            st.error(f"Currency '{to_currency}' not available in API response.")
