import pandas as pd
import datetime as dt
from binance.client import Client
from misc.logger import Logger, ascii_symbols
import sys


logger = Logger()

try:

    logger.info("Connecting to Binance API", end="  ")
    client = Client()
    logger.print(ascii_symbols.TICK)

except Exception as e:

    logger.print("ERROR")
    logger.error("Couldn't connect to Binance API")
    logger.print("Exception:")
    logger.print(e)
    logger.error("Terminating bot...")
    sys.exit(1)


def get_symbols():

    symbols = []
    exchange_info = client.get_exchange_info()
    for s in exchange_info["symbols"]:

        if (s["symbol"][-4:] == "USDT"):

            symbols.append(s["symbol"])

    return symbols


def get_historical_ohlc_data(symbol, past_days=None, interval=None):
    """Returns historical klines from past for given symbol and interval
    past_days: how many days back one wants to download the data"""

    if not interval:
        interval = "1h"  # default interval 1 hour
    if not past_days:
        past_days = 30  # default past days 30.

    start_str = str(
        (pd.to_datetime("today")-pd.Timedelta(str(past_days)+" days")).date())

    D = pd.DataFrame(client.get_historical_klines(
        symbol=symbol, start_str=start_str, interval=interval))
    D.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time",
                 "qav", "num_trades", "taker_base_vol", "taker_quote_vol", "is_best_match"]
    D["open_date_time"] = [
        dt.datetime.fromtimestamp(x/1000) for x in D.open_time]
    D["symbol"] = symbol
    D = D[["symbol", "open_date_time", "open", "high", "low", "close",
           "volume", "num_trades", "taker_base_vol", "taker_quote_vol"]]

    return D
