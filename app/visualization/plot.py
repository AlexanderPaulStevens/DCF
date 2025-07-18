"""
Quick visualization toolkit. I'd like to build this out to be decently powerful
in terms of enabling quick interpretation of DCF related data.
"""

import sys

import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append("..")
from modeling.data import get_historical_share_prices

sns.set()
sns.set_context("paper")


def visualize(dcf_prices, ticker, condition, apikey):
    """
    2d plot comparing dcf-forecasted per share price with historical share price.
    """
    dcf_share_prices = {}
    try:
        conditions = [str(cond) for cond in next(iter(condition.values()))]
    except IndexError:
        print(condition)
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


def visualize_bulk_historicals(dcfs, ticker, condition, apikey):
    """
    multiple 2d plot comparing historical DCFS of different growth
    assumption conditions

    args:
        dcfs: list of dcfs of format {'value1', {'year1': dcf}, ...}
        condition: dict of format {'condition': [value1, value2, value3]}

    """
    dcf_share_prices = {}
    try:
        conditions = [str(cond) for cond in next(iter(condition.values()))]
    except IndexError:
        print(condition)
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
    # in the above plt.plot() call without knowing the conditions we index with abo
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


def visualize_historicals(dcfs):
    """
    2d plot comparing dcf history to share price history
    """

    dcf_share_prices = {}
    for k, v in dcfs.items():
        dcf_share_prices[dcfs[k]["date"]] = v["share_price"]

    xs = list(dcf_share_prices.keys())[::-1]
    ys = list(dcf_share_prices.values())[::-1]

    plt.scatter(xs, ys)
    plt.show()
