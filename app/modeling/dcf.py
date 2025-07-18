import traceback
from decimal import Decimal

from modeling.data import (
    get_income_statement,
    get_balance_statement,
    get_cashflow_statement,
    get_ev_statement,
)


def dcf(
    ticker,
    ev_statement,
    income_statement,
    balance_statement,
    cashflow_statement,
    discount_rate,
    forecast,
    earnings_growth_rate,
    cap_ex_growth_rate,
    perpetual_growth_rate,
):
    """
    a very basic 2-stage DCF implemented for learning purposes.
    see enterprise_value() for details on arguments.

    args:
        see enterprise value for more info...

    returns:
        dict: {'share price': __, 'enterprise_value': __, 'equity_value': __, 'date': __}
        CURRENT DCF VALUATION. See historical_dcf to fetch a history.
    """
    enterprise_val = enterprise_value(
        income_statement,
        cashflow_statement,
        balance_statement,
        forecast,
        discount_rate,
        earnings_growth_rate,
        cap_ex_growth_rate,
        perpetual_growth_rate,
    )

    equity_val, share_price = equity_value(enterprise_val, ev_statement)

    print(
        "\nEnterprise Value for {}: ${}.".format(ticker, "%.2E" % Decimal(str(enterprise_val))),
        "\nEquity Value for {}: ${}.".format(ticker, "%.2E" % Decimal(str(equity_val))),
        "\nPer share value for {}: ${}.\n".format(ticker, "%.2E" % Decimal(str(share_price))),
    )

    return {
        "date": income_statement[0]["date"],  # statement date used
        "enterprise_value": enterprise_val,
        "equity_value": equity_val,
        "share_price": share_price,
    }


def historical_dcf(
    ticker,
    years,
    forecast,
    discount_rate,
    earnings_growth_rate,
    cap_ex_growth_rate,
    perpetual_growth_rate,
    interval="annual",
    apikey="",
):
    """
    Wrap DCF to fetch DCF values over a historical timeframe, denoted period.

    args:
        same as DCF, except for
        period: number of years to fetch DCF for

    returns:
        {'date': dcf, ..., 'date', dcf}
    """
    dcfs = {}

    income_statement = get_income_statement(ticker=ticker, period=interval, apikey=apikey)[
        "financials"
    ]
    balance_statement = get_balance_statement(ticker=ticker, period=interval, apikey=apikey)[
        "financials"
    ]
    cashflow_statement = get_cashflow_statement(ticker=ticker, period=interval, apikey=apikey)[
        "financials"
    ]
    enterprise_value_statement = get_ev_statement(ticker=ticker, period=interval, apikey=apikey)

    if interval == "quarter":
        intervals = years * 4
    else:
        intervals = years

    for interval_idx in range(intervals):
        try:
            dcf_result = dcf(
                ticker,
                enterprise_value_statement[interval_idx],
                income_statement[interval_idx : interval_idx + 2],
                balance_statement[interval_idx : interval_idx + 2],
                cashflow_statement[interval_idx : interval_idx + 2],
                discount_rate,
                forecast,
                earnings_growth_rate,
                cap_ex_growth_rate,
                perpetual_growth_rate,
            )
        except (Exception, IndexError):
            print(traceback.format_exc())
            print(f"Interval {interval_idx} unavailable, no historical statement.")
        else:
            dcfs[dcf_result["date"]] = dcf_result
        print("-" * 60)

    return dcfs


def ul_fcf(ebit, tax_rate, non_cash_charges, cwc, cap_ex):
    """
    Formula to derive unlevered free cash flow to firm. Used in forecasting.

    args:
        ebit: Earnings before interest payments and taxes.
        tax_rate: The tax rate a firm is expected to pay. Usually a company's
            historical effective rate.
        non_cash_charges: Depreciation and amortization costs.
        cwc: Annual change in net working capital.
        cap_ex: capital expenditures, or what is spent to maintain zgrowth rate.

    returns:
        unlevered free cash flow
    """
    return ebit * (1 - tax_rate) + non_cash_charges + cwc + cap_ex


def get_discount_rate():
    """
    Calculate the Weighted Average Cost of Capital (WACC) for our company.
    Used for consideration of existing capital structure.

    args:

    returns:
        W.A.C.C.
    """
    return 0.1  # TODO: implement


def equity_value(enterprise_value, enterprise_value_statement):
    """
    Given an enterprise value, return the equity value by adjusting for cash/cash equivs.
    and total debt.

    args:
        enterprise_value: (EV = market cap + total debt - cash), or total value
        enterprise_value_statement: information on debt & cash

    returns:
        equity_value: (enterprise value - debt + cash)
        share_price: equity value/shares outstanding
    """
    # API field names are different from what the original code expected
    total_debt = enterprise_value_statement.get("addTotalDebt", 0)
    cash_equivalents = enterprise_value_statement.get("minusCashAndCashEquivalents", 0)
    number_of_shares = enterprise_value_statement.get("numberOfShares", 1)

    equity_val = enterprise_value - total_debt
    equity_val += cash_equivalents
    share_price = equity_val / float(number_of_shares)

    return equity_val, share_price


def enterprise_value(
    income_statement,
    cashflow_statement,
    balance_statement,
    period,
    discount_rate,
    earnings_growth_rate,
    cap_ex_growth_rate,
    perpetual_growth_rate,
):
    """
    Calculate enterprise value by NPV of explicit _period_ free cash flows + NPV of terminal value,
    both discounted by W.A.C.C.

    args:
        ticker: company for forecasting
        period: years into the future
        earnings growth rate: assumed growth rate in earnings, YoY
        cap_ex_growth_rate: assumed growth rate in cap_ex, YoY
        perpetual_growth_rate: assumed growth rate in perpetuity for terminal value, YoY

    returns:
        enterprise value
    """
    # XXX: statements are returned as historical list, 0 most recent
    if income_statement[0]["EBIT"]:
        ebit = float(income_statement[0]["EBIT"])
    else:
        ebit = float(input(f"EBIT missing. Enter EBIT on {income_statement[0]['date']} or skip: "))
    tax_rate = float(income_statement[0]["Income Tax Expense"]) / float(
        income_statement[0]["Earnings before Tax"]
    )
    non_cash_charges = float(cashflow_statement[0]["Depreciation & Amortization"])
    cwc = (
        float(balance_statement[0]["Total assets"])
        - float(balance_statement[0]["Total non-current assets"])
    ) - (
        float(balance_statement[1]["Total assets"])
        - float(balance_statement[1]["Total non-current assets"])
    )
    cap_ex = float(cashflow_statement[0]["Capital Expenditure"])
    discount = discount_rate

    flows = []

    # Now let's iterate through years to calculate FCF, starting with most recent year
    print(
        "Forecasting flows for {} years out, starting at {}.".format(
            period, income_statement[0]["date"]
        ),
        ("\n         DFCF   |    EBIT   |    D&A    |    CWC     |   CAP_EX   | "),
    )
    for yr in range(1, period + 1):
        # increment each value by growth rate
        ebit = ebit * (1 + (yr * earnings_growth_rate))
        non_cash_charges = non_cash_charges * (1 + (yr * earnings_growth_rate))
        cwc = cwc * 0.7  # TODO: evaluate this cwc rate? 0.1 annually?
        cap_ex = cap_ex * (1 + (yr * cap_ex_growth_rate))

        # discount by WACC
        flow = ul_fcf(ebit, tax_rate, non_cash_charges, cwc, cap_ex)
        pv_flow = flow / ((1 + discount) ** yr)
        flows.append(pv_flow)

        print(
            str(int(income_statement[0]["date"][0:4]) + yr) + "  ",
            "%.2E" % Decimal(pv_flow) + " | ",
            "%.2E" % Decimal(ebit) + " | ",
            "%.2E" % Decimal(non_cash_charges) + " | ",
            "%.2E" % Decimal(cwc) + " | ",
            "%.2E" % Decimal(cap_ex) + " | ",
        )

    npv_fcf = sum(flows)

    # now calculate terminal value using perpetual growth rate
    final_cashflow = flows[-1] * (1 + perpetual_growth_rate)
    tv = final_cashflow / (discount - perpetual_growth_rate)
    npv_tv = tv / (1 + discount) ** (1 + period)

    return npv_tv + npv_fcf
