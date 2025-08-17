"""
Configuration settings for the financial forecasting application.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class APIConfig:
    """API configuration settings."""

    base_url: str = "https://financialmodelingprep.com/api/v3"
    api_key: Optional[str] = None

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.environ.get("APIKEY")


@dataclass
class DCFConfig:
    """DCF model configuration settings."""

    default_forecast_years: int = 5
    default_discount_rate: float = 0.1
    default_earnings_growth_rate: float = 0.05
    default_cap_ex_growth_rate: float = 0.045
    default_perpetual_growth_rate: float = 0.05
    default_interval: str = "annual"
    default_years: int = 1
    default_steps: int = 5


@dataclass
class VisualizationConfig:
    """Visualization configuration settings."""

    output_directory: str = "app/imgs"
    figure_size: tuple[int, int] = (12, 9)
    dpi: int = 150
    style: str = "seaborn-v0_8"
    color_palette: str = "husl"


@dataclass
class AppConfig:
    """Main application configuration."""

    api: APIConfig = None
    dcf: DCFConfig = None
    visualization: VisualizationConfig = None

    def __post_init__(self) -> None:
        if self.api is None:
            self.api = APIConfig()
        if self.dcf is None:
            self.dcf = DCFConfig()
        if self.visualization is None:
            self.visualization = VisualizationConfig()


# Global configuration instance
config = AppConfig()
