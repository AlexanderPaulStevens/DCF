"""
DCF calculation service layer.
"""

import traceback
from decimal import Decimal
from typing import Dict, Optional, Tuple

from app.custom_types import DCFParameters, DCFResult, DCFResults
from app.exceptions import APIError, DataFetchError, DCFCalculationError
from app.modeling.data import FinancialDataFetcher


class DCFService:
    """Service for handling DCF calculations."""

    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True) -> None:
        """
        Initialize the DCF service.

        Args:
            api_key: Optional API key for financial data services
            use_cache: Whether to use caching (default: True)
        """
        self.data_fetcher = FinancialDataFetcher(api_key, use_cache)

    def calculate_dcf(
        self,
        ticker: str,
        forecast_years: int,
        discount_rate: float,
        earnings_growth_rate: float,
        cap_ex_growth_rate: float,
        perpetual_growth_rate: float,
        interval: str = "annual",
    ) -> DCFResult:
        """
        Calculate DCF for a single period.

        Args:
            ticker: Company ticker symbol
            forecast_years: Number of years to forecast
            discount_rate: Discount rate for future cash flows
            earnings_growth_rate: Assumed growth rate in earnings
            cap_ex_growth_rate: Assumed growth rate in capital expenditures
            perpetual_growth_rate: Assumed growth rate in perpetuity
            interval: Data interval (annual/quarter)

        Returns:
            DCFResult containing the calculation results

        Raises:
            DCFCalculationError: If calculation fails
        """
        try:
            # Fetch financial data
            ev_statement = self.data_fetcher.get_enterprise_value_statement(ticker, interval)
            income_statement = self.data_fetcher.get_income_statement(ticker, interval)
            balance_statement = self.data_fetcher.get_balance_statement(ticker, interval)
            cashflow_statement = self.data_fetcher.get_cashflow_statement(ticker, interval)

            # Calculate enterprise value
            enterprise_val = self._calculate_enterprise_value(
                income_statement.data[0:2],
                cashflow_statement.data[0:2],
                balance_statement.data[0:2],
                forecast_years,
                discount_rate,
                earnings_growth_rate,
                cap_ex_growth_rate,
                perpetual_growth_rate,
            )

            # Calculate equity value and share price
            equity_val, share_price = self._calculate_equity_value(
                enterprise_val, ev_statement.data[0]
            )

            # Print results
            self._print_dcf_results(ticker, enterprise_val, equity_val, share_price)

            return DCFResult(
                date=income_statement.data[0]["date"],
                enterprise_value=enterprise_val,
                equity_value=equity_val,
                share_price=share_price,
            )

        except Exception as e:
            raise DCFCalculationError(f"DCF calculation failed for {ticker}: {e}") from e

    def calculate_historical_dcf(self, params: DCFParameters) -> DCFResults:
        """
        Calculate DCF values over a historical timeframe.

        Args:
            params: DCFParameters containing all calculation parameters

        Returns:
            Dictionary mapping dates to DCF results

        Raises:
            DCFCalculationError: If data fetching fails
        """
        dcfs: DCFResults = {}

        # Determine number of intervals
        intervals = params.years * (4 if params.interval == "quarter" else 1)

        # Fetch all financial data upfront
        try:
            self.data_fetcher.get_enterprise_value_statement(params.ticker, params.interval)
            self.data_fetcher.get_income_statement(params.ticker, params.interval)
            self.data_fetcher.get_balance_statement(params.ticker, params.interval)
            self.data_fetcher.get_cashflow_statement(params.ticker, params.interval)
        except Exception as e:
            raise DCFCalculationError(f"Failed to fetch financial data: {e}") from e

        for interval_idx in range(intervals):
            try:
                dcf_result = self.calculate_dcf(
                    params.ticker,
                    params.forecast_years,
                    params.discount_rate,
                    params.earnings_growth_rate,
                    params.cap_ex_growth_rate,
                    params.perpetual_growth_rate,
                    params.interval,
                )
                dcfs[dcf_result.date] = dcf_result

            except (DCFCalculationError, APIError, DataFetchError) as e:
                print(f"Calculation error for interval {interval_idx}: {e}")
                print(traceback.format_exc())
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Unexpected error for interval {interval_idx}: {e}")
                print(traceback.format_exc())
            finally:
                print("-" * 60)

        return dcfs

    def _calculate_enterprise_value(
        self,
        income_statement: list,
        cashflow_statement: list,
        balance_statement: list,
        forecast_years: int,
        discount_rate: float,
        earnings_growth_rate: float,
        cap_ex_growth_rate: float,
        perpetual_growth_rate: float,
    ) -> float:
        """
        Calculate enterprise value using DCF methodology.

        Args:
            income_statement: Income statement data
            cashflow_statement: Cash flow statement data
            balance_statement: Balance sheet data
            forecast_years: Number of years to forecast
            discount_rate: Discount rate for future cash flows
            earnings_growth_rate: Assumed growth rate in earnings
            cap_ex_growth_rate: Assumed growth rate in capital expenditures
            perpetual_growth_rate: Assumed growth rate in perpetuity

        Returns:
            Calculated enterprise value
        """
        # Extract current period data
        current_income = income_statement[0]
        current_cashflow = cashflow_statement[0]

        # Calculate unlevered free cash flow
        ebit = float(current_income.get("EBIT", 0))
        tax_rate = 0.25  # Default tax rate - could be made configurable
        non_cash_charges = float(current_cashflow.get("Depreciation & Amortization", 0))
        cwc = self._calculate_change_in_working_capital(balance_statement)
        cap_ex = abs(float(current_cashflow.get("Capital Expenditure", 0)))

        current_fcf = self._calculate_unlevered_fcf(ebit, tax_rate, non_cash_charges, cwc, cap_ex)

        # Calculate present value of explicit period cash flows
        pv_explicit = 0
        for year in range(1, forecast_years + 1):
            # Project future cash flows
            future_fcf = current_fcf * (1 + earnings_growth_rate) ** year
            future_cap_ex = cap_ex * (1 + cap_ex_growth_rate) ** year

            # Adjust for projected capital expenditures
            future_fcf -= future_cap_ex

            # Discount to present value
            pv_explicit += future_fcf / (1 + discount_rate) ** year

        # Calculate terminal value
        terminal_fcf = current_fcf * (1 + earnings_growth_rate) ** forecast_years
        terminal_value = (
            terminal_fcf * (1 + perpetual_growth_rate) / (discount_rate - perpetual_growth_rate)
        )
        pv_terminal = terminal_value / (1 + discount_rate) ** forecast_years

        return pv_explicit + pv_terminal

    def _calculate_equity_value(
        self, enterprise_value: float, ev_statement: Dict
    ) -> Tuple[float, float]:
        """
        Calculate equity value and share price from enterprise value.

        Args:
            enterprise_value: Calculated enterprise value
            ev_statement: Enterprise value statement data

        Returns:
            Tuple of (equity_value, share_price)
        """
        total_debt = ev_statement.get("addTotalDebt", 0)
        cash_equivalents = ev_statement.get("minusCashAndCashEquivalents", 0)
        number_of_shares = ev_statement.get("numberOfShares", 1)

        equity_val = enterprise_value - total_debt + cash_equivalents
        share_price = equity_val / float(number_of_shares)

        return equity_val, share_price

    def _calculate_unlevered_fcf(
        self, ebit: float, tax_rate: float, non_cash_charges: float, cwc: float, cap_ex: float
    ) -> float:
        """
        Calculate unlevered free cash flow.

        Args:
            ebit: Earnings before interest and taxes
            tax_rate: Corporate tax rate
            non_cash_charges: Depreciation and amortization
            cwc: Change in working capital
            cap_ex: Capital expenditures

        Returns:
            Unlevered free cash flow
        """
        return ebit * (1 - tax_rate) + non_cash_charges + cwc + cap_ex

    def _calculate_change_in_working_capital(self, balance_statement: list) -> float:
        """
        Calculate change in working capital.

        Args:
            balance_statement: Balance sheet data

        Returns:
            Change in working capital
        """
        if len(balance_statement) < 2:
            return 0

        current = balance_statement[0]
        previous = balance_statement[1]

        current_wc = float(current.get("Total current assets", 0)) - float(
            current.get("Total current liabilities", 0)
        )
        previous_wc = float(previous.get("Total current assets", 0)) - float(
            previous.get("Total current liabilities", 0)
        )

        return current_wc - previous_wc

    def _print_dcf_results(
        self, ticker: str, enterprise_val: float, equity_val: float, share_price: float
    ) -> None:
        """
        Print DCF calculation results.

        Args:
            ticker: Company ticker symbol
            enterprise_val: Calculated enterprise value
            equity_val: Calculated equity value
            share_price: Calculated share price
        """
        print(
            f"\nEnterprise Value for {ticker}: ${'%.2E' % Decimal(str(enterprise_val))}.",
            f"\nEquity Value for {ticker}: ${'%.2E' % Decimal(str(equity_val))}.",
            f"\nPer share value for {ticker}: ${'%.2E' % Decimal(str(share_price))}.\n",
        )


# Legacy function for backward compatibility
def historical_dcf(
    ticker: str,
    years: int,
    forecast: int,
    discount_rate: float,
    earnings_growth_rate: float,
    cap_ex_growth_rate: float,
    perpetual_growth_rate: float,
    interval: str = "annual",
    api_key: str = "",
) -> DCFResults:
    """
    Legacy function for historical DCF calculation.

    Args:
        ticker: Company ticker symbol
        years: Number of years to analyze
        forecast: Number of years to forecast
        discount_rate: Discount rate for future cash flows
        earnings_growth_rate: Assumed growth rate in earnings
        cap_ex_growth_rate: Assumed growth rate in capital expenditures
        perpetual_growth_rate: Assumed growth rate in perpetuity
        interval: Data interval (annual/quarter)
        api_key: API key for financial data services

    Returns:
        Dictionary mapping dates to DCF results

    Note:
        This function is deprecated. Use DCFService.calculate_historical_dcf() instead.
    """
    service = DCFService(api_key)
    params = DCFParameters(
        ticker=ticker,
        years=years,
        forecast_years=forecast,
        discount_rate=discount_rate,
        earnings_growth_rate=earnings_growth_rate,
        cap_ex_growth_rate=cap_ex_growth_rate,
        perpetual_growth_rate=perpetual_growth_rate,
        interval=interval,
        api_key=api_key,
    )
    return service.calculate_historical_dcf(params)
