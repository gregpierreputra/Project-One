# --- Imports ---
# Core
import polars as pl
import numpy as np

# --- Polars - Technical Indicator (TI) - Variable volatility period based on user-specified settings ---
def ti_daily_return_and_volatility(stock_dataframe: pl.DataFrame,
                                   time_period: int = 5) -> pl.DataFrame:
    """
    Volatility
    A statistical measure of the dispersion of returns for a given security or market index
    In this case, we create a daily return through percentage change using the "close" column, and calculate the volatility over a user-specified amount of time periods using the standard deviation method 

    Based on https://www.investopedia.com/terms/v/volatility.asp
    "Represents how greatly an asset's prices swing around the mean price"
    "Volatile assets are often considered riskier than less volatile assets because the price is expected to be less predictable"

    where:
    Volatility = A * (sqrt)T
    where:
    A  : Standard deviation of daily returns
    T  : Number of periods in the time horizon

    Args:
        stock_dataframe: A Polars dataframe containing the OHLC data and sorted in ascending order for the column timestamp
        time_period: An integer holding the time period value that we will use to calculate the volatility over
    Returns:
        A two column Polars DataFrame in both Float32 dtype based on the percentage change over one time period, and the volatility of the stock based on the "close" column over a user-specified time period
    """
    daily_return = pl.Series(name=f"ti_returns",
                             values=stock_dataframe["close"].pct_change(n=1),
                             dtype=pl.Float32,
                             nan_to_null=True).to_frame()
    
    volatility = pl.Series(name=f"ti_volatility_over_{time_period}_period",
                           values=(stock_dataframe["close"].rolling_std(window_size=time_period) * np.sqrt(time_period)),
                           dtype=pl.Float32,
                           nan_to_null=True).to_frame()
    
    daily_return_volatility_final_output = pl.concat([daily_return, volatility],
                                                     how="horizontal")

    return daily_return_volatility_final_output

# --- Polars - Technical Indicator (TI) - Variable simple moving average based on user-specified settings ---
def ti_variable_day_simple_moving_average(stock_dataframe: pl.DataFrame,
                                          time_period: int = 5,
                                          column_name: str = "close") -> pl.DataFrame: 
    """
    Simple Moving Average (SMA)
    A simple technical analysis tool
    Used to identify the trend direction of a stock or to determine its support and resistance levels
    Applies an equal weight to all observation in the period

    Based on https://www.investopedia.com/terms/m/movingaverage.asp
    "The 50-day and 200-day moving average figures for stocks are widely followed by investors and traders and are considered to be important trading signals"
    "The shorter the timespan used to create the average, the more sensitive it will be to price changes. The longer the time span, the less sensitive the average will be."

    where:
    SM(A) = (A1 + A2 + ... + An) / n
    where:
    A  : Average in period n
    n  : Number of time periods

    Args:
        stock_dataframe: A Polars dataframe containing the OHLC data and sorted in ascending order for the column timestamp
        time_period: An integer holding the time period value that we will use to calculate the average over
        column_name: The column whose values will be used to calculate the average over across the specified time periods
    Returns:
        A single column Polars DataFrame in Float64 dtype with the user-specified period as its column name, alongside the SMA values at every time period
    """
    variable_sma_final_output = pl.Series(name=f"ti_simple_moving_average_over_{time_period}_period",
                                          values=stock_dataframe[f"{column_name}"].rolling_mean(window_size=time_period),
                                          dtype=pl.Float64,
                                          nan_to_null=True).to_frame()

    return variable_sma_final_output