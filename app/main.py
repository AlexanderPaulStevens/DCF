"""
Financial Forecasting Application.

This module provides the main entry point for the financial forecasting application
that performs DCF (Discounted Cash Flow) analysis on publicly traded companies.

What is DCF Analysis?
=====================

DCF analysis values companies by estimating the present value of their future cash flows.
It's based on the principle that a company's value today is the sum of all its future
cash flows, discounted back to present value.

Required Parameters:
-------------------
- **--ticker**: Company stock symbol (e.g., AAPL, MSFT, GOOGL)
- **--apikey**: Financial Modeling Prep API key (or set $APIKEY environment variable)

Key Optional Parameters:
-----------------------
- **--period**: Years to forecast (default: 5)
- **--discount_rate**: Discount rate for future cash flows (default: 0.1)
- **--earnings_growth_rate**: Assumed earnings growth rate (default: 0.05)

Output:
--------
- Terminal output with key valuation metrics
- Generated charts saved to 'app/imgs/' directory
- Comprehensive DCF dashboard visualization

Data Sources:
-------------
- Financial statements from Financial Modeling Prep API
"""

import logging

from app.argument_parser import create_argument_parser, show_cache_info
from app.services.application_service import ApplicationService
from app.services.cache_service import CacheService
from app.services.validation_service import ValidationService

# Configure logging for the main application
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the application."""
    # Configure basic logging for the application
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    args = create_argument_parser()

    # Handle cache management commands
    if args.cache_info:
        show_cache_info()
        return

    # Handle cache clearing
    if args.clear_cache:
        logger.info("Clearing cache...")
        cache_service = CacheService()
        cache_service.clear_cache()
        logger.info("Cache cleared.")

    # Create services
    validation_service = ValidationService()

    # Validate all parameters early (fail fast principle)
    validation_service.validate_all_parameters(args)

    # Run application
    app = ApplicationService(args)
    app.run(validation_service, args)


if __name__ == "__main__":
    main()
