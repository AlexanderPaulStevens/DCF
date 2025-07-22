"""
Financial data fetching utilities using financialmodelingprep.com API.

NOTE: Some code taken directly from their documentation. See: https://financialmodelingprep.com/developer/docs/.
"""

import json
import traceback
from typing import Dict, List, Optional
from urllib.request import URLError, urlopen

from app.config import config
from app.custom_types import (
    APIResponse,
    BalanceStatement,
    CashFlowStatement,
    EnterpriseValueStatement,
    IncomeStatement,
)
from app.exceptions import APIError, DataFetchError, InvalidParameterError
from app.services.cache_service import CacheService


class FinancialDataFetcher:
    """Handles fetching financial data from the API with caching."""

    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True) -> None:
        """
        Initialize the data fetcher.

        Args:
            api_key: API key for financial data services
            use_cache: Whether to use caching (default: True)
        """
        self.api_key = api_key or config.api.api_key
        if not self.api_key:
            raise InvalidParameterError("API key is required")

        self.use_cache = use_cache
        self.cache_service = CacheService() if use_cache else None

    def _build_url(self, endpoint: str, ticker: str, period: str = "annual") -> str:
        """Build API URL for the given endpoint and parameters."""
        if period not in ["annual", "quarter"]:
            raise InvalidParameterError(f"Invalid period: {period}")

        base_url = config.api.base_url
        if period == "annual":
            return f"{base_url}/{endpoint}/{ticker}?apikey={self.api_key}"
        else:
            return f"{base_url}/{endpoint}/{ticker}?period=quarter&apikey={self.api_key}"

    def _fetch_json_data(self, url: str) -> APIResponse:
        """Fetch and parse JSON data from the given URL."""
        try:
            # Validate URL scheme for security
            if not url.startswith(("http://", "https://")):
                raise DataFetchError(f"Invalid URL scheme: {url}")
            response = urlopen(url)  # noqa: S310
        except URLError as e:
            error_msg = f"Error retrieving {url}"
            try:
                error_msg += f": {e.read().decode()}"
            except AttributeError:
                pass
            raise DataFetchError(error_msg) from e

        try:
            data = response.read().decode("utf-8")
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise DataFetchError(f"JSON decode error for {url}: {e}") from e

        if "Error Message" in json_data:
            raise APIError(f"API Error for '{url}': {json_data['Error Message']}")

        return json_data

    def _get_cached_or_fetch(
        self, ticker: str, data_type: str, period: str = "annual"
    ) -> APIResponse:
        """
        Get data from cache if available, otherwise fetch from API.

        Args:
            ticker: Company ticker symbol
            data_type: Type of financial data
            period: Data period ('annual' or 'quarter')

        Returns:
            Financial data from cache or API
        """
        if self.use_cache and self.cache_service:
            # Try to load from cache first
            cached_data = self.cache_service.load_data(ticker, data_type, period)
            if cached_data is not None:
                print(f"Using cached data for {ticker} {data_type}")
                return cached_data

        # Fetch from API
        url = self._build_url(data_type, ticker, period)
        data = self._fetch_json_data(url)

        # Save to cache if caching is enabled
        if self.use_cache and self.cache_service:
            try:
                self.cache_service.save_data(ticker, data_type, data, period)
                print(f"Cached data for {ticker} {data_type}")
            except (OSError, IOError, ValueError, TypeError) as e:
                print(f"Warning: Failed to cache data for {ticker}: {e}")

        return data

    def get_enterprise_value_statement(
        self, ticker: str, period: str = "annual"
    ) -> EnterpriseValueStatement:
        """Fetch enterprise value statement."""
        data = self._get_cached_or_fetch(ticker, "enterprise-value", period)
        return EnterpriseValueStatement(ticker=ticker, period=period, data=data)

    def get_income_statement(self, ticker: str, period: str = "annual") -> IncomeStatement:
        """Fetch income statement."""
        data = self._get_cached_or_fetch(ticker, "financials/income-statement", period)
        return IncomeStatement(ticker=ticker, period=period, data=data.get("financials", []))

    def get_cashflow_statement(self, ticker: str, period: str = "annual") -> CashFlowStatement:
        """Fetch cash flow statement."""
        data = self._get_cached_or_fetch(ticker, "financials/cash-flow-statement", period)
        return CashFlowStatement(ticker=ticker, period=period, data=data.get("financials", []))

    def get_balance_statement(self, ticker: str, period: str = "annual") -> BalanceStatement:
        """Fetch balance sheet statement."""
        data = self._get_cached_or_fetch(ticker, "financials/balance-sheet-statement", period)
        return BalanceStatement(ticker=ticker, period=period, data=data.get("financials", []))

    def get_stock_price(self, ticker: str) -> Dict[str, float]:
        """Fetch current stock price."""
        url = f"{config.api.base_url}/stock/real-time-price/{ticker}?apikey={self.api_key}"
        data = self._fetch_json_data(url)
        return {"symbol": ticker, "price": data["price"]}

    def get_batch_stock_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Fetch stock prices for multiple tickers."""
        prices = {}
        for ticker in tickers:
            try:
                price_data = self.get_stock_price(ticker)
                prices[ticker] = price_data["price"]
            except (APIError, DataFetchError) as e:
                print(f"Error fetching price for {ticker}: {e}")
                continue
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Unexpected error fetching price for {ticker}: {e}")
                continue
        return prices

    def get_historical_share_prices(self, ticker: str, dates: List[str]) -> Dict[str, float]:
        """Fetch historical stock prices for given dates."""
        prices = {}
        for date in dates:
            try:
                # Calculate date range for API call
                date_start = date[0:8] + str(int(date[8:]) - 2)
                date_end = date

                url = (
                    f"{config.api.base_url}/historical-price-full/{ticker}"
                    f"?from={date_start}&to={date_end}&apikey={self.api_key}"
                )

                data = self._fetch_json_data(url)
                prices[date_end] = data["historical"][0]["close"]

            except (ValueError, IndexError) as e:
                print(f"Error parsing date '{date}': {e}")
                print(traceback.format_exc())
                continue
            except (APIError, DataFetchError) as e:
                print(f"Error fetching historical price for {date}: {e}")
                continue
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Unexpected error fetching historical price for {date}: {e}")
                continue

        return prices

    def clear_cache(self, ticker: Optional[str] = None, data_type: Optional[str] = None) -> None:
        """
        Clear cached data.

        Args:
            ticker: Specific ticker to clear (if None, clears all)
            data_type: Specific data type to clear (if None, clears all)
        """
        if self.cache_service:
            self.cache_service.clear_cache(ticker, data_type)

    def get_cache_info(self) -> Dict:
        """
        Get information about cached data.

        Returns:
            Dictionary with cache statistics
        """
        if self.cache_service:
            return self.cache_service.get_cache_info()
        return {"error": "Caching is disabled"}


# Legacy functions for backward compatibility
def get_api_url(requested_data: str, ticker: str, period: str, apikey: str) -> str:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return fetcher._build_url(requested_data, ticker, period)


def get_jsonparsed_data(url: str) -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher()
    return fetcher._fetch_json_data(url)


def get_ev_statement(ticker: str, period: str = "annual", apikey: str = "") -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return fetcher.get_enterprise_value_statement(ticker, period).data


def get_income_statement(ticker: str, period: str = "annual", apikey: str = "") -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return {"financials": fetcher.get_income_statement(ticker, period).data}


def get_cashflow_statement(ticker: str, period: str = "annual", apikey: str = "") -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return {"financials": fetcher.get_cashflow_statement(ticker, period).data}


def get_balance_statement(ticker: str, period: str = "annual", apikey: str = "") -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return {"financials": fetcher.get_balance_statement(ticker, period).data}


def get_stock_price(ticker: str, apikey: str = "") -> Dict[str, float]:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return fetcher.get_stock_price(ticker)


def get_batch_stock_prices(tickers: List[str], apikey: str = "") -> Dict[str, float]:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return fetcher.get_batch_stock_prices(tickers)


def get_historical_share_prices(
    ticker: str, dates: List[str], apikey: str = ""
) -> Dict[str, float]:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return fetcher.get_historical_share_prices(ticker, dates)


if __name__ == "__main__":
    """Quick test - run data.py directly."""
    try:
        fetcher = FinancialDataFetcher()
        data = fetcher.get_cashflow_statement("AAPL")
        print("Successfully fetched cash flow statement for AAPL")
        print(f"Number of periods: {len(data.data)}")
    except (APIError, DataFetchError) as e:
        print(f"API Error: {e}")
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Unexpected error: {e}")
