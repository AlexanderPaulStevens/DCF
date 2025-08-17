"""
Application service for orchestrating DCF analysis workflows.

This module provides the main application logic for running DCF analyses,
including single analysis and sensitivity analysis modes.
"""

import argparse
import logging

from app.custom_types import DCFParameters, DCFResults, SensitivityVariable
from app.exceptions import DCFCalculationError
from app.services.dcf_service import DCFService
from app.services.error_handler import ErrorHandler
from app.services.validation_service import ValidationService
from app.services.visualization_service import VisualizationService

# Configure logging for this module
logger = logging.getLogger(__name__)


class ApplicationService:
    """
    Main application service for DCF analysis workflows.

    This service orchestrates the complete DCF analysis process, including
    parameter validation, data fetching, calculations, and visualization.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        """
        Initialize the application service.

        Args:
            args: Command line arguments containing analysis parameters
        """
        self.args = args
        self.dcf_service = DCFService(args.apikey, args.caching)
        self.viz_service = VisualizationService()
        self.error_handler = ErrorHandler()

    def run_analysis(
        self, args: argparse.Namespace, validation_service: ValidationService
    ) -> DCFResults:
        """
        Run DCF analysis (single or sensitivity) based on parameters.

        Args:
            args: Command line arguments
            validation_service: Validation service instance

        Returns:
            DCF calculation results normalized with ticker as key

        Raises:
            DCFCalculationError: If analysis fails
        """
        try:
            # Create base DCF parameters
            params = self._create_dcf_parameters(args)

            if args.step_increase > 0:
                # Sensitivity analysis mode
                variable = validation_service.get_variable_for_sensitivity(args)
                dcfs = self._run_sensitivity_steps(args, variable)
                logger.info(f"Completed sensitivity analysis with {len(dcfs)} steps")
            else:
                # Single analysis mode
                dcfs = self.dcf_service.calculate_historical_dcf(params)
                logger.info("Completed single DCF analysis")

            # Normalize structure: wrap in ticker key for consistency with visualization service
            normalized_dcfs = {args.ticker: dcfs}

            # Display results
            self._display_results(args.ticker, dcfs)

            return normalized_dcfs

        except Exception as e:
            self.error_handler.handle_unexpected_error(e, "DCF analysis")
            raise DCFCalculationError(f"DCF analysis failed: {e}") from e

    def _run_sensitivity_steps(
        self, args: argparse.Namespace, variable: SensitivityVariable
    ) -> DCFResults:
        """
        Run sensitivity analysis steps for the specified variable.

        Args:
            args: Command line arguments
            variable: Variable to vary for sensitivity analysis

        Returns:
            DCF results for all sensitivity scenarios
        """
        base_value = self._get_variable_value(args, variable)
        step_increase = args.step_increase
        steps = args.steps

        logger.info(f"Running sensitivity analysis for {variable.value}")
        logger.info(f"Base value: {base_value}, Step: {step_increase}, Steps: {steps}")

        dcfs = {}

        for step in range(steps + 1):
            # Calculate new value for this step
            new_value = base_value + (step * step_increase)

            # Create step label
            step_label = self._create_step_label(variable, new_value)

            # Create parameters with modified value
            params = self._create_dcf_parameters_with_variable(args, variable, new_value)

            # Run DCF calculation
            step_dcfs = self.dcf_service.calculate_historical_dcf(params)

            # Store results with step label
            dcfs[step_label] = step_dcfs

            logger.info(f"Completed step {step + 1}/{steps + 1}: {step_label}")

        return dcfs

    def _get_variable_value(self, args: argparse.Namespace, variable: SensitivityVariable) -> float:
        """Get the current value of the specified variable from args."""
        try:
            value = getattr(args, variable.value)
            return float(value)
        except (AttributeError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid value for {variable.value}: {e}")

    def _create_step_label(self, variable: SensitivityVariable, value: float) -> str:
        """Create a descriptive step label."""
        return f"{variable.value}: {value:.3f}"

    def _create_dcf_parameters_with_variable(
        self, args: argparse.Namespace, variable: SensitivityVariable, new_value: float
    ) -> DCFParameters:
        """Create DCF parameters with the modified variable value."""
        # Create a copy of args to avoid mutating the original
        args_dict = vars(args).copy()
        args_dict[variable.value] = new_value

        # Create a new Namespace object with the modified values
        modified_args = argparse.Namespace(**args_dict)

        return self._create_dcf_parameters(modified_args)

    def _create_dcf_parameters(self, args: argparse.Namespace) -> DCFParameters:
        """
        Create DCF parameters from command line arguments.

        This method extracts and validates the key parameters needed for DCF analysis
        from the parsed command line arguments. It ensures all required parameters
        are properly formatted and available.

        Args:
            args: Parsed command line arguments

        Returns:
            DCFParameters object containing all required parameters for DCF calculation

        Required Parameters:
            - ticker: Company stock symbol
            - years: Historical period for analysis
            - forecast_years: Number of years to project forward
            - discount_rate: Rate for discounting future cash flows
            - earnings_growth_rate: Assumed growth rate in earnings
            - cap_ex_growth_rate: Assumed growth rate in capital expenditures
            - perpetual_growth_rate: Long-term growth rate for terminal value
            - interval: Data frequency (annual/quarterly)
            - api_key: API key for financial data
        """
        return DCFParameters(
            ticker=getattr(args, "ticker", ""),
            years=getattr(args, "years", 1),
            forecast_years=getattr(args, "period", 5),
            discount_rate=getattr(args, "discount_rate", 0.1),
            earnings_growth_rate=getattr(args, "earnings_growth_rate", 0.05),
            cap_ex_growth_rate=getattr(args, "cap_ex_growth_rate", 0.045),
            perpetual_growth_rate=getattr(args, "perpetual_growth_rate", 0.05),
            interval=getattr(args, "interval", "annual"),
            api_key=getattr(args, "apikey", None),
        )

    def run(self, validation_service: ValidationService, args: argparse.Namespace) -> None:
        """
        Main application execution logic for DCF analysis.

        This method orchestrates the complete DCF analysis workflow, including:
        1. Parameter validation
        2. Data fetching and caching
        3. DCF calculations (single or sensitivity analysis)
        4. Visualization generation
        5. Results presentation

        The method automatically determines whether to run a single DCF analysis
        or sensitivity analysis based on the provided parameters.

        Args:
            validation_service: Validation service instance
            args: Command line arguments containing all analysis parameters

        Analysis Modes:
        ---------------
        - **Single Analysis**: Standard DCF valuation with point estimates
        - **Sensitivity Analysis**: Multiple DCF calculations with varying parameters
          to understand valuation sensitivity to key assumptions

        Output:
        -------
        - Terminal output with key valuation metrics
        - Generated charts saved to 'app/imgs/' directory
        - Comprehensive DCF dashboard visualization
        """
        try:
            # Run DCF analysis (single or sensitivity)
            dcfs = self.run_analysis(args, validation_service)

            # Generate visualizations
            self.viz_service.generate_enhanced_visualizations(args.ticker, dcfs, args.period)

            logger.info("DCF analysis completed successfully")

        except Exception as e:
            self.error_handler.handle_unexpected_error(e, "main application execution")
            raise

    def _display_results(self, ticker: str, dcfs: DCFResults) -> None:
        """Display DCF calculation results."""
        try:
            if not dcfs:
                logger.warning(f"No DCF results to display for {ticker}")
                return

            # Get the most recent result
            latest_date = max(dcfs.keys())
            latest_result = dcfs[latest_date]

            logger.info(f"\nDCF Results for {ticker} ({latest_date}):")
            logger.info(f"Enterprise Value: ${latest_result.enterprise_value:,.2f}")
            logger.info(f"Equity Value: ${latest_result.equity_value:,.2f}")
            logger.info(f"Share Price: ${latest_result.share_price:.2f}")

        except (ValueError, KeyError, AttributeError) as e:
            logger.error(f"Error displaying results: {e}")
            # Don't raise - this is just display logic
