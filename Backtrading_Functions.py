# --- Imports ---
# Core
import backtrader
from backtrader_plotly.plotter import BacktraderPlotly
from backtrader_plotly.scheme import PlotScheme
import polars as pl
import math

# --- Backtrader - Analyzer - Analyzes the current position for any given time period ---
class TradeLogger(backtrader.analyzers.Analyzer):
    """
    Analyzer
    Analyzes the current trading period for the key information such as bar open, bar close, etc. 
    """
    def start(self):
      super(TradeLogger, self).start()

    def log(self, txt):
        """ Logging Function """
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f'{dt}, {txt}')

    def create_analysis(self):
      self.rets = []
      self.vals = dict()
      self.order = None
      self.price = None
      self.comm = None

    def notify_trade(self, trade):
      # Receives trade notifications before each next cycle
      if not trade.isclosed:
        return
      
      if trade.isclosed:
        self.vals = {'Date': self.strategy.datetime.datetime(),
                     'Bar Open': round(trade.baropen),
                     'Bar Close': round(trade.barclose),
                     'Trade Price': round(trade.price),
                     'Trade Duration (in days)': (trade.dtclose - trade.dtopen),
                     'Trade Commission': trade.commission,
                     'Gross Profit and Loss': round(trade.pnl, 2),
                     'Net Profit and Loss': round(trade.pnlcomm, 2),
        }
        self.rets.append(self.vals)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Print the executed buy order
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'Buy Executed ---- Price: {order.executed.price: .2f}, Cost: {order.executed.value: .2f}, Commission: {order.executed.comm: .2f}')
                self.price = order.executed.price
                self.comm = order.executed.comm
            else:
                self.log(f'Sell Executed ---- Price: {order.executed.price: .2f}, Cost: {order.executed.value: .2f}, Commission: {order.executed.comm: .2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Failed')
        self.order = None

    def get_analysis(self):
      return self.rets

# --- Backtrader - Trade Sizer - Sizer class for determining buy/sell decisions based on risk and other factors ---
class variablesizer_max_risk(backtrader.Sizer):
  """
  Variable Stake (Sizer) Class - Created in order to mimic the reasoning of a real-life trader

  Takes into account the risk associated w/ a trade by accounting for the traders initial account balance
  Will return the number of shares that can be traded based on the maximum risk tolerance of a given trader
  Also accounts for the amount of commission associated with each trade
  """
  params = (('risk', 0.1),
            ('debug', True))

  def _getsizing(self, comminfo, cash, data, isbuy):
    size = 0

    # Calculate the maximum risk we can take assuming that all of the account balance can be used
    maximum_risk_stake = math.floor(cash * self.p.risk)

    comm = comminfo.p.commission

    # Percentage-based commissions - first apply the commission to the trade, and then divide the risk by this value
    if comminfo.stocklike:
      com_adj_price = data[0] * (1 + (comm * 2))
      comm_adj_max_risk = "N/A"

      if isbuy == True:
        comm_adj_size = maximum_risk_stake / com_adj_price
        if comm_adj_size < 0:
          # Prevent from accidently going short
          comm_adj_size = 0
      else:
        comm_adj_size = maximum_risk_stake / com_adj_price * -1

    else:
      # Use a fixed size staking, and deduct commission from the available investment account balance
      comm_adj_max_risk = maximum_risk_stake - (comm * 2)
      comm_adj_max_risk = "N/A"

      # In the case that the trader does not have enough cash for a trade
      if comm_adj_max_risk < 0:
        return 0

      if isbuy == True:
        comm_adj_size = comm_adj_max_risk / data[0]
      else:
        comm_adj_size = comm_adj_max_risk / data[0] * -1

    comm_adj_size = math.floor(comm_adj_size)

    if self.p.debug:
      if isbuy:
        buysell = 'BUY'
      else:
        buysell = 'SELL'
    
      print(f"""
            |---Staker Debug---|\n
            Action: {buysell}\n
            Price: {data[0]}\n
            Cash: {cash}\n
            Max Risk %: {self.p.risk}\n
            Max Risk $: {maximum_risk_stake}\n
            Commission Adjusted Max Risk: {comm_adj_max_risk}\n
            Current Price: {data[0]}\n
            Commission: {comm}\n
            Commission Adj Price (Round Trip): {com_adj_price}\n
            Size: {comm_adj_size}\n
            |---|
            """)
      
    return comm_adj_size

# --- Backtrader - Strategy - Buy and Hold Strategy for the given stock --- 
class buy_and_hold_strategy(backtrader.Strategy):
  """
  Simple Buy & Hold Strategy
  Used for comparing between active trading and passive trading strategies.
  Enter the market at the earliest possible time period and hold the stock
  """
  def __init__(self):
    self.data_open = self.datas[0].open
    self.data_close = self.datas[0].close

    self.order = None
    self.price = None
    self.comm = None
    self.size = None

  def log(self, text):
    dt = self.datas[0].datetime.date(0).isoformat()
    print(f'{dt}, {text}')

  def nextstart(self):
    if self.order:
      return

    # Key - Buy as much of the stock as possible within the limits of the account balance and the maximum stake possible at any one time
    maximum_trade_stake = int(self.broker.get_cash() / self.data_close)
    self.buy(size=maximum_trade_stake)

# --- Backtrader - Feed - Converts a Polars Dataframe into a data feed processable by Backtrader ---
def backtrader_data_to_feed(stock_dataframe: pl.DataFrame):
  """
  Converts a Polars DataFrame to a Pandas DataFrame and then to a Backtrader feed data where it can be processed by all the other Backtrader classes

  Args:
    stock_dataframe: The user-queried stock Polars Dataframe to be converted
  Returns:
    The data converted into a Backtrader Feeds data stream
  """
  stock_feed = backtrader.feeds.PandasData(dataname=stock_dataframe.to_pandas())

  return stock_feed

# --- Backtrader - Initialization - Runner class for the trading strategy ---
def buy_and_hold_stock_trader_init(stock_dataframe: pl.DataFrame,
                                   strategy: backtrader.Strategy = buy_and_hold_strategy, 
                                   initial_account_balance: int = 1000, 
                                   commission: float = 0, 
                                   stake: int = 5):
    """
    Runner class for executing any trading strategy
    Modify this with any changes to analyzers to gauge the metrics of the trade.
    Documentation @ https://www.backtrader.com/docu/analyzers/analyzers/

    Args:
        stock_dataframe: The user-queried stock Polars Dataframe
        strategy: A backtrader.Strategy class that outlines the strategy to be implemented by the trading algorithm
        initial_account_balance: The amount of initial cash that the trader has access to in an integer datatype 
        commission: The percentage commision charged for each performed trade represented in a float datatype
        stake: The amount of trades that the trader can perform at any single point in time
    Returns:
        A return code for the successful/fail run of the Cerebro engine.
        The graph figure with all of the key information (trades executed, candlestick chart, and other metrics) outputted
    """
    # Initialize Cerebro engine, add the strategy and initial capital
    cerebro = backtrader.Cerebro()

    # Initialize the key information
    cerebro.addstrategy(strategy=strategy)
    cerebro.adddata(data=backtrader_data_to_feed(stock_dataframe))
    cerebro.broker.setcash(initial_account_balance)
    
    # Output the initial account balance separate to the other trading information
    print(f"""
          \nInitial Account Balance: {cerebro.broker.getvalue()}\n
           """)

    # Broker commission that the trader has to pay
    cerebro.broker.setcommission(commission)

    # Number of shares that the trader can buy/sell
    cerebro.addsizer(variablesizer_max_risk, risk=0.5, debug=True)

    # Evaluation metrics to determine the performance of the trader
    cerebro.addanalyzer(backtrader.analyzers.Returns, timeframe=backtrader.TimeFrame.Days, tann=365)
    cerebro.addanalyzer(backtrader.analyzers.SharpeRatio, timeframe=backtrader.TimeFrame.Days, compression=1, factor=365, annualize=True)
    cerebro.addanalyzer(backtrader.analyzers.VWR, timeframe=backtrader.TimeFrame.Days, tann=365)
    cerebro.addanalyzer(TradeLogger, _name="trade_logger")

    results = cerebro.run()
    
    # Outputting key information about any key points within the TraderLogs
    print(f"""
          \n|---|\n
          Average Return for the Entire Period: {results[0].analyzers.returns.get_analysis()['ravg']}\n
          Variability-Weighted Return (in %): {results[0].analyzers.vwr.get_analysis()['vwr']}\n
          Sharpe Ratio: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']}\n
          Total Compound Return: {results[0].analyzers.returns.get_analysis()['rtot']}\n
          |---|\n
          Current Account Balance: {cerebro.broker.getvalue()}\n
          """)
    
    # Plot the key information, trades, and other information
    scheme = PlotScheme(decimal_places=3)
    figs = cerebro.plot(BacktraderPlotly(show=True, scheme=scheme))