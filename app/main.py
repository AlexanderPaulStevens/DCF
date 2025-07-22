"""
Financial Forecasting Application.

This module provides the main entry point for the financial forecasting application
that performs DCF (Discounted Cash Flow) analysis on publicly traded companies.
"""

import argparse

from app.config import config
from app.services.application_service import ApplicationService
from app.services.cache_service import CacheService
from app.services.validation_service import ValidationService


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        Configured argument parser
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
        "--no-cache", help="Disable caching (fetch fresh data from API)", action="store_true"
    )
    parser.add_argument(
        "--clear-cache", help="Clear all cached data before running analysis", action="store_true"
    )
    parser.add_argument("--cache-info", help="Show cache information and exit", action="store_true")

    return parser


def show_cache_info() -> None:
    """Display cache information."""
    cache_service = CacheService()
    info = cache_service.get_cache_info()

    print("Cache Information:")
    print(f"Directory: {info['cache_directory']}")
    print(f"Total files: {info['total_files']}")
    print(f"Total size: {info['total_size_mb']} MB")
    print()

    if info["files"]:
        print("Cached files:")
        for file_info in info["files"]:
            if "error" in file_info:
                print(f"  {file_info['file']}: {file_info['error']}")
            else:
                status = "✓" if file_info["is_valid"] else "✗"
                print(
                    f"  {status} {file_info['file']} "
                    f"({file_info['ticker']} - {file_info['data_type']})"
                )
                print(f"    Cached: {file_info['cached_at']}")
                print(f"    Size: {file_info['size_bytes']} bytes")
    else:
        print("No cached files found.")


def main() -> None:
    """Main entry point for the application."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Handle cache management commands
    if args.cache_info:
        show_cache_info()
        return

    # Create services
    validation_service = ValidationService()
    use_cache = not args.no_cache  # Invert the no-cache flag
    app = ApplicationService(args.apikey, use_cache)

    # Validate API key
    validation_service.validate_api_key(args.apikey)

    # Handle cache clearing
    if args.clear_cache:
        print("Clearing cache...")
        cache_service = CacheService()
        cache_service.clear_cache()
        print("Cache cleared.")

    # Run application
    app.run(args)


if __name__ == "__main__":
    main()
