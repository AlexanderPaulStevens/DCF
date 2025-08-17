"""
Custom type definitions for the financial forecasting application.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict


class SensitivityVariable(Enum):
    """Enum for sensitivity analysis variables."""

    EARNINGS_GROWTH_RATE = "earnings_growth_rate"
    DISCOUNT_RATE = "discount_rate"
    CAP_EX_GROWTH_RATE = "cap_ex_growth_rate"
    PERPETUAL_GROWTH_RATE = "perpetual_growth_rate"


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
class DCFResult:
    """Result of a single DCF calculation."""

    date: str
    enterprise_value: float
    equity_value: float
    share_price: float


DCFResults = Dict[str, DCFResult]


class APIResponse(TypedDict):
    """Response from financial API."""


class IncomeStatement(TypedDict):
    """Income statement data."""

    ticker: str
    period: str
    data: List[Dict[str, Any]]


class BalanceStatement(TypedDict):
    """Balance sheet data."""

    ticker: str
    period: str
    data: List[Dict[str, Any]]


class CashFlowStatement(TypedDict):
    """Cash flow statement data."""

    ticker: str
    period: str
    data: List[Dict[str, Any]]


class EnterpriseValueStatement(TypedDict):
    """Enterprise value statement data."""

    ticker: str
    period: str
    data: List[Dict[str, Any]]


@dataclass
class VisualizationData:
    """Data for visualization generation."""

    ticker: str
    enterprise_value: float
    equity_value: float
    share_price: float
    forecast_years: int
