"""
Application Service for Financial Forecasting.

This module contains the main application logic for the financial forecasting application,
including sensitivity analysis and orchestration of services.
"""

import argparse
from typing import Dict, Optional, Tuple

from app.custom_types import DCFParameters, DCFResults
from app.services.dcf_service import DCFService
from app.services.error_handler import ErrorHandler
from app.services.validation_service import ValidationService
from app.services.visualization_service import VisualizationService
from app.visualization.plot import visualize_bulk_historicals
from app.visualization.printouts import prettyprint


class ApplicationService:
    """Service for orchestrating the financial forecasting application."""

    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True) -> None:
        """
        Initialize the application service with required services.

        Args:
            api_key: Optional API key for financial data services
            use_cache: Whether to use caching (default: True)
        """
        self.dcf_service = DCFService(api_key, use_cache)
        self.viz_service = VisualizationService()
        self.validation_service = ValidationService()
        self.error_handler = ErrorHandler()

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
        cond = {args.variable: []}

        for increment in range(1, int(args.steps) + 1):
            # Calculate new variable value
            var_value = vars(args)[variable] * (1 + (args.step_increase * increment))
            step_label = f"{args.variable}: {str(var_value)[:4]}"

            cond[args.variable].append(step_label)
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
        cond = {"Ticker": [args.ticker]}
        params = self._create_dcf_parameters(args)
        dcfs = {args.ticker: self.dcf_service.calculate_historical_dcf(params)}
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
            ticker=args.ticker,
            years=args.years,
            forecast_years=args.period,
            discount_rate=args.discount_rate,
            earnings_growth_rate=args.earnings_growth_rate,
            cap_ex_growth_rate=args.cap_ex_growth_rate,
            perpetual_growth_rate=args.perpetual_growth_rate,
            interval=args.interval,
            api_key=args.apikey,
        )

    @ErrorHandler.handle_application_errors
    def run(self, args: argparse.Namespace) -> None:
        """
        Main application execution logic.

        Args:
            args: Command line arguments
        """
        # Validate parameters
        self.validation_service.validate_api_key(args.apikey)
        self.validation_service.validate_dcf_parameters(args)

        # Run DCF analysis
        if args.step_increase > 0:
            variable = self.validation_service.validate_sensitivity_parameters(args)
            cond, dcfs = self.run_sensitivity_analysis(args, variable)
        else:
            cond, dcfs = self.run_single_analysis(args)

        # Generate visualizations based on analysis type
        if args.years > 1:
            visualize_bulk_historicals(dcfs, args.ticker, cond, args.apikey)
        else:
            prettyprint(dcfs, args.years)

        # Generate enhanced visualizations using the visualization service
        self.viz_service.generate_enhanced_visualizations(args.ticker, dcfs, args.period)
