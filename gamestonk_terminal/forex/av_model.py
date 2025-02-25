"""AlphaVantage FX Model"""

import argparse
from typing import Dict
import os
import pandas as pd
import requests
from gamestonk_terminal import config_terminal as cfg


def check_valid_forex_currency(fx_symbol: str) -> str:
    """Check if given symbol is supported on alphavantage

    Parameters
    ----------
    fx_symbol : str
        Symbol to check

    Returns
    -------
    str
        Currency symbol

    Raises
    ------
    argparse.ArgumentTypeError
        Symbol not valid on alphavantage
    """
    path = os.path.join(os.path.dirname(__file__), "av_forex_currencies.csv")
    if fx_symbol.upper() in list(pd.read_csv(path)["currency code"]):
        return fx_symbol.upper()

    raise argparse.ArgumentTypeError(
        f"{fx_symbol.upper()} not found in alphavantage supported currency codes. "
    )


def get_quote(to_symbol: str, from_symbol: str) -> Dict:
    """Get current exchange rate quote from alpha vantage

    Parameters
    ----------
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol

    Returns
    -------
    Dict
        Dictionary of exchange rate
    """
    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RAT"
    url += f"E&from_currency={from_symbol}&to_currency={to_symbol}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url)
    if r.status_code != 200:
        return {}
    return r.json()


def get_historical(
    to_symbol: str,
    from_symbol: str,
    resolution: str = "d",
    interval: int = 5,
    start_date: str = "",
) -> pd.DataFrame:
    """Get historical forex data

    Parameters
    ----------
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol
    resolution : str, optional
        Resolution of data.  Can be "i", "d", "w", "m" for intraday, daily, weekly or monthly
    interval : int, optional
        Interval for intraday data
    start_date : str, optional
        Start date for data.

    Returns
    -------
    pd.DataFrame
        Historical data for forex pair
    """
    d_res = {"i": "FX_INTRADAY", "d": "FX_DAILY", "w": "FX_WEEKLY", "m": "FX_MONTHLY"}

    url = f"https://www.alphavantage.co/query?function={d_res[resolution]}&from_symbol={from_symbol}"
    url += f"&to_symbol={to_symbol}&outputsize=full&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    if resolution == "i":
        url += f"&interval={interval}min"

    r = requests.get(url)
    if r.status_code != 200:
        return pd.DataFrame()

    key = list(r.json().keys())[1]

    df = pd.DataFrame.from_dict(r.json()[key], orient="index")
    if start_date and resolution != "i":
        df = df[df.index > start_date]

    df = df.rename(
        columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
        }
    )
    df.index = pd.DatetimeIndex(df.index)
    return df.astype(float)
