# --- Imports ---
# Env
import os
from dotenv import load_dotenv
load_dotenv()

# Core
import streamlit as st

# Functions
import Transform_Functions, API_Functions

# --- Session States ---
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = 0

# --- Streamlit - Frontend - Configs ---
st.set_page_config(page_title="Project Stonks",
                   page_icon="💰")
st.title("💰 Project Stonks")
st.markdown("""
            Yet another project focused on stocks.
            Primarily created to learn new technologies and their possible interactions.
            """)

# --- Streamlit - Frontend - Sidebar
with st.sidebar:

    # --- Streamlit - Frontend - Data Loading Container ---
    with st.container():
        st.subheader("Stock Data Settings")
        with st.form(key="Stock_Data_Pull_Form"):
            stock_symbol_input = st.text_input("Stock Symbol", key="Symbol", max_chars=4, help="The ticker symbol for the stock. Enter a ticker symbol, e.g., AAPL for Apple, or AMZN for Amazon")
            timespan_input = st.text_input("Timespan", key="Timespan", max_chars=7, help="The size of the time window. Enter values such as: second, minute, hour, day, week, month, quarter, year")
            timespan_multiplier_input = st.text_input("Timespan Multiplier", key="Timespan_Multiplier", max_chars=2, help="The size of the timespan multier. If set to 5 and timespan to hours, then 5-hour bars will be returned.Enter a value between 1 and 99, e.g., 10")
            start_date_input = st.text_input("Start Date", key="Start_Date", max_chars=10, help="Start of the aggregate time window. Enter a date in YYYY-MM-DD format, e.g., 2024-01-01")
            end_date_input = st.text_input("End Date", key="End_Date", max_chars=10, help="End of the aggregate time window. Enter a date in YYYY-MM-DD format, e.g., 2024-12-31")

            submitted_stock_data_form = st.form_submit_button(label="Connect to the API")

            if submitted_stock_data_form:
                with st.spinner("Attempting a connection to retrieve the data..."):
                    data_call, mean_open, standard_deviation_open, mean_close, standard_deviation_close = Transform_Functions.transform_json_to_dataframe(
                        symbol=stock_symbol_input,
                        timespan=timespan_input,
                        timespan_multiplier=timespan_multiplier_input,
                        from_date=start_date_input,
                        to_date=end_date_input)
                    
                    st.session_state["Stock_Dataframe"] = data_call
                    st.session_state.data_loaded = 1

        if st.session_state.data_loaded == 1:
            st.success("Stock data has been loaded!")
        else:
            st.error("Data has not been loaded...")


# --- Key Functionalities ---
if "Stock_Dataframe" not in st.session_state:
    st.markdown("**Stock data has not been loaded yet...**")
else:

    st.markdown("**Successfully retrieved the stock data!**")
    st.markdown("**Queried the data for Stock: {}, Start-Date: {}, End-Date: {}**"
                .format(stock_symbol_input, start_date_input, end_date_input))
    st.markdown(f"### 📊 Chart")
    st.markdown("The open, high, low, and close (OHLC) data for the specified stock. You can zoom in on specific periods, and hover to see the data in detail.")
    st.plotly_chart(figure_or_data=Transform_Functions.ohlc_plotly_graph(st.session_state["Stock_Dataframe"]),
                    theme="streamlit",
                    key="Stock_OHLC_Chart")

    st.markdown(f"### 📋 Table")
    st.markdown("The full list of information for the specified stock")
    st.dataframe(st.session_state["Stock_Dataframe"])

    st.markdown(f"### 📰 News and Market Sentiment")
    st.markdown("All related news and the current market sentiment related to the stock")