# --- Imports ---
# Env
from dotenv import load_dotenv
load_dotenv()

# Core
import pandas as pd
import numpy as np
import streamlit as st

# Functions
import functions

# --- Session States ---
st.session_state.data_loaded = 0
st.session_state.data_connection_completed = 0
st.session_state.chat_history = [
    "Testing Purposes"
]

# --- Streamlit - Frontend - Configs ---
st.set_page_config(page_title="Project One")
st.title("Project One")


# --- Streamlit - Frontend - Sidebar
with st.sidebar:

    # --- Streamlit - Frontend - Data Loading Container ---
    with st.container(height=200):
        st.subheader("Data")
        if st.session_state.data_loaded == 1:
            st.success("Data has been loaded!")
        else:
            st.error("Data has not been loaded...")

        if st.button("Connect to the API and retrieve the data"):
            with st.spinner("Attempting a connection to retrieve the data..."):
                st.session_state.data_loaded = 1

    # --- Streamlit - Frontend - Features Container ---
    with st.container(height=200):
        st.subheader("Feature")
        
# --- Key Functionalities ---
test_call = functions.test_retrieval_from_alpha_vantage()
st.json(test_call)
