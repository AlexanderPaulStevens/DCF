"""
Error handling service for financial forecasting application.

This module centralizes all exception handling logic, providing consistent
error handling across the application.
"""

import sys
from typing import Callable, TypeVar

from app.exceptions import (
    ConfigurationError,
    DCFCalculationError,
    InvalidParameterError,
    VisualizationError,
)

T = TypeVar("T")


class ErrorHandler:
    """Service for handling application errors and exceptions."""

    @staticmethod
    def handle_application_errors(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to handle application errors consistently.

        Args:
            func: Function to wrap with error handling

        Returns:
            Wrapped function with error handling
        """

        def wrapper(*args: object, **kwargs: object) -> T:
            try:
                return func(*args, **kwargs)
            except (InvalidParameterError, DCFCalculationError, ConfigurationError) as e:
                print(f"Error: {e}")
                sys.exit(1)
            except (OSError, IOError) as e:
                print(f"System error: {e}")
                sys.exit(1)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Unexpected error: {e}")
                sys.exit(1)

        return wrapper

    @staticmethod
    def handle_validation_errors(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to handle validation errors.

        Args:
            func: Function to wrap with validation error handling

        Returns:
            Wrapped function with validation error handling
        """

        def wrapper(*args: object, **kwargs: object) -> T:
            try:
                return func(*args, **kwargs)
            except InvalidParameterError as e:
                print(f"Validation error: {e}")
                sys.exit(1)

        return wrapper

    @staticmethod
    def handle_visualization_errors(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to handle visualization errors.

        Args:
            func: Function to wrap with visualization error handling

        Returns:
            Wrapped function with visualization error handling
        """

        def wrapper(*args: object, **kwargs: object) -> T:
            try:
                return func(*args, **kwargs)
            except VisualizationError as e:
                print(f"Visualization error: {e}")
                return None

        return wrapper
