"""
Argument parser for the financial forecasting application.

This module handles command-line argument parsing and validation for the DCF analysis
application, providing a user-friendly interface for configuring analysis parameters.
"""

import argparse
import logging

from app.config import config
from app.services.cache_service import CacheService

# Configure logging for this module
logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.Namespace:
    """
    Create and configure the argument parser.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Financial forecasting application using DCF modeling"
    )

    # Core parameters
    parser.add_argument(
        "--period",
        help="Years to forecast",
        type=int,
        default=config.dcf.default_forecast_years,
    )
    parser.add_argument(
        "--ticker", help="Single ticker to do historical DCF", type=str, default="AAPL"
    )
    parser.add_argument(
        "--years",
        help="Number of years to compute DCF analysis for",
        type=int,
        default=config.dcf.default_years,
    )
    parser.add_argument(
        "--interval",
        help='Interval period for each calc, either "annual" or "quarter"',
        default=config.dcf.default_interval,
    )

    # Sensitivity analysis parameters
    parser.add_argument(
        "--step_increase",
        help="Step increase for sensitivity analysis",
        type=float,
        default=0,
    )
    parser.add_argument(
        "--steps",
        help="Steps to take if --step_increase is > 0",
        type=int,
        default=config.dcf.default_steps,
    )
    parser.add_argument(
        "--variable",
        help="Variable to increase for sensitivity analysis: [earnings_growth_rate, discount_rate]",
        default=None,
    )

    # DCF model parameters
    parser.add_argument(
        "--discount_rate",
        help="Discount rate for future cash flow to firm",
        type=float,
        default=config.dcf.default_discount_rate,
    )
    parser.add_argument(
        "--earnings_growth_rate",
        help="Growth in revenue, YoY",
        type=float,
        default=config.dcf.default_earnings_growth_rate,
    )
    parser.add_argument(
        "--cap_ex_growth_rate",
        help="Growth in cap_ex, YoY",
        type=float,
        default=config.dcf.default_cap_ex_growth_rate,
    )
    parser.add_argument(
        "--perpetual_growth_rate",
        help="For perpetuity growth terminal value",
        type=float,
        default=config.dcf.default_perpetual_growth_rate,
    )

    # API configuration
    parser.add_argument(
        "--apikey", help="API key for financialmodelingprep.com", default=config.api.api_key
    )

    # Cache management
    parser.add_argument(
        "--caching",
        help="Enable caching (use cache if available, fall back to API)",
        type=lambda x: x.lower() in ("true", "1", "yes", "on"),
        default=True,
    )
    parser.add_argument(
        "--no-caching",
        help="Disable caching (always fetch fresh data from API)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--clear-cache", help="Clear all cached data before running analysis", action="store_true"
    )
    parser.add_argument("--cache-info", help="Show cache information and exit", action="store_true")

    # Parse arguments
    args = parser.parse_args()

    return args


def show_cache_info() -> None:
    """Display cache information."""
    cache_service = CacheService()
    info = cache_service.get_cache_info()

    logger.info("Cache Information:")
    logger.info(f"Directory: {info['cache_directory']}")
    logger.info(f"Total files: {info['total_files']}")
    logger.info(f"Total size: {info['total_size_mb']} MB")
    logger.info("")

    if info["files"]:
        logger.info("Cached files:")
        for file_info in info["files"]:
            if "error" in file_info:
                logger.warning(f"  {file_info['file']}: {file_info['error']}")
            else:
                status = "✓" if file_info["is_valid"] else "✗"
                logger.info(
                    f"  {status} {file_info['file']} "
                    f"({file_info['ticker']} - {file_info['data_type']})"
                )
                logger.info(f"    Cached: {file_info['cached_at']}")
                logger.info(f"    Size: {file_info['size_bytes']} bytes")
    else:
        logger.info("No cached files found.")
