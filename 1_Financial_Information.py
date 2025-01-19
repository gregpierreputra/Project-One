# --- Imports ---
# Core
import os
import streamlit as st
import polars as pl

# Functions
import Transformation_Functions, API_Functions

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
                        st.error("You have entered stock data that does not exist. **Please enter a ticker symbol for stocks traded in the US, with a realistic set of settings.**\n\n**Also please refer to the question mark symbols for example data that can be entered.**")

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
    st.markdown(f"### 📊 Chart")
    st.markdown("The open, high, low, and close (OHLC) data for the specified stock in a **candlestick chart**. You can zoom in on specific periods, and hover to see the data in detail.")
    st.plotly_chart(figure_or_data=Transformation_Functions.candlestick_plotly_graph(st.session_state["Stock_Dataframe"]),
                    theme="streamlit",
                    key="Stock_Candlestick_Chart")
    st.markdown("***")

    # --- Table ---
    st.markdown(f"### 📋 Table")
    st.markdown("""
                Here is a list of the most relevant information for the stock that you queried. The information here cover OHLC data, trading volume, number of transactions in the aggregated window, and volume weighted average price.
                
                **Technical indicators** are also included in this data, and they have the "ti_" prefix attached to them. The list of technical indicators are
                - *Returns* over a given time period based on the *close* column
                - *Volatility* over 5 time periods based on the *returns* column
                - *Simple moving average* over 20 time periods based on the *close* column
                """)
    st.dataframe(st.session_state["Stock_Dataframe"])
    st.markdown("***")

    # --- News ---
    st.markdown(f"### 📰 News")
    st.markdown("Here are some of the most interesting, and recent news articles in descending order using the end date related to the stock that you queried.")
    stock_news_dataframe = Transformation_Functions.transform_ticker_news_json_to_dataframe(symbol=stock_symbol_input,
                                                                                            from_date=start_date_input,
                                                                                            to_date=end_date_input)
    for article in range(len(stock_news_dataframe)):
        with st.container(border=True):
            st.markdown(f"**[{stock_news_dataframe.item(article, "title")}]({stock_news_dataframe.item(article, "article_url")})**")
            st.markdown(f"*Published by **{stock_news_dataframe.item(article, "author")}** on {stock_news_dataframe.item(article, "published_utc")}*")
            st.image(image=f"{stock_news_dataframe.item(article, "image_url")}",width=300)
            st.markdown(f"{stock_news_dataframe.item(article, "description")}")
    st.markdown("***")