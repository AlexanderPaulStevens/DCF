"""
Type definitions for the financial forecasting application.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


@dataclass
class DCFResult:
    """Result of a DCF calculation."""

    date: str
    enterprise_value: float
    equity_value: float
    share_price: float


@dataclass
class FinancialStatement:
    """Base class for financial statements."""

    ticker: str
    period: str
    data: List[Dict[str, Any]]


@dataclass
class IncomeStatement(FinancialStatement):
    """Income statement data."""


@dataclass
class BalanceStatement(FinancialStatement):
    """Balance sheet data."""


@dataclass
class CashFlowStatement(FinancialStatement):
    """Cash flow statement data."""


@dataclass
class EnterpriseValueStatement:
    """Enterprise value statement data."""

    ticker: str
    period: str
    data: Dict[str, Any]


@dataclass
class DCFParameters:
    """Parameters for DCF calculation."""

    ticker: str
    years: int
    forecast_years: int
    discount_rate: float
    earnings_growth_rate: float
    cap_ex_growth_rate: float
    perpetual_growth_rate: float
    interval: str
    api_key: Optional[str] = None


@dataclass
class VisualizationData:
    """Data for visualization."""

    ticker: str
    enterprise_value: float
    equity_value: float
    share_price: float
    forecast_years: int


# Type aliases for better readability
DCFResults = Dict[str, DCFResult]
FinancialData = Union[IncomeStatement, BalanceStatement, CashFlowStatement]
APIResponse = Dict[str, Any]
