# --- Imports ---
# Env
from dotenv import load_dotenv
load_dotenv()

# Core
import polars as pl

# API Functions
import API_Functions

# --- Pandas - ETL - JSON Conversion ---
def transform_json_to_dataframe(symbol: str = "AAPL",
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
        The transformed stock data in a Polars DataFrame format
    """
    json_data = API_Functions.retrieve_aggregate_data_for_stock(symbol, timespan, timespan_multiplier, from_date, to_date, adjusted, sort_order, limit)
    
    # Conversion to Polars DataFrame for learning reasons
    pl_dataframe_data = pl.DataFrame(json_data[f"results"], schema={"t":pl.Int64,
                                     "o":pl.Float32,
                                     "h":pl.Float32,
                                     "l":pl.Float32,
                                     "c":pl.Float32,
                                     "n":pl.Int32,
                                     "v":pl.Int32,
                                     "vw":pl.Int32}) \
                            .select([pl.lit(symbol).alias("stock_code"),
                                     pl.from_epoch(pl.col("t"), time_unit="ms").alias("timestamp"),
                                     pl.col("o").alias("open"),
                                     pl.col("h").alias("high"),
                                     pl.col("l").alias("low"),
                                     pl.col("c").alias("close"),
                                     pl.col("v").alias("trading_volume"),
                                     pl.col("n").alias("number_of_transactions_in_aggregate_window"),
                                     pl.col("vw").alias("volume_weighted_average_price")])
                                     

    print(pl_dataframe_data)
    return pl_dataframe_data