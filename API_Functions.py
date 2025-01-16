# --- Imports ---
# Env
from dotenv import load_dotenv
load_dotenv()

# Core
import os
import requests

# --- AlphaVantage - API - Function Data Retrieval ---
def retrieve_aggregate_data_for_stock(symbol: str,
                                      timespan: str,
                                      timespan_multiplier: str,
                                      from_date: str,
                                      to_date: str,
                                      adjusted: str,
                                      sort_order: str,
                                      limit: str):
    """
    Calls the Polygon Aggregate (Bars) API to retrieve aggregated bars for a user-specified stock based on a set of user-specified settings.

    Args:
        stock: The ticker symbol of the stock to download
        timespan: The size of the aggregate time window, e.g., day, minute, quarter, year
        timespan_multiplier: The size of the aggregate timespan multiplier, e.g., a value of 3 and day denotes an aggreggate timespan of 3 days
        from_date: The start date for the stock data that will be retrieved
        to_date: The end date for the stock data that will be retrieved
        adjusted: Setting for whether the stock data will be adjusted for splits
        sort_order: The sorting order for the stock data will be retrieved can be ascending or descending based on time
        limit: The total amount (in rows) of data before aggregation that the data will be limited to

    Returns:
        The stock data in JSON format with the data being stored within a value called "results"
        Metadata and status code is also sent as part of the API call
    """
    api_key = os.getenv("POLYGON_API_KEY")

    # Call the Polygon Aggregate Data API to retrieve the data
    # Default to pre-defined if not selected by the user
    url_generator = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{timespan_multiplier}/{timespan}/{from_date}/{to_date}?adjusted={adjusted}&sort={sort_order}&limit={limit}&apiKey={api_key}"
    data_request = requests.get(url_generator)
    data = data_request.json()

    return data