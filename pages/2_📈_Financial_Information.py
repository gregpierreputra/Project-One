# --- Imports ---
# Env
from dotenv import load_dotenv
load_dotenv()

# Core
import streamlit as st

# Functions
import Transform_Functions

# --- Session States ---
st.session_state.data_loaded = 0
st.session_state.data_connection_completed = 0
st.session_state.chat_history = [
    "Testing Purposes"
]

# --- Streamlit - Frontend - Configs ---
st.set_page_config(page_title="Financial Information",
                   page_icon="📈")
st.title("Financial Information")


# --- Streamlit - Frontend - Sidebar
with st.sidebar:

    # --- Streamlit - Frontend - Data Loading Container ---
    with st.container():
        st.subheader("Stock Data Settings")
        st.text_input("Stock Symbol", key="Symbol", value="AAPL", max_chars=4, help="The ticker symbol for the stock")
        st.text_input("Timespan", key="Timespan", value="hour", help="The size of the time window. Possible values are: second, minute, hour, day, week, month, quarter, year")
        st.text_input("Timespan Multiplier", key="Timespan_Multiplier", value="5", max_chars=2, help="The size of the timespan multier. If set to 5 and timespan to hours, then 5-hour bars will be returned")
        st.text_input("Start Date", key="Start_Date", value="2024-01-01", max_chars=10, help="Start of the aggregate time window")
        st.text_input("End Date", key="End_Date", value="2024-12-31", max_chars=10, help="End of the aggregate time window")
        
        if st.button("Connect to the API"):
            with st.spinner("Attempting a connection to retrieve the data..."):
                data_call = Transform_Functions.transform_json_to_dataframe(
                    symbol=st.session_state["Symbol"],
                    timespan=st.session_state["Timespan"],
                    timespan_multiplier=st.session_state["Timespan_Multiplier"],
                    from_date=st.session_state["Start_Date"],
                    to_date=st.session_state["End_Date"])
                
                st.session_state["Stock_Dataframe"] = data_call
                st.session_state.data_loaded = 1

        if st.session_state.data_loaded == 1:
            st.success("Stock data has been loaded!")
        else:
            st.error("Data has not been loaded...")
        
# --- Key Functionalities ---
st.markdown("This is the financial information page!")
