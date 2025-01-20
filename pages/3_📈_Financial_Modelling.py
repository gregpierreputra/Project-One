# --- Imports ---
# Core
import os
import streamlit as st

# Functions
import Transformation_Functions, Backtrading_Functions

# --- Session States ---
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = 0

# --- Streamlit - Frontend - Configs ---
st.set_page_config(page_title="Financial Modelling with Stock Data",
                   page_icon="📈")
st.title("📈 Financial Modelling")
st.markdown("""
            **This page is currently under construction** and will host the financial modelling functionality within it.
            It will allow you to **utilize machine learning models** to predict a certain column's value at the next time period based on a selection of columns used as features. 
            """)

# --- Streamlit - Frontend - Sidebar
with st.sidebar:

    # --- Streamlit - Frontend - Data Loading Container ---
    with st.container():
        st.subheader("Stock Data Settings")
        with st.form(key="Stock_Data_Pull_Form"):
            stock_symbol_input = str(st.text_input("Stock Symbol", key="Symbol", placeholder="AAPL", max_chars=4, help="The ticker symbol for the stock. Enter a ticker symbol, e.g., AAPL for Apple, or AMZN for Amazon")).upper()
            timespan_input = st.text_input("Timespan", key="Timespan", placeholder="day", max_chars=7, help="The size of the time window. Enter values such as: second, minute, hour, day, week, month, quarter, year")
            timespan_multiplier_input = st.text_input("Timespan Multiplier", placeholder="1", key="Timespan_Multiplier", max_chars=2, help="The size of the timespan multier. If set to 5 and timespan to hours, then 5-hour bars will be returned.Enter a value between 1 and 99, e.g., 10")
            start_date_input = st.text_input("Start Date", key="Start_Date", placeholder="2024-01-01", max_chars=10, help="Start of the aggregate time window. Enter a date in YYYY-MM-DD format, e.g., 2024-01-01")
            end_date_input = st.text_input("End Date", key="End_Date", placeholder="2024-12-31", max_chars=10, help="End of the aggregate time window. Enter a date in YYYY-MM-DD format, e.g., 2024-12-31")

            submitted_stock_data_form = st.form_submit_button(label="Connect to the API")

            if submitted_stock_data_form:
                with st.spinner("Attempting a connection to retrieve the data..."):
                    try:
                        data_call = Transformation_Functions.transform_aggregate_stock_json_to_dataframe(
                            symbol=stock_symbol_input,
                            timespan=timespan_input,
                            timespan_multiplier=timespan_multiplier_input,
                            from_date=start_date_input,
                            to_date=end_date_input)
                        
                        st.session_state["Stock_Dataframe"] = data_call
                        st.session_state.data_loaded = 1
                    except KeyError as StockDataCallError:
                        st.error("**You have entered stock data that does not exist**. Please enter a ticker symbol for stocks traded in the US, with a realistic set of settings.\n\nAlso please refer to the question mark symbols for example data that can be entered.")

        if st.session_state.data_loaded == 1:
            st.success("Stock data has been loaded!")
        else:
            st.error("Data has not been loaded...")


# --- Key Functionalities ---
if "Stock_Dataframe" not in st.session_state:
    st.markdown("**Stock data has not been loaded.**\n\n**Please load the stock data through the sidebar on the left.**")
else:
    # --- Chart ---
    st.markdown("**Successfully retrieved the stock data!**")
    st.markdown("However, the functionality for this page is still not available yet. Apologies.")

    # --- Benchmark - Buy and Sell Strategy ---
    # TODO: Complete the backtrading functionality in the Backtrading_Functions.py file
    # st.markdown("### Benchmark - Buy and Hold Strategy")
    # st.markdown("""
    #             The benchmark for any trading strategy will be buy and hold, where we buy the stock at the earliest possible time period with all our capital, and simply hold the stock in our portfolio.
    #             By backtrading with this trading strategy, we can see how much returns would have been generated if implemented on the queried stock.
    #             """)
    # test_call = Backtrading_Functions.buy_and_hold_stock_trader_init(stock_dataframe=st.session_state["Stock_Dataframe"])