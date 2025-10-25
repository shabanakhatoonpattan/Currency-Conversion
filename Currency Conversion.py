import streamlit as st
import requests

# -------------------------------
# Title and setup
# -------------------------------
st.set_page_config(page_title="💱 Real-Time Currency Converter", layout="centered")
st.title("💱 Real-Time Currency Converter")

st.markdown("""
This simple app converts one currency to another using live exchange rates.
Data source: [exchangerate.host](https://exchangerate.host/)
""")

# -------------------------------
# Function to fetch exchange rates
# -------------------------------
@st.cache_data(ttl=600)
def get_exchange_rates(base_currency="USD"):
    """Fetch live exchange rates for a given base currency."""
    url = f"https://api.exchangerate.host/latest?base={base_currency}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to fetch exchange rates. Please try again later.")
        return None
    return response.json()

# -------------------------------
# User Inputs
# -------------------------------
st.header("Enter Details:")

col1, col2, col3 = st.columns(3)
with col1:
    from_currency = st.text_input("From Currency (e.g. USD, INR, EUR):", value="USD").upper()
with col2:
    to_currency = st.text_input("To Currency (e.g. INR, EUR, GBP):", value="INR").upper()
with col3:
    amount = st.number_input("Amount to Convert:", min_value=0.0, value=1.0, step=0.1, format="%.2f")

# -------------------------------
# Conversion Logic
# -------------------------------
if st.button("Convert"):
    with st.spinner("Fetching live rates..."):
        data = get_exchange_rates(from_currency)
        if data and "rates" in data:
            rates = data["rates"]
            if to_currency in rates:
                rate = rates[to_currency]
                converted_amount = amount * rate
                st.success(f"✅ {amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}")
                st.caption(f"Exchange rate: 1 {from_currency} = {rate:.4f} {to_currency}")
            else:
                st.error(f"Currency '{to_currency}' not found in rates data.")
        else:
            st.error("Unable to fetch exchange rates. Please check the currency code.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("💡 *Built with Streamlit and exchangerate.host — by Shabana*")
