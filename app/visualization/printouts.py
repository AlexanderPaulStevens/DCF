"""
Pretty print utilities for DCF analysis results.

This module provides formatted output functions for displaying DCF calculation
results in a human-readable format.
"""

import logging
from typing import Any, Dict

# Configure logging for this module
logger = logging.getLogger(__name__)


def prettyprint(dcfs: Dict[str, Any], years: int) -> None:
    """
    Pretty print-out results of a DCF query.
    Handles formatting for all output variations.

    Args:
        dcfs: Dictionary containing DCF results
        years: Number of years in the analysis
    """
    if years > 1:
        for k, v in dcfs.items():
            logger.info(f"ticker: {k}")
            if len(v.keys()) > 1:
                for yr, dcf in v.items():
                    logger.info(f"date: {yr} \nvalue: {dcf}")
    else:
        for k, v in dcfs.items():
            logger.info(f"ticker: {k} \nvalue: {v}")
