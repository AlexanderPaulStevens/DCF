"""
Validation service for financial forecasting application.

This module handles all parameter validation logic, following software engineering
principles for robust input validation and error handling.
"""

import argparse
from typing import Dict, Optional, Union

from app.custom_types import SensitivityVariable
from app.exceptions import InvalidParameterError


class ValidationService:
    """
    Service for validating application parameters and inputs.

    Follows software engineering principles:
    - Single Responsibility: Only handles validation
    - Fail Fast: Validates critical parameters early
    - Comprehensive: Validates all aspects of input
    - User-Friendly: Provides clear error messages
    """

    def __init__(self) -> None:
        """Initialize the validation service."""
        self._variable_mapping = {
            "eg": SensitivityVariable.EARNINGS_GROWTH_RATE,
            "earnings_growth_rate": SensitivityVariable.EARNINGS_GROWTH_RATE,
            "cg": SensitivityVariable.CAP_EX_GROWTH_RATE,
            "cap_ex_growth_rate": SensitivityVariable.CAP_EX_GROWTH_RATE,
            "pg": SensitivityVariable.PERPETUAL_GROWTH_RATE,
            "perpetual_growth_rate": SensitivityVariable.PERPETUAL_GROWTH_RATE,
            "discount_rate": SensitivityVariable.DISCOUNT_RATE,
            "discount": SensitivityVariable.DISCOUNT_RATE,
        }

        # Business logic constraints
        self._constraints = {
            "period": {"min": 1, "max": 20, "description": "Forecast period"},
            "years": {"min": 1, "max": 10, "description": "Historical years"},
            "discount_rate": {"min": 0.01, "max": 0.50, "description": "Discount rate"},
            "earnings_growth_rate": {
                "min": -0.50,
                "max": 1.0,
                "description": "Earnings growth rate",
            },
            "cap_ex_growth_rate": {
                "min": -0.50,
                "max": 1.0,
                "description": "Capital expenditure growth rate",
            },
            "perpetual_growth_rate": {
                "min": 0.0,
                "max": 0.10,
                "description": "Perpetual growth rate",
            },
            "step_increase": {"min": 0.001, "max": 1.0, "description": "Step increase"},
            "steps": {"min": 1, "max": 50, "description": "Number of steps"},
        }

    def validate_all_parameters(self, args: argparse.Namespace) -> None:
        """
        Comprehensive validation of all parameters.

        This method follows the "fail fast" principle by validating all critical
        parameters before any processing begins.

        Args:
            args: Command line arguments

        Raises:
            InvalidParameterError: If any validation fails
        """
        # Validate in order of criticality
        self._validate_critical_parameters(args)
        self._validate_business_constraints(args)
        self._validate_sensitivity_parameters_if_needed(args)

    def _validate_critical_parameters(self, args: argparse.Namespace) -> None:
        """Validate critical parameters that must exist and be valid."""
        # API key validation
        if not args.apikey:
            raise InvalidParameterError(
                "API key is required. Set APIKEY environment variable or use --apikey"
            )

        # Ticker validation
        if not args.ticker or not isinstance(args.ticker, str):
            raise InvalidParameterError("Ticker symbol is required and must be a string")

        if len(args.ticker) > 10:  # Reasonable max length for ticker
            raise InvalidParameterError("Ticker symbol is too long")

        # Interval validation
        if args.interval not in ["annual", "quarter"]:
            raise InvalidParameterError("Interval must be either 'annual' or 'quarter'")

    def _validate_business_constraints(self, args: argparse.Namespace) -> None:
        """Validate business logic constraints for numeric parameters."""
        # Check if we're doing sensitivity analysis
        is_sensitivity_analysis = getattr(args, "step_increase", 0) > 0

        for param_name, constraint in self._constraints.items():
            if hasattr(args, param_name):
                value = getattr(args, param_name)
                if value is not None:
                    # Skip sensitivity parameters if not doing sensitivity analysis
                    if param_name in ["step_increase", "steps"] and not is_sensitivity_analysis:
                        continue

                    # For step_increase, allow 0 (which means no sensitivity analysis)
                    if param_name == "step_increase" and value == 0:
                        continue

                    self._validate_numeric_constraint(value, constraint)

    def _validate_numeric_constraint(
        self, value: Union[float, str], constraint: Dict[str, Union[str, float]]
    ) -> None:
        """Validate a single numeric parameter against its constraints."""
        try:
            # Convert to float for validation
            numeric_value = float(value)
        except (ValueError, TypeError):
            raise InvalidParameterError(
                f"{constraint['description']} must be a valid number, got: {value}"
            )

        min_val = constraint["min"]
        max_val = constraint["max"]

        if numeric_value < min_val or numeric_value > max_val:
            raise InvalidParameterError(
                f"{constraint['description']} must be between {min_val} and {max_val}, "
                f"got: {numeric_value}"
            )

    def _validate_sensitivity_parameters_if_needed(self, args: argparse.Namespace) -> None:
        """Validate sensitivity analysis parameters if they're being used."""
        if hasattr(args, "step_increase") and args.step_increase > 0:
            self._validate_sensitivity_setup(args)

    def _validate_sensitivity_setup(self, args: argparse.Namespace) -> None:
        """Validate that sensitivity analysis is properly configured."""
        if args.variable is None:
            raise InvalidParameterError(
                "For sensitivity analysis, you must specify --variable when --step_increase > 0"
            )

        variable = self._get_variable_mapping(args.variable)
        if variable is None:
            valid_variables = [var.value for var in SensitivityVariable]
            raise InvalidParameterError(
                f"Invalid variable '{args.variable}'. Must choose from: {valid_variables}"
            )

    def get_variable_for_sensitivity(self, args: argparse.Namespace) -> SensitivityVariable:
        """
        Get the validated variable name for sensitivity analysis.

        This method should only be called after validation is complete.

        Args:
            args: Command line arguments

        Returns:
            Validated SensitivityVariable enum value

        Raises:
            InvalidParameterError: If variable is not properly configured
        """
        if not hasattr(args, "variable") or args.variable is None:
            raise InvalidParameterError("Variable not specified for sensitivity analysis")

        variable = self._get_variable_mapping(args.variable)
        if variable is None:
            raise InvalidParameterError(f"Invalid variable: {args.variable}")

        return variable

    def _get_variable_mapping(self, variable: str) -> Optional[SensitivityVariable]:
        """
        Map variable names to their internal representations.

        Args:
            variable: Variable name to map

        Returns:
            Mapped SensitivityVariable enum value or None if not found
        """
        return self._variable_mapping.get(variable)

    # Legacy methods for backward compatibility
    def validate_api_key(self, api_key: Optional[str]) -> None:
        """Legacy method - use validate_all_parameters instead."""
        if not api_key:
            raise InvalidParameterError(
                "API key is required. Set APIKEY environment variable or use --apikey"
            )

    def validate_dcf_parameters(self, args: argparse.Namespace) -> None:
        """Legacy method - use validate_all_parameters instead."""
        self._validate_business_constraints(args)

    def validate_sensitivity_parameters(self, args: argparse.Namespace) -> str:
        """Legacy method - use get_variable_for_sensitivity instead."""
        if args.step_increase <= 0:
            raise InvalidParameterError("Step increase must be greater than 0")

        return self.get_variable_for_sensitivity(args)
