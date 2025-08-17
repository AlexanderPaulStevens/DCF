"""
Custom exceptions for the financial forecasting application.
"""


class FinancialForecastingError(Exception):
    """Base exception for financial forecasting application."""


class APIError(FinancialForecastingError):
    """Raised when there's an error with API calls."""


class DataFetchError(APIError):
    """Raised when financial data cannot be fetched."""


class InvalidParameterError(FinancialForecastingError):
    """Raised when invalid parameters are provided."""


class DCFCalculationError(FinancialForecastingError):
    """Raised when DCF calculation fails."""


class VisualizationError(FinancialForecastingError):
    """Raised when visualization generation fails."""


class ConfigurationError(FinancialForecastingError):
    """Raised when there's a configuration issue."""
