"""
Validation service for financial forecasting application.

This module handles all parameter validation logic, separating validation concerns
from the main application service.
"""

import argparse
from typing import Optional

from app.exceptions import InvalidParameterError


class ValidationService:
    """Service for validating application parameters and inputs."""

    def __init__(self) -> None:
        """Initialize the validation service."""
        self._variable_mapping = {
            "eg": "eg",
            "earnings_growth_rate": "eg",
            "cg": "cg",
            "cap_ex_growth_rate": "cg",
            "pg": "pg",
            "perpetual_growth_rate": "pg",
            "discount_rate": "discount",
            "discount": "discount",
        }

    def validate_api_key(self, api_key: Optional[str]) -> None:
        """
        Validate that an API key is provided.

        Args:
            api_key: API key to validate

        Raises:
            InvalidParameterError: If API key is not provided
        """
        if not api_key:
            raise InvalidParameterError(
                "API key is required. Set APIKEY environment variable or use --apikey"
            )

    def validate_sensitivity_parameters(self, args: argparse.Namespace) -> str:
        """
        Validate sensitivity analysis parameters.

        Args:
            args: Command line arguments

        Returns:
            Validated variable name

        Raises:
            InvalidParameterError: If parameters are invalid
        """
        # Ensure step_increase is properly typed
        try:
            step_increase = (
                float(args.step_increase)
                if isinstance(args.step_increase, str)
                else args.step_increase
            )
        except (ValueError, TypeError) as e:
            raise InvalidParameterError(f"Invalid step_increase parameter: {e}")

        if step_increase <= 0:
            raise InvalidParameterError("Step increase must be greater than 0")

        if args.variable is None:
            raise InvalidParameterError(
                "If step (--step_increase) is > 0, you must specify the variable via --variable"
            )

        variable = self._get_variable_mapping(args.variable)
        if variable is None:
            raise InvalidParameterError(
                "Invalid variable. Must choose from: "
                "[earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, discount]"
            )

        return variable

    def validate_dcf_parameters(self, args: argparse.Namespace) -> None:
        """
        Validate DCF calculation parameters.

        Args:
            args: Command line arguments

        Raises:
            InvalidParameterError: If parameters are invalid
        """
        # Ensure numeric parameters are properly typed
        try:
            period = int(args.period) if isinstance(args.period, str) else args.period
            years = int(args.years) if isinstance(args.years, str) else args.years
            discount_rate = (
                float(args.discount_rate)
                if isinstance(args.discount_rate, str)
                else args.discount_rate
            )
            steps = int(args.steps) if isinstance(args.steps, str) else args.steps
        except (ValueError, TypeError) as e:
            raise InvalidParameterError(f"Invalid numeric parameter: {e}")

        if period <= 0:
            raise InvalidParameterError("Forecast period must be greater than 0")

        if years <= 0:
            raise InvalidParameterError("Years must be greater than 0")

        if discount_rate <= 0:
            raise InvalidParameterError("Discount rate must be greater than 0")

        if args.interval not in ["annual", "quarter"]:
            raise InvalidParameterError("Interval must be either 'annual' or 'quarter'")

        if steps <= 0:
            raise InvalidParameterError("Steps must be greater than 0")

    def _get_variable_mapping(self, variable: str) -> Optional[str]:
        """
        Map variable names to their internal representations.

        Args:
            variable: Variable name to map

        Returns:
            Mapped variable name or None if not found
        """
        return self._variable_mapping.get(variable)
