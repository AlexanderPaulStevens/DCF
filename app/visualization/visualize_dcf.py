#!/usr/bin/env python3
"""
Enhanced DCF Visualization Script
Creates comprehensive visualizations of DCF analysis results
"""

from datetime import datetime

import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set up the plotting style
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


def create_dcf_visualization(
    ticker: str = "AAPL",
    enterprise_value: float = 1.94e12,
    equity_value: float = 1.85e12,
    share_price: float = 120.46,
    forecast_years: int = 5,
) -> None:
    """
    Create a comprehensive DCF visualization dashboard
    """

    # Create figure with subplots
    plt.figure(figsize=(12, 9))

    # 1. Main Summary Dashboard
    ax1 = plt.subplot(2, 3, 1)
    create_summary_dashboard(ax1, ticker, enterprise_value, equity_value, share_price)

    # 2. Value Breakdown
    ax2 = plt.subplot(2, 3, 2)
    create_value_breakdown(ax2, enterprise_value, equity_value)

    # 3. Cash Flow Projection
    ax3 = plt.subplot(2, 3, 3)
    create_cash_flow_projection(ax3, forecast_years)

    # 4. Sensitivity Analysis
    ax4 = plt.subplot(2, 3, 4)
    create_sensitivity_analysis(ax4, share_price)

    # 5. Valuation Metrics
    ax5 = plt.subplot(2, 3, 5)
    create_valuation_metrics(ax5, share_price)

    # 6. Risk Assessment
    ax6 = plt.subplot(2, 3, 6)
    create_risk_assessment(ax6)

    plt.tight_layout()
    plt.savefig(f"app/imgs/{ticker}_comprehensive_dcf.png", dpi=150, bbox_inches="tight")
    plt.show()


def create_summary_dashboard(
    ax: matplotlib.axes.Axes,
    ticker: str,
    enterprise_value: float,
    equity_value: float,
    share_price: float,
) -> None:
    """Create the main summary dashboard"""

    # Format values for display
    ev_formatted = f"${enterprise_value / 1e12:.2f}T"
    equity_formatted = f"${equity_value / 1e12:.2f}T"
    price_formatted = f"${share_price:.2f}"

    # Create summary text
    summary_text = f"""
    DCF Analysis Summary

    Company: {ticker}

    Enterprise Value: {ev_formatted}
    Equity Value: {equity_formatted}
    Per Share Value: {price_formatted}

    Analysis Date: {datetime.now().strftime("%Y-%m-%d")}
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


def create_value_breakdown(
    ax: matplotlib.axes.Axes, enterprise_value: float, equity_value: float
) -> None:
    """Create value breakdown chart"""

    # Calculate components
    debt_cash_adjustment = enterprise_value - equity_value

    labels = ["Enterprise Value", "Debt & Cash\nAdjustment", "Equity Value"]
    sizes = [enterprise_value, debt_cash_adjustment, equity_value]
    colors = ["#ff9999", "#66b3ff", "#99ff99"]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
    )

    # Format the percentage labels
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title("Value Breakdown", fontsize=14, fontweight="bold")


def create_cash_flow_projection(ax: matplotlib.axes.Axes, forecast_years: int) -> None:
    """Create cash flow projection chart"""

    # Sample cash flow data (you can replace with actual data)
    years = list(range(1, forecast_years + 1))
    dfcf = [9.72e10, 9.51e10, 9.80e10, 1.06e11, 1.20e11]  # From your terminal output
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
    ax.set_title("5-Year Cash Flow Projection")
    ax.set_xticks(x)
    ax.set_xticklabels([f"202{5 + i}" for i in range(forecast_years)])
    ax.legend()
    ax.grid(True, alpha=0.3)


def create_sensitivity_analysis(ax: matplotlib.axes.Axes, base_share_price: float) -> None:
    """Create sensitivity analysis chart"""

    # Create sensitivity matrix
    growth_rates = np.linspace(0.02, 0.08, 7)  # 2% to 8%
    discount_rates = np.linspace(0.08, 0.15, 8)  # 8% to 15%

    # Create a simple sensitivity matrix (you can replace with actual calculations)
    sensitivity_matrix = np.zeros((len(growth_rates), len(discount_rates)))

    for i, growth in enumerate(growth_rates):
        for j, discount in enumerate(discount_rates):
            # Simplified sensitivity calculation
            sensitivity_matrix[i, j] = base_share_price * (1 + growth) / (1 + discount)

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


def create_valuation_metrics(ax: matplotlib.axes.Axes, share_price: float) -> None:
    """Create valuation metrics comparison"""

    # Sample metrics (you can replace with actual data)
    metrics = ["DCF Value", "Market Price", "P/E Ratio", "P/B Ratio", "ROE"]
    values = [share_price, 227.79, 37.3, 35.2, 0.15]  # Sample values

    # Create horizontal bar chart
    y_pos = np.arange(len(metrics))
    bars = ax.barh(y_pos, values, color=["green" if i == 0 else "blue" for i in range(len(values))])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics)
    ax.set_xlabel("Value")
    ax.set_title("Valuation Metrics")

    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(
            width + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{values[i]:.2f}",
            ha="left",
            va="center",
        )


def create_risk_assessment(ax: matplotlib.axes.Axes) -> None:
    """Create risk assessment radar chart"""

    # Risk categories and scores (0-10, where 10 is highest risk)
    categories = [
        "Market Risk",
        "Business Risk",
        "Financial Risk",
        "Regulatory Risk",
        "Technology Risk",
    ]
    scores = [6, 4, 3, 5, 7]  # Sample risk scores

    # Number of variables
    nr_categories = len(categories)

    # Compute angle for each axis
    angles = [n / float(nr_categories) * 2 * np.pi for n in range(nr_categories)]
    angles += angles[:1]  # Complete the circle

    # Add the first value at the end to close the plot
    scores += scores[:1]

    # Create the plot
    ax.plot(angles, scores, "o-", linewidth=2, color="red", alpha=0.7)
    ax.fill(angles, scores, alpha=0.25, color="red")

    # Set the labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 11, 2))
    ax.set_yticklabels([f"{i}" for i in range(0, 11, 2)])

    ax.set_title("Risk Assessment", fontsize=14, fontweight="bold")
    ax.grid(True)


def create_terminal_style_output() -> None:
    """Create a terminal-style output visualization"""

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor("black")

    # Terminal output text
    terminal_text = """
Forecasting flows for 5 years out, starting at 2024-09-28.
         DFCF   |    EBIT   |    D&A    |    CWC     |   CAP_EX   |
2025   9.72E+10 |  1.29E+11 |  1.20E+10 |  6.59E+09 |  -9.87E+09 |
2026   9.51E+10 |  1.42E+11 |  1.32E+10 |  4.62E+09 |  -1.08E+10 |
2027   9.80E+10 |  1.64E+11 |  1.52E+10 |  3.23E+09 |  -1.22E+10 |
2028   1.06E+11 |  1.96E+11 |  1.82E+10 |  2.26E+09 |  -1.44E+10 |
2029   1.20E+11 |  2.45E+11 |  2.28E+10 |  1.58E+09 |  -1.77E+10 |

Enterprise Value for AAPL: $1.94E+12.
Equity Value for AAPL: $1.85E+12.
Per share value for AAPL: $1.20E+02.

------------------------------------------------------------
ticker: AAPL
value: {'2024-09-28': {'date': '2024-09-28', 'enterprise_value': 1937395670542.2856,
       'equity_value': 1848279670542.2856, 'share_price': 120.4578864640021}}
    """

    ax.text(
        0.05,
        0.95,
        terminal_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        color="lime",
        fontfamily="monospace",
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("DCF Analysis Terminal Output", fontsize=16, fontweight="bold", color="white")

    plt.savefig(
        "app/imgs/terminal_output.png",
        dpi=150,
        bbox_inches="tight",
        facecolor="black",
    )
    plt.show()


if __name__ == "__main__":
    # Create the comprehensive visualization
    create_dcf_visualization()

    # Create terminal-style output
    create_terminal_style_output()

    print("Visualizations created successfully!")
    print("Check the 'app/imgs/' directory for the generated charts.")
