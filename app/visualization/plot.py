"""
Plotting utilities for DCF analysis visualization.

This module provides functions for creating various types of plots comparing
DCF-forecasted share prices with historical share prices.
"""

import logging
import sys
from typing import Any, Dict

import matplotlib.pyplot as plt
import seaborn as sns

from app.modeling.data import get_historical_share_prices

# Configure logging for this module
logger = logging.getLogger(__name__)

# Set modern seaborn theme (replaces deprecated sns.set())
sns.set_theme(style="whitegrid", font_scale=1.0)

# Add parent directory to path for imports
sys.path.append("..")


def visualize(
    dcf_prices: Dict[str, Any], ticker: str, condition: Dict[str, Any], apikey: str
) -> None:
    """
    2d plot comparing dcf-forecasted per share price with historical share price.

    Args:
        dcf_prices: Dictionary containing DCF price data
        ticker: Company ticker symbol
        condition: Dictionary containing condition parameters
        apikey: API key for financial data services
    """
    dcf_share_prices = {}
    try:
        conditions = [str(cond) for cond in next(iter(condition.values()))]
    except IndexError:
        logger.error(f"Invalid condition format: {condition}")
        return
    for cond in conditions:
        dcf_share_prices[cond] = {k: v["share_price"] for k, v in dcf_prices.items()}
        plt.plot(
            list(dcf_share_prices[cond].keys()),
            list(dcf_share_prices[cond].values()),
            label=f"DCF {cond}",
        )
    historical_stock_prices = get_historical_share_prices(
        ticker=ticker,
        dates=list(dcf_share_prices[next(iter(dcf_share_prices.keys()))].keys())[::-1],
        apikey=apikey,
    )
    plt.plot(
        list(historical_stock_prices.keys()),
        list(historical_stock_prices.values()),
        label="Historical Share Price",
    )
    plt.legend(loc="upper right")
    plt.title("$" + ticker + "  ")
    plt.savefig(f"imgs/{ticker}_{next(iter(condition.keys()))}.png")
    plt.show()


def visualize_bulk_historicals(
    dcfs: Dict[str, Any], ticker: str, condition: Dict[str, Any], apikey: str
) -> None:
    """
    Multiple 2d plot comparing historical DCFs of different growth assumption conditions.

    Args:
        dcfs: List of DCFs of format {'value1': {'year1': dcf}, ...}
        condition: Dict of format {'condition': [value1, value2, value3]}
        ticker: Company ticker symbol
        apikey: API key for financial data services
    """
    dcf_share_prices = {}
    try:
        conditions = [str(cond) for cond in next(iter(condition.values()))]
    except IndexError:
        logger.error(f"Invalid condition format: {condition}")
        conditions = [condition["Ticker"]]

    for cond in conditions:
        dcf_share_prices[cond] = {}
        years = dcfs[cond].keys()
        for year in years:
            dcf_share_prices[cond][year] = dcfs[cond][year]["share_price"]

    for cond in conditions:
        plt.plot(
            list(dcf_share_prices[cond].keys())[::-1],
            list(dcf_share_prices[cond].values())[::-1],
            label=cond,
        )

    # sorry for anybody reading this, bit too pythonic
    # the second argument here just fetches the list of dates we're using as x values
    # in the above plt.plot() call without knowing the conditions we index with above
    historical_stock_prices = get_historical_share_prices(
        ticker=ticker,
        dates=list(dcf_share_prices[next(iter(dcf_share_prices.keys()))].keys())[::-1],
        apikey=apikey,
    )
    plt.plot(
        list(historical_stock_prices.keys()),
        list(historical_stock_prices.values()),
        label="${} over time".format(ticker),
    )

    plt.xlabel("Date")
    plt.ylabel("Share price ($)")
    plt.legend(loc="upper right")
    plt.title("$" + ticker + "  ")
    plt.savefig("imgs/{}_{}.png".format(ticker, next(iter(condition.keys()))))
    plt.show()


def visualize_historicals(dcfs: Dict[str, Any]) -> None:
    """
    2d plot comparing dcf history to share price history.

    Args:
        dcfs: Dictionary containing DCF historical data
    """
    dcf_share_prices = {}
    for k, v in dcfs.items():
        dcf_share_prices[dcfs[k]["date"]] = v["share_price"]

    xs = list(dcf_share_prices.keys())[::-1]
    ys = list(dcf_share_prices.values())[::-1]

    plt.scatter(xs, ys)
    plt.show()
