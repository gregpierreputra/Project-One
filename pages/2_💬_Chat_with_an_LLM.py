# --- Imports ---
# Core
import streamlit as st

# Langchain
from langchain_core.messages import AIMessage, HumanMessage

# Functions
import Transformation_Functions, API_Functions

# --- Session States ---
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = 0

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! I am a helpful chatbot here to answer any questions related to stocks. Keep in mind that this is not financial advice, and please do your own personal research before making any financial decisions.")
    ]

# --- Streamlit - Frontend - Configs ---
st.set_page_config(page_title="Chat with Mistral",
                   page_icon="💬")
st.title("💬 Chat with Mistral")
st.markdown("""
            Ask the infamous LLM a range of questions related to your queried stock data.
            Keep in mind that you should load the data through the sidebar on the left.
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
                    data_call, mean_open, standard_deviation_open, mean_close, standard_deviation_close = Transformation_Functions.transform_json_to_dataframe(
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
# --- Stock dataframe loaded/not loaded check ---
if "Stock_Dataframe" not in st.session_state:
    st.markdown("**Stock data has not been loaded.**\n\n**Please load the stock data through the sidebar on the left.**")
else:
    st.markdown("**Successfully retrieved the stock data**, feel free to start asking questions!")

    # --- Chat with LLM ---
    # Message display based on whether the message is from the user or from the LLM
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    # Chat input initialization
    user_message = st.chat_input(placeholder="Ask a question!",
                                key="User_Chat_Message")

    # Chat handling with the session history, and calls to the query_llm_with_question function
    if user_message is not None and user_message.strip() != "":
        st.session_state.chat_history.append(HumanMessage(content=user_message))

        with st.chat_message("Human"):
            st.markdown(user_message)

        with st.chat_message("AI"):
            response_init = API_Functions.query_llm_with_question()
            response = response_init.invoke(input={"dataframe":st.session_state["Stock_Dataframe"],
                                                "conversation_history":st.session_state.chat_history,
                                                "user_question":user_message})
            st.markdown(response)
        st.session_state.chat_history.append(AIMessage(content=response))