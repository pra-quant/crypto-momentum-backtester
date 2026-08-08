"""
Step 6 — Run everything end to end and export results.json.

Runs the backtest across MULTIPLE lookback values (7, 14, 30 days) so you
can compare them side by side on the dashboard, instead of editing this
file and re-running it three separate times.

Each lookback still gets its own in-sample / out-of-sample split —
report BOTH for every lookback. A strategy that only works in-sample
isn't a strategy, it's overfitting.

Usage: python src/main.py
"""
import json
import os

from data_loader import load_price_panel
from strategy import generate_signals
from backtest import run_backtest
from metrics import summarize

LOOKBACKS = [7, 14, 30]   # days of trailing return used to rank coins — comparing all three
TOP_N = 3                  # how many coins to hold long
HOLD_DAYS = 7               # rebalance frequency
COST_BPS = 10                # round-trip transaction cost estimate

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "results.json")


def run_segment(price_panel, lookback):
    signals = generate_signals(price_panel, lookback=lookback, top_n=TOP_N)
    result = run_backtest(price_panel, signals, hold_days=HOLD_DAYS, cost_bps=COST_BPS)
    metrics, drawdown_series = summarize(result["daily_returns"], result["equity_curve"], result["turnover"])
    return result, metrics, drawdown_series


def main():
    panel = load_price_panel()
    split_idx = int(len(panel) * 0.7)
    in_sample = panel.iloc[:split_idx]
    out_sample = panel.iloc[split_idx:]

    runs = {}

    for lookback in LOOKBACKS:
        print(f"\n########## LOOKBACK = {lookback} days ##########")
        is_result, is_metrics, is_dd = run_segment(in_sample, lookback)
        oos_result, oos_metrics, oos_dd = run_segment(out_sample, lookback)

        print("=== IN-SAMPLE ===")
        print(is_metrics)
        print("=== OUT-OF-SAMPLE ===")
        print(oos_metrics)

        runs[str(lookback)] = {
            "params": {"lookback": lookback, "top_n": TOP_N, "hold_days": HOLD_DAYS, "cost_bps": COST_BPS},
            "in_sample": {
                "metrics": is_metrics,
                "equity_curve": {str(d.date()): v for d, v in is_result["equity_curve"].items()},
                "drawdown": {str(d.date()): v for d, v in is_dd.items()},
            },
            "out_of_sample": {
                "metrics": oos_metrics,
                "equity_curve": {str(d.date()): v for d, v in oos_result["equity_curve"].items()},
                "drawdown": {str(d.date()): v for d, v in oos_dd.items()},
            },
        }

    output = {"lookbacks": LOOKBACKS, "runs": runs}

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved results -> {OUT_PATH}")
    print("Open dashboard.html and load this file to compare all three lookbacks.")


if __name__ == "__main__":
    main()
