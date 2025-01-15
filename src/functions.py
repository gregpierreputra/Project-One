# --- Imports ---
# Env
from dotenv import load_dotenv
load_dotenv()

# Core
import os
import requests

# --- Test Retrieval Function ---
def test_retrieval_from_alpha_vantage(function: str = "TIME_SERIES_INTRADAY",
                                      symbol: str = "IBM",
                                      interval: str = "1min"):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    url_generator = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}"
    data_request = requests.get(url_generator)
    data = data_request.json()

    print(f"Attempting to print the JSON retrieved through the AlphaVantage API")
    print(data)
    return data
