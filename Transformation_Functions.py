# --- Imports ---
# Env
from dotenv import load_dotenv
load_dotenv()

# Core
import polars as pl
import plotly.graph_objects as go

# API Functions
import API_Functions

# --- Pandas - ETL - JSON Conversion for Polygon Aggregate Bars API Data ---
def transform_aggregate_stock_json_to_dataframe(symbol: str = "AAPL",
                                                timespan: str = "day",
                                                timespan_multiplier: str = "1",
                                                from_date: str = "2024-01-01",
                                                to_date: str = "2024-12-31",
                                                adjusted: str = "true",
                                                sort_order: str = "desc",
                                                limit: str = "10000") -> pl.DataFrame:
    """
    Retrieves the stock data from the retrieve_aggregate_data_for_stock of the API_Functions.py file

    Performs several transformation tasks:
        - Datatype conversions for the base columns from the API
        - Conversion of the timestamp column from unix to readable datetime
        - Renaming of the base columns from the API to a readable format
        - New column containing the literal value of the user-specified stock ticker symbol

    Returns various details as the session state is not saved between page changes and one way for persistence is through the st.markdown() function

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
        mean_open: The mean value of the "open" column
        standard_deviation_open: The standard deviation value of the "open" column
        mean_close: The mean value of the "close" column
        standard_deviation_close: The standard deviation value of the "close" column
        pl_dataframe_data: The transformed stock data in a Polars DataFrame format
    """
    json_data = API_Functions.retrieve_aggregate_data_for_stock(symbol, timespan, timespan_multiplier, from_date, to_date, adjusted, sort_order, limit)
    
    # Conversion to Polars DataFrame for learning reasons
    pl_dataframe_data = pl.DataFrame(json_data[f"results"], schema={"t":pl.UInt64,
                                     "o":pl.Float64,
                                     "h":pl.Float64,
                                     "l":pl.Float64,
                                     "c":pl.Float64,
                                     "n":pl.Int64,
                                     "v":pl.UInt64,
                                     "vw":pl.UInt64}) \
                            .select([pl.lit(symbol).alias("stock_code"),
                                     pl.from_epoch(pl.col("t"), time_unit="ms").alias("timestamp"),
                                     pl.col("o").alias("open"),
                                     pl.col("h").alias("high"),
                                     pl.col("l").alias("low"),
                                     pl.col("c").alias("close"),
                                     pl.col("v").alias("trading_volume"),
                                     pl.col("n").alias("number_of_transactions_in_aggregate_window"),
                                     pl.col("vw").alias("volume_weighted_average_price")])
    
    # Create statistical aggregation for all columns 
    mean_pl_dataframe_data = pl_dataframe_data.mean()
    standard_deviation_pl_dataframe_data = pl_dataframe_data.std()
    
    # Extract column values with statistical significance
    # TODO: Resolve the persistence error with session_state. Have to reload the API call to load this call. Think of a solution.
    mean_open = mean_pl_dataframe_data.item(0, "open")
    standard_deviation_open = standard_deviation_pl_dataframe_data.item(0, "open")

    mean_close = mean_pl_dataframe_data.item(0, "close")
    standard_deviation_close = standard_deviation_pl_dataframe_data.item(0, "close")

    return pl_dataframe_data, mean_open, standard_deviation_open, mean_close, standard_deviation_close

# --- Pandas - ETL - JSON Conversion for Polygon Ticker News API Data ---
def transform_ticker_news_json_to_dataframe(symbol: str,
                                            from_date: str,
                                            to_date: str) -> pl.DataFrame:
    """
    Retrieves the ticker news data from the retrieve_news_for_stock of the API_Functions.py file

    Performs several transformation tasks:
        - Retrieving of key information from the results JSON object

    As of now, details that are pulled and utilized are:
        - title
        - article_url
        - author
        - published_utc
        - image_url
        - description

    Args:
        symbol: The ticker symbol of the stock news articles that will be retrieved
        from_date: The start date for the stock news articles that will be retrieved. Date entered here is inclusive.
        to_date: The end date for the stock news articles that will be retrieved. Date entered here is inclusive.

    Returns:
        The information from the JSON object transformed into a Polars DataFrame object
    """
    json_data = API_Functions.retrieve_news_for_stock(symbol=symbol,
                                                      from_date=from_date,
                                                      to_date=to_date)
    
    # Conversion from JSON API Data to a Polars Dataframe for easier processing in frontend
    # TODO: Extract the insights objects inside the Ticker News API. Nested JSON object structure from the API call.
    pl_dataframe_data = pl.DataFrame(json_data[f"results"])

    return pl_dataframe_data

def ohlc_plotly_graph(dataframe: pl.DataFrame) -> go.Figure:
    """
    Create an open, high, low, and close (OHLC) graph figure using the Plotly library and the dataframe input argument.
    Also create the hovertext that will be attached to each datapoint in the figure.

    Args:
        dataframe: A polars dataframe containing the date, open, high, low, and close data
    Returns:
        An OHLC figure in Plotly Graph Object format
    """
    # Text creation when hovering over individual datapoints in the graph
    hovertext = []
    for i in range(len(dataframe["timestamp"])):
        hovertext.append(
            f"Open: {str(round(dataframe["open"][i], 2))}" +
            f"<br>High: {str(round(dataframe["high"][i], 2))}" +
            f"<br>Low: {str(round(dataframe["low"][i], 2))}" + 
            f"<br>Close: {str(round(dataframe["close"][i], 2))}")
        
    # OHLC graph figure initialization using the dataframe from the input
    ohlc_graph_figure = go.Figure(data=go.Ohlc(
        x=dataframe["timestamp"],
        open=dataframe["open"],
        high=dataframe["high"],
        low=dataframe["low"],
        close=dataframe["close"],
        text=hovertext,
        hoverinfo="text"))

    return ohlc_graph_figure