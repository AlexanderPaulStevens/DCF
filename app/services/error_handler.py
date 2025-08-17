"""
Error handling service for the financial forecasting application.

This module provides centralized error handling and logging for all application
components, ensuring consistent error reporting and debugging information.
"""

import logging
import traceback
from typing import Callable, Optional, TypeVar

from app.exceptions import (
    APIError,
    ConfigurationError,
    DataFetchError,
    DCFCalculationError,
    InvalidParameterError,
    VisualizationError,
)

# Configure logging for this module
logger = logging.getLogger(__name__)

# Type variable for generic function return type
T = TypeVar("T")


class ErrorHandler:
    """Centralized error handling service."""

    def __init__(self) -> None:
        """Initialize the error handler."""
        self.error_count = 0
        self.warning_count = 0

    def handle_api_error(self, error: APIError, context: str = "") -> None:
        """
        Handle API-related errors with appropriate logging and recovery.

        Args:
            error: The API error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        context_msg = f" in {context}" if context else ""
        logger.error(f"API error{context_msg}: {error}")

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"API error cause: {error.__cause__}")

    def handle_data_error(self, error: DataFetchError, context: str = "") -> None:
        """
        Handle data fetching errors with appropriate logging.

        Args:
            error: The data fetching error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        context_msg = f" in {context}" if context else ""
        logger.error(f"Data fetching error{context_msg}: {error}")

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Data error cause: {error.__cause__}")

    def handle_validation_error(self, error: InvalidParameterError, context: str = "") -> None:
        """
        Handle validation errors with appropriate logging.

        Args:
            error: The validation error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        context_msg = f" in {context}" if context else ""
        logger.error(f"Validation error{context_msg}: {error}")

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Validation error cause: {error.__cause__}")

    def handle_dcf_error(self, error: DCFCalculationError, context: str = "") -> None:
        """
        Handle DCF calculation errors with appropriate logging.

        Args:
            error: The DCF calculation error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        context_msg = f" in {context}" if context else ""
        logger.error(f"DCF calculation error{context_msg}: {error}")

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"DCF error cause: {error.__cause__}")

    def handle_visualization_error(self, error: VisualizationError, context: str = "") -> None:
        """
        Handle visualization errors with appropriate logging.

        Args:
            error: The visualization error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        context_msg = f" in {context}" if context else ""
        logger.error(f"Visualization error{context_msg}: {error}")

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Visualization error cause: {error.__cause__}")

    def handle_configuration_error(self, error: ConfigurationError, context: str = "") -> None:
        """
        Handle configuration errors with appropriate logging.

        Args:
            error: The configuration error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        context_msg = f" in {context}" if context else ""
        logger.error(f"Configuration error{context_msg}: {error}")

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Configuration error cause: {error.__cause__}")

    def handle_unexpected_error(self, error: Exception, context: str = "") -> None:
        """
        Handle unexpected errors with appropriate logging.

        Args:
            error: The unexpected error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        context_msg = f" in {context}" if context else ""
        logger.error(f"Unexpected error{context_msg}: {error}")
        logger.debug(f"Unexpected error traceback: {traceback.format_exc()}")

    def safe_execute(
        self, func: Callable[..., T], *args: object, context: str = "", **kwargs: object
    ) -> Optional[T]:
        """
        Safely execute a function with comprehensive error handling.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            context: Context string for error reporting
            **kwargs: Keyword arguments for the function

        Returns:
            Function result if successful, None if error occurred
        """
        try:
            return func(*args, **kwargs)
        except APIError as e:
            self.handle_api_error(e, context)
        except DataFetchError as e:
            self.handle_data_error(e, context)
        except InvalidParameterError as e:
            self.handle_validation_error(e, context)
        except DCFCalculationError as e:
            self.handle_dcf_error(e, context)
        except VisualizationError as e:
            self.handle_visualization_error(e, context)
        except ConfigurationError as e:
            self.handle_configuration_error(e, context)
        except (ValueError, TypeError, AttributeError, RuntimeError) as e:
            self.handle_unexpected_error(e, context)

        return None

    def get_error_summary(self) -> dict:
        """
        Get a summary of errors and warnings encountered.

        Returns:
            Dictionary with error and warning counts
        """
        return {
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "total_issues": self.error_count + self.warning_count,
        }

    def reset_counts(self) -> None:
        """Reset error and warning counts."""
        self.error_count = 0
        self.warning_count = 0
