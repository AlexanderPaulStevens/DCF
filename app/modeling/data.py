"""
Financial data fetching utilities using financialmodelingprep.com API.

NOTE: Some code taken directly from their documentation. See: https://financialmodelingprep.com/developer/docs/.
"""

import json
import logging
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

# Configure logging for this module
logger = logging.getLogger(__name__)


class FinancialDataFetcher:
    """Handles fetching financial data from the API with caching."""

    def __init__(self, api_key: Optional[str] = None, caching: bool = True) -> None:
        """
        Initialize the data fetcher.

        Args:
            api_key: API key for financial data services
            caching: Whether to enable caching (default: True)
        """
        self.api_key = api_key or config.api.api_key
        if not self.api_key:
            raise InvalidParameterError("API key is required")

        self.caching = caching
        self.cache_service = CacheService() if caching else None

    def _build_url(self, endpoint: str, ticker: str, period: str = "annual") -> str:
        """Build API URL for the given endpoint and parameters."""
        if period not in ["annual", "quarter"]:
            raise InvalidParameterError(f"Invalid period: {period}")

        base_url = config.api.base_url
        if period == "annual":
            return f"{base_url}/{endpoint}/{ticker}?apikey={self.api_key}"
        else:
            return f"{base_url}/{endpoint}/{ticker}?period=quarter&apikey={self.api_key}"

    def _validate_financial_data(self, data: APIResponse, data_type: str) -> None:
        """
        Validate financial data for quality and completeness.

        Args:
            data: Financial data to validate
            data_type: Type of financial data being validated

        Raises:
            DataFetchError: If data validation fails
        """
        if not data:
            raise DataFetchError(f"Empty data received for {data_type}")

        # Check for common API error responses
        if isinstance(data, dict):
            if "Error Message" in data:
                raise APIError(f"API Error for {data_type}: {data['Error Message']}")
            if "Note" in data and "limit" in data["Note"].lower():
                raise APIError(f"API rate limit exceeded for {data_type}")

        # Validate data structure based on type
        if data_type in [
            "financials/income-statement",
            "financials/cash-flow-statement",
            "financials/balance-sheet-statement",
        ]:
            if "financials" not in data:
                raise DataFetchError(f"Missing 'financials' key in {data_type} response")
            if not data["financials"]:
                raise DataFetchError(f"Empty financials data for {data_type}")

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
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e

        try:
            data = response.read().decode("utf-8")
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {url}: {e}")
            raise DataFetchError(f"JSON decode error for {url}: {e}")

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
        if self.caching and self.cache_service:
            # Try to load from cache first
            cached_data = self.cache_service.load_data(ticker, data_type, period)
            if cached_data is not None:
                logger.info(f"Using cached data for {ticker} {data_type}")
                return cached_data

        # Fetch from API (caching disabled doesn't prevent API calls)
        url = self._build_url(data_type, ticker, period)
        data = self._fetch_json_data(url)

        # Validate the fetched data
        self._validate_financial_data(data, data_type)

        # Save to cache if caching is enabled
        if self.caching and self.cache_service:
            try:
                self.cache_service.save_data(ticker, data_type, data, period)
                logger.info(f"Cached data for {ticker} {data_type}")
            except (OSError, IOError, ValueError, TypeError) as e:
                logger.warning(f"Failed to cache data for {ticker}: {e}")

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

        # Validate stock price data
        if "price" not in data:
            raise DataFetchError(f"Missing price data for {ticker}")

        price = data["price"]
        if not isinstance(price, (int, float)) or price <= 0:
            raise DataFetchError(f"Invalid price value for {ticker}: {price}")

        return {"symbol": ticker, "price": price}

    def get_batch_stock_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Fetch stock prices for multiple tickers."""
        prices = {}
        for ticker in tickers:
            try:
                price_data = self.get_stock_price(ticker)
                prices[ticker] = price_data["price"]
            except (APIError, DataFetchError) as e:
                logger.error(f"Error fetching price for {ticker}: {e}")
                continue
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Unexpected error fetching price for {ticker}: {e}")
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

                # Validate historical price data
                if "historical" not in data or not data["historical"]:
                    logger.warning(f"No historical data available for {ticker} on {date_end}")
                    continue

                close_price = data["historical"][0]["close"]
                if not isinstance(close_price, (int, float)) or close_price <= 0:
                    logger.warning(f"Invalid close price for {ticker} on {date_end}: {close_price}")
                    continue

                prices[date_end] = close_price

            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing date '{date}': {e}")
                logger.debug(traceback.format_exc())
                continue
            except (APIError, DataFetchError) as e:
                logger.error(f"Error fetching historical price for {date}: {e}")
                continue
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Unexpected error fetching historical price for {date}: {e}")
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
    return fetcher.get_enterprise_value_statement(ticker, period)["data"]


def get_income_statement(ticker: str, period: str = "annual", apikey: str = "") -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return {"financials": fetcher.get_income_statement(ticker, period)["data"]}


def get_cashflow_statement(ticker: str, period: str = "annual", apikey: str = "") -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return {"financials": fetcher.get_cashflow_statement(ticker, period)["data"]}


def get_balance_statement(ticker: str, period: str = "annual", apikey: str = "") -> APIResponse:
    """Legacy function - use FinancialDataFetcher instead."""
    fetcher = FinancialDataFetcher(apikey)
    return {"financials": fetcher.get_balance_statement(ticker, period)["data"]}


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
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        fetcher = FinancialDataFetcher()
        data = fetcher.get_cashflow_statement("AAPL")
        logger.info("Successfully fetched cash flow statement for AAPL")
        logger.info(f"Number of periods: {len(data['data'])}")
    except (APIError, DataFetchError) as e:
        logger.error(f"API Error: {e}")
    except (ValueError, TypeError, AttributeError) as e:
        logger.error(f"Unexpected error: {e}")
