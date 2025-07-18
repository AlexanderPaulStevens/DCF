"""
Financial Forecasting Application.

This module provides the main entry point for the financial forecasting application
that performs DCF (Discounted Cash Flow) analysis on publicly traded companies.
"""

import argparse
import sys
from typing import Dict, Optional, Tuple

from config import config
from custom_types import DCFParameters, DCFResults
from exceptions import (
    ConfigurationError,
    DCFCalculationError,
    InvalidParameterError,
    VisualizationError,
)
from services.dcf_service import DCFService
from services.visualization_service import VisualizationService
from visualization.plot import visualize_bulk_historicals
from visualization.printouts import prettyprint


class FinancialForecastingApp:
    """Main application class for financial forecasting."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the application with services.

        Args:
            api_key: Optional API key for financial data services
        """
        self.dcf_service = DCFService(api_key)
        self.viz_service = VisualizationService()

    def run_sensitivity_analysis(
        self, args: argparse.Namespace, variable: str
    ) -> Tuple[Dict, DCFResults]:
        """
        Run sensitivity analysis with step increases.

        Args:
            args: Command line arguments
            variable: Variable to analyze

        Returns:
            Tuple of conditions and DCF results
        """
        dcfs: DCFResults = {}
        cond = {args.v: []}

        for increment in range(1, int(args.steps) + 1):
            # Calculate new variable value
            var_value = vars(args)[variable] * (1 + (args.s * increment))
            step_label = f"{args.v}: {str(var_value)[:4]}"

            cond[args.v].append(step_label)
            vars(args)[variable] = var_value

            # Create parameters and calculate DCF
            params = self._create_dcf_parameters(args)
            dcfs[step_label] = self.dcf_service.calculate_historical_dcf(params)

        return cond, dcfs

    def run_single_analysis(self, args: argparse.Namespace) -> Tuple[Dict, DCFResults]:
        """
        Run single DCF analysis.

        Args:
            args: Command line arguments

        Returns:
            Tuple of conditions and DCF results
        """
        cond = {"Ticker": [args.t]}
        params = self._create_dcf_parameters(args)
        dcfs = {args.t: self.dcf_service.calculate_historical_dcf(params)}
        return cond, dcfs

    def _create_dcf_parameters(self, args: argparse.Namespace) -> DCFParameters:
        """
        Create DCF parameters from command line arguments.

        Args:
            args: Command line arguments

        Returns:
            DCFParameters object with all required parameters
        """
        return DCFParameters(
            ticker=args.t,
            years=args.y,
            forecast_years=args.p,
            discount_rate=args.d,
            earnings_growth_rate=args.eg,
            cap_ex_growth_rate=args.cg,
            perpetual_growth_rate=args.pg,
            interval=args.i,
            api_key=args.apikey,
        )

    def _get_variable_mapping(self, variable: str) -> Optional[str]:
        """
        Map variable names to their internal representations.

        Args:
            variable: Variable name to map

        Returns:
            Mapped variable name or None if not found
        """
        variable_map = {
            "eg": "eg",
            "earnings_growth_rate": "eg",
            "cg": "cg",
            "cap_ex_growth_rate": "cg",
            "pg": "pg",
            "perpetual_growth_rate": "pg",
            "discount_rate": "discount",
            "discount": "discount",
        }
        return variable_map.get(variable)

    def _validate_sensitivity_parameters(self, args: argparse.Namespace) -> str:
        """
        Validate sensitivity analysis parameters.

        Args:
            args: Command line arguments

        Returns:
            Validated variable name

        Raises:
            InvalidParameterError: If parameters are invalid
        """
        if args.s <= 0:
            raise InvalidParameterError("Step increase must be greater than 0")

        if args.v is None:
            raise InvalidParameterError(
                "If step (--s) is > 0, you must specify the variable via --v"
            )

        variable = self._get_variable_mapping(args.v)
        if variable is None:
            raise InvalidParameterError(
                "Invalid variable. Must choose from: "
                "[earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, discount]"
            )

        return variable

    def _generate_visualizations(self, args: argparse.Namespace, dcfs: DCFResults) -> None:
        """
        Generate enhanced visualizations.

        Args:
            args: Command line arguments
            dcfs: DCF calculation results
        """
        print("\n" + "=" * 60)
        print("Generating Enhanced Visualizations...")
        print("=" * 60)

        if not dcfs or args.t not in dcfs or not dcfs[args.t]:
            print("Warning: No DCF results available for visualization")
            return

        try:
            # Create visualizations
            self.viz_service.create_comprehensive_visualization(args.t, dcfs[args.t], args.p)
            self.viz_service.create_terminal_style_output(args.t, dcfs[args.t], args.p)

            print("Visualizations created successfully!")
            print("Check the 'app/imgs/' directory for generated charts:")
            print(f"   - {args.t}_comprehensive_dcf.png (Main dashboard)")
            print("   - terminal_output.png (Terminal-style output)")

        except VisualizationError as e:
            print(f"Visualization error: {e}")

    def run(self, args: argparse.Namespace) -> None:
        """
        Main application execution logic.

        Args:
            args: Command line arguments
        """
        try:
            # Run DCF analysis
            if args.s > 0:
                variable = self._validate_sensitivity_parameters(args)
                cond, dcfs = self.run_sensitivity_analysis(args, variable)
            else:
                cond, dcfs = self.run_single_analysis(args)

            # Generate visualizations based on analysis type
            if args.y > 1:
                visualize_bulk_historicals(dcfs, args.t, cond, args.apikey)
            else:
                prettyprint(dcfs, args.y)

            # Generate enhanced visualizations
            self._generate_visualizations(args, dcfs)

        except (InvalidParameterError, DCFCalculationError, ConfigurationError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        except (OSError, IOError) as e:
            print(f"System error: {e}")
            sys.exit(1)
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


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
        "--p",
        "--period",
        help="Years to forecast",
        type=int,
        default=config.dcf.default_forecast_years,
    )
    parser.add_argument(
        "--t", "--ticker", help="Single ticker to do historical DCF", type=str, default="AAPL"
    )
    parser.add_argument(
        "--y",
        "--years",
        help="Number of years to compute DCF analysis for",
        type=int,
        default=config.dcf.default_years,
    )
    parser.add_argument(
        "--i",
        "--interval",
        help='Interval period for each calc, either "annual" or "quarter"',
        default=config.dcf.default_interval,
    )

    # Sensitivity analysis parameters
    parser.add_argument(
        "--s",
        "--step_increase",
        help="Step increase for sensitivity analysis",
        type=float,
        default=0,
    )
    parser.add_argument(
        "--steps", help="Steps to take if --s is > 0", default=config.dcf.default_steps
    )
    parser.add_argument(
        "--v",
        "--variable",
        help="Variable to increase for sensitivity analysis: [earnings_growth_rate, discount_rate]",
        default=None,
    )

    # DCF model parameters
    parser.add_argument(
        "--d",
        "--discount_rate",
        help="Discount rate for future cash flow to firm",
        type=float,
        default=config.dcf.default_discount_rate,
    )
    parser.add_argument(
        "--eg",
        "--earnings_growth_rate",
        help="Growth in revenue, YoY",
        type=float,
        default=config.dcf.default_earnings_growth_rate,
    )
    parser.add_argument(
        "--cg",
        "--cap_ex_growth_rate",
        help="Growth in cap_ex, YoY",
        type=float,
        default=config.dcf.default_cap_ex_growth_rate,
    )
    parser.add_argument(
        "--pg",
        "--perpetual_growth_rate",
        help="For perpetuity growth terminal value",
        type=float,
        default=config.dcf.default_perpetual_growth_rate,
    )

    # API configuration
    parser.add_argument(
        "--apikey", help="API key for financialmodelingprep.com", default=config.api.api_key
    )

    return parser


def validate_api_key(api_key: Optional[str]) -> None:
    """
    Validate that an API key is provided.

    Args:
        api_key: API key to validate

    Raises:
        SystemExit: If API key is not provided
    """
    if not api_key:
        print("Error: API key is required. Set APIKEY environment variable or use --apikey")
        sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Validate API key
    validate_api_key(args.apikey)

    # Create and run application
    app = FinancialForecastingApp(args.apikey)
    app.run(args)


if __name__ == "__main__":
    main()
