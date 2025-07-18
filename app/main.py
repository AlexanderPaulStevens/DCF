"""
author: Hugh Alessi
date: Saturday, July 27, 2019  8:25:00 PM
description: Use primitive underlying DCF modeling to compare intrinsic per share price
    to current share price.

future goals:
    -- Formalize sensitivity analysis.
    -- More robust revenue forecasts in FCF.
    -- EBITA multiples terminal value calculation.
    -- More to be added.
"""

import argparse
import os

from modeling.dcf import historical_dcf
from visualization.plot import visualize_bulk_historicals
from visualization.printouts import prettyprint

# Import visualization functions at top level
try:
    from visualization.visualize_dcf import (
        create_dcf_visualization,
        create_terminal_style_output,
    )

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


def _get_variable_mapping(variable):
    """Map variable names to their internal representations."""
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


def main(args):
    """
    although the if statements are less than desirable, it allows rapid exploration of
    historical or present DCF values for either a single or list of tickers.
    """

    if args.s > 0:
        if args.v is None:
            raise ValueError(
                "If step (--s) is > 0, you must specify the variable via --v. "
                "What was passed is invalid."
            )

        variable = _get_variable_mapping(args.v)
        if variable is None:
            raise ValueError(
                "args.variable is invalid, must choose (as of now) from this list -> "
                "[earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, discount]"
            )

        cond, dcfs = run_setup(args, variable=variable)
    else:
        cond, dcfs = {"Ticker": [args.t]}, {}
        dcfs[args.t] = historical_dcf(
            args.t, args.y, args.p, args.d, args.eg, args.cg, args.pg, args.i, args.apikey
        )

    if args.y > 1:  # can't graph single timepoint very well....
        visualize_bulk_historicals(dcfs, args.t, cond, args.apikey)
    else:
        prettyprint(dcfs, args.y)

        # Automatically generate enhanced visualizations
    if VISUALIZATION_AVAILABLE:
        print("\n" + "=" * 60)
        print("📊 Generating Enhanced Visualizations...")
        print("=" * 60)

        # Extract values from the DCF results for visualization
        if dcfs and args.t in dcfs and dcfs[args.t]:
            # Get the first (most recent) DCF result
            first_result = next(iter(dcfs[args.t].values()))
            enterprise_value = first_result.get("enterprise_value", 1.94e12)
            equity_value = first_result.get("equity_value", 1.85e12)
            share_price = first_result.get("share_price", 120.46)

            # Create visualizations
            create_dcf_visualization(
                ticker=args.t,
                enterprise_value=enterprise_value,
                equity_value=equity_value,
                share_price=share_price,
                forecast_years=args.p,
            )
            create_terminal_style_output()

            print("✅ Visualizations created successfully!")
            print("📁 Check the 'app/imgs/' directory for generated charts:")
            print("   - {}_comprehensive_dcf.png (Main dashboard)".format(args.t))
            print("   - terminal_output.png (Terminal-style output)")
        else:
            print("⚠️  No DCF results available for visualization")
    else:
        print("\n⚠️  Visualization module not available")
        print("   Make sure visualize_dcf.py is in the app/visualization/ directory")


def run_setup(args, variable):
    dcfs, cond = {}, {args.v: []}

    for increment in range(1, int(args.steps) + 1):  # default to 5 steps?
        # this should probably be wrapped in another function..
        var = vars(args)[variable] * (1 + (args.s * increment))
        step = "{}: {}".format(args.v, str(var)[0:4])

        cond[args.v].append(step)
        vars(args)[variable] = var
        dcfs[step] = historical_dcf(
            args.t, args.y, args.p, args.d, args.eg, args.cg, args.pg, args.i, args.apikey
        )

    return cond, dcfs


def multiple_tickers():
    """
    can be called from main to spawn dcf/historical dcfs for
    a list of tickers TODO: fully fix
    """
    # if args.ts is not None:
    #     """list to forecast"""
    #     if args.y > 1:
    #         for ticker in args.ts:
    #             dcfs[ticker] =  historical_DCF(args.t, args.y, args.p, args.eg, args.cg, args.pgr)
    #     else:
    #         for ticker in args.tss:
    #             dcfs[ticker] = DCF(args.t, args.p, args.eg, args.cg, args.pgr)
    # elif args.t is not None:
    #     """ single ticker"""
    #     if args.y > 1:
    #         dcfs[args.t] = historical_DCF(args.t, args.y, args.p, args.eg, args.cg, args.pgr)
    #     else:
    #         dcfs[args.t] = DCF(args.t, args.p, args.eg, args.cg, args.pgr)
    # else:
    #     raise ValueError('A ticker or list of tickers must be specified with '
    #                     '--ticker or --tickers')
    return NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--p", "--period", help="years to forecast", type=int, default=5)
    parser.add_argument(
        "--t",
        "--ticker",
        help="pass a single ticker to do historical DCF",
        type=str,
        default="AAPL",
    )
    parser.add_argument(
        "--y", "--years", help="number of years to compute DCF analysis for", type=int, default=1
    )
    parser.add_argument(
        "--i",
        "--interval",
        help='interval period for each calc, either "annual" or "quarter"',
        default="annual",
    )
    parser.add_argument(
        "--s",
        "--step_increase",
        help="specify step increase for EG, CG, PG to enable comparisons.",
        type=float,
        default=0,
    )
    parser.add_argument("--steps", help="steps to take if --s is > 0", default=5)
    parser.add_argument(
        "--v",
        "--variable",
        help="if --step_increase is specified, must specifiy variable to increase from: "
        "[earnings_growth_rate, discount_rate]",
        default=None,
    )
    parser.add_argument(
        "--d",
        "--discount_rate",
        help="discount rate for future cash flow to firm",
        type=float,
        default=0.1,
    )
    parser.add_argument(
        "--eg", "--earnings_growth_rate", help="growth in revenue, YoY", type=float, default=0.05
    )
    parser.add_argument(
        "--cg", "--cap_ex_growth_rate", help="growth in cap_ex, YoY", type=float, default=0.045
    )
    parser.add_argument(
        "--pg",
        "--perpetual_growth_rate",
        help="for perpetuity growth terminal value",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--apikey", help="API key for financialmodelingprep.com", default=os.environ.get("APIKEY")
    )

    args = parser.parse_args()
    main(args)
