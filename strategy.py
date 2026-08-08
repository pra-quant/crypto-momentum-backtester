"""
Step 3 — The strategy itself.

Rule: every rebalance date, rank coins by trailing N-day return.
Go long the top `top_n`. Optionally short the bottom `bottom_n`
for a market-neutral version (skip shorting at first — go long-only
until the long-only version is validated).
"""
import pandas as pd


def generate_signals(price_panel: pd.DataFrame, lookback: int = 14, top_n: int = 3, bottom_n: int = 0):
    """
    Returns a DataFrame of the same shape as price_panel, with values:
        1  -> long this symbol on this date
       -1  -> short this symbol on this date
        0  -> flat
    """
    trailing_return = price_panel.pct_change(lookback)
    signals = pd.DataFrame(0, index=price_panel.index, columns=price_panel.columns)

    for date, row in trailing_return.iterrows():
        ranked = row.dropna().sort_values(ascending=False)
        if len(ranked) < top_n:
            continue  # not enough coins with valid data yet
        longs = ranked.head(top_n).index
        signals.loc[date, longs] = 1
        if bottom_n:
            shorts = ranked.tail(bottom_n).index
            signals.loc[date, shorts] = -1

    return signals
