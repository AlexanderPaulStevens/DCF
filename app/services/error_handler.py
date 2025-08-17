"""
Error handling service for the financial forecasting application.

This module provides centralized error handling and logging for all application
components, ensuring consistent error reporting and debugging information.
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional, TypeVar

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
        self.error_contexts: Dict[str, int] = {}
        self.last_error: Optional[Exception] = None

    def handle_api_error(self, error: APIError, context: str = "") -> None:
        """
        Handle API-related errors with appropriate logging and recovery.

        Args:
            error: The API error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        self.last_error = error
        context_msg = f" in {context}" if context else ""

        logger.error(f"API error{context_msg}: {error}")
        self._track_error_context("API", context)

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"API error cause: {error.__cause__}")

        # Log stack trace for debugging
        logger.debug(f"API error stack trace: {traceback.format_exc()}")

    def handle_data_error(self, error: DataFetchError, context: str = "") -> None:
        """
        Handle data fetching errors with appropriate logging.

        Args:
            error: The data fetching error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        self.last_error = error
        context_msg = f" in {context}" if context else ""

        logger.error(f"Data fetching error{context_msg}: {error}")
        self._track_error_context("Data", context)

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Data error cause: {error.__cause__}")

        # Log stack trace for debugging
        logger.debug(f"Data error stack trace: {traceback.format_exc()}")

    def handle_validation_error(self, error: InvalidParameterError, context: str = "") -> None:
        """
        Handle validation errors with appropriate logging.

        Args:
            error: The validation error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        self.last_error = error
        context_msg = f" in {context}" if context else ""

        logger.error(f"Validation error{context_msg}: {error}")
        self._track_error_context("Validation", context)

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Validation error cause: {error.__cause__}")

        # Log stack trace for debugging
        logger.debug(f"Validation error stack trace: {traceback.format_exc()}")

    def handle_dcf_error(self, error: DCFCalculationError, context: str = "") -> None:
        """
        Handle DCF calculation errors with appropriate logging.

        Args:
            error: The DCF calculation error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        self.last_error = error
        context_msg = f" in {context}" if context else ""

        logger.error(f"DCF calculation error{context_msg}: {error}")
        self._track_error_context("DCF", context)

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"DCF error cause: {error.__cause__}")

        # Log stack trace for debugging
        logger.debug(f"DCF error stack trace: {traceback.format_exc()}")

    def handle_visualization_error(self, error: VisualizationError, context: str = "") -> None:
        """
        Handle visualization errors with appropriate logging.

        Args:
            error: The visualization error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        self.last_error = error
        context_msg = f" in {context}" if context else ""

        logger.error(f"Visualization error{context_msg}: {error}")
        self._track_error_context("Visualization", context)

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Visualization error cause: {error.__cause__}")

        # Log stack trace for debugging
        logger.debug(f"Visualization error stack trace: {traceback.format_exc()}")

    def handle_configuration_error(self, error: ConfigurationError, context: str = "") -> None:
        """
        Handle configuration errors with appropriate logging.

        Args:
            error: The configuration error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        self.last_error = error
        context_msg = f" in {context}" if context else ""

        logger.error(f"Configuration error{context_msg}: {error}")
        self._track_error_context("Configuration", context)

        # Log additional context for debugging
        if hasattr(error, "__cause__") and error.__cause__:
            logger.debug(f"Configuration error cause: {error.__cause__}")

        # Log stack trace for debugging
        logger.debug(f"Configuration error stack trace: {traceback.format_exc()}")

    def handle_unexpected_error(self, error: Exception, context: str = "") -> None:
        """
        Handle unexpected errors with appropriate logging.

        Args:
            error: The unexpected error that occurred
            context: Additional context about where the error occurred
        """
        self.error_count += 1
        self.last_error = error
        context_msg = f" in {context}" if context else ""

        logger.error(f"Unexpected error{context_msg}: {error}")
        self._track_error_context("Unexpected", context)

        # Log detailed error information
        logger.debug(f"Unexpected error type: {type(error).__name__}")
        logger.debug(f"Unexpected error traceback: {traceback.format_exc()}")

    def handle_warning(self, message: str, context: str = "") -> None:
        """
        Handle warnings with appropriate logging.

        Args:
            message: Warning message
            context: Additional context about where the warning occurred
        """
        self.warning_count += 1
        context_msg = f" in {context}" if context else ""

        logger.warning(f"Warning{context_msg}: {message}")
        self._track_error_context("Warning", context)

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
        except (OSError, ImportError, MemoryError) as e:
            # Catch specific system-level errors
            logger.error(f"System error {type(e).__name__} in {context}: {e}")
            self.handle_unexpected_error(e, context)

        return None

    def _track_error_context(self, error_type: str, context: str) -> None:
        """
        Track error context for analysis and reporting.

        Args:
            error_type: Type of error that occurred
            context: Context where the error occurred
        """
        context_key = f"{error_type}:{context}" if context else error_type
        self.error_contexts[context_key] = self.error_contexts.get(context_key, 0) + 1

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of errors and warnings encountered.

        Returns:
            Dictionary with detailed error and warning information
        """
        return {
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "total_issues": self.error_count + self.warning_count,
            "error_contexts": self.error_contexts.copy(),
            "last_error": str(self.last_error) if self.last_error else None,
            "last_error_type": type(self.last_error).__name__ if self.last_error else None,
        }

    def reset_counts(self) -> None:
        """Reset error and warning counts and clear error tracking."""
        self.error_count = 0
        self.warning_count = 0
        self.error_contexts.clear()
        self.last_error = None

    def has_errors(self) -> bool:
        """
        Check if any errors have occurred.

        Returns:
            True if errors exist, False otherwise
        """
        return self.error_count > 0

    def has_warnings(self) -> bool:
        """
        Check if any warnings have occurred.

        Returns:
            True if warnings exist, False otherwise
        """
        return self.warning_count > 0

    def get_error_context_summary(self) -> Dict[str, int]:
        """
        Get a summary of errors by context.

        Returns:
            Dictionary mapping error contexts to their counts
        """
        return self.error_contexts.copy()
