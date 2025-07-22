"""
Visualization service for DCF analysis results.
"""

import os
from datetime import datetime

import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from app.config import config
from app.custom_types import DCFResult, DCFResults, VisualizationData
from app.exceptions import VisualizationError


class VisualizationService:
    """Service for handling DCF visualization generation."""

    def __init__(self) -> None:
        """Initialize the visualization service."""
        self._setup_plotting_style()

    def _setup_plotting_style(self) -> None:
        """Set up the plotting style and configuration."""
        plt.style.use(config.visualization.style)
        sns.set_palette(config.visualization.color_palette)

    def generate_enhanced_visualizations(
        self, ticker: str, dcf_results: DCFResults, forecast_years: int
    ) -> None:
        """
        Generate enhanced visualizations with user feedback.

        Args:
            ticker: Company ticker symbol
            dcf_results: DCF calculation results
            forecast_years: Number of forecast years

        Raises:
            VisualizationError: If visualization generation fails
        """
        print("\n" + "=" * 60)
        print("Generating Enhanced Visualizations...")
        print("=" * 60)

        if not dcf_results or ticker not in dcf_results or not dcf_results[ticker]:
            print("Warning: No DCF results available for visualization")
            return

        try:
            # Create visualizations
            self.create_comprehensive_visualization(ticker, dcf_results[ticker], forecast_years)
            self.create_terminal_style_output(ticker, dcf_results[ticker], forecast_years)

            print("Visualizations created successfully!")
            print("Check the 'app/imgs/' directory for generated charts:")
            print(f"   - {ticker}_comprehensive_dcf.png (Main dashboard)")
            print("   - terminal_output.png (Terminal-style output)")

        except Exception as e:
            print(f"Visualization error: {e}")
            raise VisualizationError(f"Failed to generate visualizations: {e}") from e

    def create_comprehensive_visualization(
        self, ticker: str, dcf_results: DCFResults, forecast_years: int
    ) -> str:
        """
        Create a comprehensive DCF visualization dashboard.

        Args:
            ticker: Company ticker symbol
            dcf_results: DCF calculation results
            forecast_years: Number of forecast years

        Returns:
            Path to the generated visualization file

        Raises:
            VisualizationError: If visualization creation fails
        """
        try:
            # Extract the most recent DCF result
            if not dcf_results:
                raise VisualizationError("No DCF results available for visualization")

            first_result = next(iter(dcf_results.values()))
            viz_data = VisualizationData(
                ticker=ticker,
                enterprise_value=first_result.enterprise_value,
                equity_value=first_result.equity_value,
                share_price=first_result.share_price,
                forecast_years=forecast_years,
            )

            # Create the visualization
            self._create_dashboard(viz_data)

            # Save the file
            output_path = os.path.join(
                config.visualization.output_directory, f"{ticker}_comprehensive_dcf.png"
            )
            plt.savefig(output_path, dpi=config.visualization.dpi, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            raise VisualizationError(f"Failed to create comprehensive visualization: {e}") from e

    def create_terminal_style_output(
        self, ticker: str, dcf_results: DCFResults, forecast_years: int
    ) -> str:
        """
        Create a terminal-style output visualization.

        Args:
            ticker: Company ticker symbol
            dcf_results: DCF calculation results
            forecast_years: Number of forecast years

        Returns:
            Path to the generated visualization file

        Raises:
            VisualizationError: If visualization creation fails
        """
        try:
            if not dcf_results:
                raise VisualizationError("No DCF results available for visualization")

            first_result = next(iter(dcf_results.values()))
            viz_data = VisualizationData(
                ticker=ticker,
                enterprise_value=first_result.enterprise_value,
                equity_value=first_result.equity_value,
                share_price=first_result.share_price,
                forecast_years=forecast_years,
            )

            # Create terminal-style output
            self._create_terminal_output(viz_data)

            # Save the file
            output_path = os.path.join(config.visualization.output_directory, "terminal_output.png")
            plt.savefig(output_path, dpi=config.visualization.dpi, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            raise VisualizationError(f"Failed to create terminal-style output: {e}") from e

    def _create_dashboard(self, viz_data: VisualizationData) -> None:
        """
        Create the main dashboard with multiple subplots.

        Args:
            viz_data: Visualization data containing DCF results
        """
        fig, axes = plt.subplots(2, 3, figsize=config.visualization.figure_size)
        fig.suptitle(f"DCF Analysis Dashboard - {viz_data.ticker}", fontsize=16, fontweight="bold")

        # Create each subplot
        self._create_summary_dashboard(axes[0, 0], viz_data)
        self._create_value_breakdown(axes[0, 1], viz_data)
        self._create_cash_flow_projection(axes[0, 2], viz_data)
        self._create_sensitivity_analysis(axes[1, 0], viz_data)
        self._create_valuation_metrics(axes[1, 1], viz_data)
        self._create_risk_assessment(axes[1, 2])

        plt.tight_layout()

    def _create_summary_dashboard(
        self, ax: matplotlib.axes.Axes, viz_data: VisualizationData
    ) -> None:
        """
        Create the main summary dashboard.

        Args:
            ax: Matplotlib axis object
            viz_data: Visualization data containing DCF results
        """
        # Format values for display
        ev_formatted = f"${viz_data.enterprise_value / 1e12:.2f}T"
        equity_formatted = f"${viz_data.equity_value / 1e12:.2f}T"
        price_formatted = f"${viz_data.share_price:.2f}"

        # Create summary text
        summary_text = f"""
        DCF Analysis Summary

        Company: {viz_data.ticker}

        Enterprise Value: {ev_formatted}
        Equity Value: {equity_formatted}
        Per Share Value: {price_formatted}

        Analysis Date: {self._get_current_date()}
        """

        ax.text(
            0.1,
            0.9,
            summary_text,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox={"boxstyle": "round", "facecolor": "lightblue", "alpha": 0.8},
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title("DCF Analysis Summary", fontsize=14, fontweight="bold")

    def _create_value_breakdown(
        self, ax: matplotlib.axes.Axes, viz_data: VisualizationData
    ) -> None:
        """
        Create value breakdown chart.

        Args:
            ax: Matplotlib axis object
            viz_data: Visualization data containing DCF results
        """
        # Calculate components
        debt_cash_adjustment = viz_data.enterprise_value - viz_data.equity_value

        labels = ["Enterprise Value", "Debt & Cash\nAdjustment", "Equity Value"]
        sizes = [viz_data.enterprise_value, debt_cash_adjustment, viz_data.equity_value]
        colors = ["#ff9999", "#66b3ff", "#99ff99"]

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
        )

        # Format the percentage labels
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title("Value Breakdown", fontsize=14, fontweight="bold")

    def _create_cash_flow_projection(
        self, ax: matplotlib.axes.Axes, viz_data: VisualizationData
    ) -> None:
        """
        Create cash flow projection chart.

        Args:
            ax: Matplotlib axis object
            viz_data: Visualization data containing DCF results
        """
        # Sample cash flow data (could be made configurable or calculated)
        years = list(range(1, viz_data.forecast_years + 1))
        dfcf = [9.72e10, 9.51e10, 9.80e10, 1.06e11, 1.20e11]
        ebit = [1.29e11, 1.42e11, 1.64e11, 1.96e11, 2.45e11]

        x = np.arange(len(years))
        width = 0.35

        ax.bar(
            x - width / 2,
            [val / 1e10 for val in dfcf],
            width,
            label="Discounted FCF",
            color="skyblue",
            alpha=0.8,
        )
        ax.bar(
            x + width / 2,
            [val / 1e10 for val in ebit],
            width,
            label="EBIT",
            color="lightcoral",
            alpha=0.8,
        )

        ax.set_xlabel("Forecast Year")
        ax.set_ylabel("Value ($10B)")
        ax.set_title(f"{viz_data.forecast_years}-Year Cash Flow Projection")
        ax.set_xticks(x)
        ax.set_xticklabels([f"202{5 + i}" for i in range(viz_data.forecast_years)])
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _create_sensitivity_analysis(
        self, ax: matplotlib.axes.Axes, viz_data: VisualizationData
    ) -> None:
        """
        Create sensitivity analysis chart.

        Args:
            ax: Matplotlib axis object
            viz_data: Visualization data containing DCF results
        """
        # Create sensitivity matrix
        growth_rates = np.linspace(0.02, 0.08, 7)  # 2% to 8%
        discount_rates = np.linspace(0.08, 0.15, 8)  # 8% to 15%

        # Create a simple sensitivity matrix
        sensitivity_matrix = np.zeros((len(growth_rates), len(discount_rates)))

        for i, growth in enumerate(growth_rates):
            for j, discount in enumerate(discount_rates):
                # Simplified sensitivity calculation
                sensitivity_matrix[i, j] = viz_data.share_price * (1 + growth) / (1 + discount)

        # Create heatmap
        im = ax.imshow(sensitivity_matrix, cmap="RdYlGn", aspect="auto")

        # Set labels
        ax.set_xticks(range(len(discount_rates)))
        ax.set_yticks(range(len(growth_rates)))
        ax.set_xticklabels([f"{d:.1%}" for d in discount_rates])
        ax.set_yticklabels([f"{g:.1%}" for g in growth_rates])

        ax.set_xlabel("Discount Rate")
        ax.set_ylabel("Growth Rate")
        ax.set_title("Sensitivity Analysis\n(Share Price)")

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Share Price ($)")

    def _create_valuation_metrics(
        self, ax: matplotlib.axes.Axes, viz_data: VisualizationData
    ) -> None:
        """
        Create valuation metrics comparison.

        Args:
            ax: Matplotlib axis object
            viz_data: Visualization data containing DCF results
        """
        # Sample metrics (could be made configurable or calculated)
        metrics = ["DCF Value", "Market Price", "P/E Ratio", "P/B Ratio", "ROE"]
        values = [viz_data.share_price, 227.79, 37.3, 35.2, 0.15]  # Sample values

        # Create horizontal bar chart
        y_pos = np.arange(len(metrics))
        bars = ax.barh(
            y_pos, values, color=["green" if i == 0 else "blue" for i in range(len(values))]
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(metrics)
        ax.set_xlabel("Value")
        ax.set_title("Valuation Metrics")
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(
                width + 0.01 * max(values),
                bar.get_y() + bar.get_height() / 2,
                f"{values[i]:.2f}",
                ha="left",
                va="center",
            )

    def _create_risk_assessment(self, ax: matplotlib.axes.Axes) -> None:
        """
        Create risk assessment chart.

        Args:
            ax: Matplotlib axis object
        """
        # Sample risk factors (could be made configurable)
        risk_factors = [
            "Market Risk",
            "Interest Rate Risk",
            "Currency Risk",
            "Regulatory Risk",
            "Competition Risk",
        ]
        risk_scores = [0.7, 0.5, 0.3, 0.6, 0.8]  # 0-1 scale

        colors = [
            "red" if score > 0.6 else "orange" if score > 0.4 else "green" for score in risk_scores
        ]

        y_pos = np.arange(len(risk_factors))
        bars = ax.barh(y_pos, risk_scores, color=colors, alpha=0.7)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(risk_factors)
        ax.set_xlabel("Risk Score (0-1)")
        ax.set_title("Risk Assessment")
        ax.set_xlim(0, 1)
        ax.grid(True, alpha=0.3)

        # Add risk level labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            risk_level = "High" if width > 0.6 else "Medium" if width > 0.4 else "Low"
            ax.text(
                width + 0.02,
                bar.get_y() + bar.get_height() / 2,
                risk_level,
                ha="left",
                va="center",
                fontweight="bold",
            )

    def _create_terminal_output(self, viz_data: VisualizationData) -> None:
        """
        Create terminal-style output visualization.

        Args:
            viz_data: Visualization data containing DCF results
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor("black")
        ax.set_facecolor("black")

        # Terminal-style text
        terminal_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           DCF ANALYSIS RESULTS                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Company: {viz_data.ticker:<60} ║
║  Analysis Date: {self._get_current_date():<50} ║
║                                                                              ║
║  ┌──────────────────────────────────────────────────────────────────────────┐ ║
║  │                           VALUATION SUMMARY                              │ ║
║  ├──────────────────────────────────────────────────────────────────────────┤ ║
║  │  Enterprise Value: ${viz_data.enterprise_value / 1e12:>15.2f}T            │ ║
║  │  Equity Value:     ${viz_data.equity_value / 1e12:>15.2f}T                │ ║
║  │  Per Share Value:  ${viz_data.share_price:>15.2f}                       │ ║
║  └──────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ┌──────────────────────────────────────────────────────────────────────────┐ ║
║  │                           KEY METRICS                                    │ ║
║  ├──────────────────────────────────────────────────────────────────────────┤ ║
║  │  Forecast Period:  {viz_data.forecast_years:>15} years                  │ ║
║  │  Discount Rate:    {config.dcf.default_discount_rate:>15.1%}            │ ║
║  │  Growth Rate:      {config.dcf.default_earnings_growth_rate:>15.1%}      │ ║
║  └──────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  ═══════════════════════════════════════════════════════════════════════════  ║
║                                                                              ║
║  Analysis completed successfully.                                            ║
║  Check the generated charts for detailed visualizations.                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """

        ax.text(
            0.05,
            0.95,
            terminal_text,
            transform=ax.transAxes,
            fontsize=10,
            fontfamily="monospace",
            color="lime",
            verticalalignment="top",
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

    def _get_current_date(self) -> str:
        """
        Get current date in formatted string.

        Returns:
            Current date as formatted string
        """
        return datetime.now().strftime("%Y-%m-%d")


# Legacy functions for backward compatibility
def create_dcf_visualization(
    ticker: str = "AAPL",
    enterprise_value: float = 1.94e12,
    equity_value: float = 1.85e12,
    share_price: float = 120.46,
    forecast_years: int = 5,
) -> str:
    """
    Legacy function for creating DCF visualization.

    Args:
        ticker: Company ticker symbol
        enterprise_value: Enterprise value
        equity_value: Equity value
        share_price: Share price
        forecast_years: Number of forecast years

    Returns:
        Path to the generated visualization file

    Note:
        This function is deprecated. Use VisualizationService.create_comprehensive_visualization()
        instead.
    """
    service = VisualizationService()
    # Create mock DCF results for backward compatibility
    mock_results = {
        "2024-01-01": DCFResult(
            date="2024-01-01",
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            share_price=share_price,
        )
    }
    return service.create_comprehensive_visualization(ticker, mock_results, forecast_years)


def create_terminal_style_output(
    ticker: str = "AAPL",
    enterprise_value: float = 1.94e12,
    equity_value: float = 1.85e12,
    share_price: float = 120.46,
    forecast_years: int = 5,
) -> str:
    """
    Legacy function for creating terminal-style output.

    Args:
        ticker: Company ticker symbol
        enterprise_value: Enterprise value
        equity_value: Equity value
        share_price: Share price
        forecast_years: Number of forecast years

    Returns:
        Path to the generated visualization file

    Note:
        This function is deprecated. Use VisualizationService.create_terminal_style_output()
        instead.
    """
    service = VisualizationService()
    # Create mock DCF results for backward compatibility
    mock_results = {
        "2024-01-01": DCFResult(
            date="2024-01-01",
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            share_price=share_price,
        )
    }
    return service.create_terminal_style_output(ticker, mock_results, forecast_years)
