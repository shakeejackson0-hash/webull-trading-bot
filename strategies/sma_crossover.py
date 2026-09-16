"""Simple Moving Average (SMA) crossover strategy.

Generates BUY when short SMA crosses above long SMA,
SELL when short SMA crosses below long SMA.
"""

from typing import List, Dict, Any
import pandas as pd


class SMACrossoverStrategy:
    def __init__(self, short_window: int = 10, long_window: int = 30):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, bars: List[Dict[str, Any]]) -> str:
        """
        bars: list of dicts with at least a 'close' key (most recent last).
        Returns: "BUY", "SELL", or "HOLD"
        """
        if len(bars) < self.long_window + 2:
            return "HOLD"

        closes = [float(b.get("close") or b.get("c") or 0) for b in bars]
        df = pd.Series(closes)

        short_sma = df.rolling(window=self.short_window).mean()
        long_sma = df.rolling(window=self.long_window).mean()

        # Previous and current values
        prev_short = short_sma.iloc[-2]
        prev_long = long_sma.iloc[-2]
        curr_short = short_sma.iloc[-1]
        curr_long = long_sma.iloc[-1]

        if pd.isna(prev_short) or pd.isna(prev_long) or pd.isna(curr_short) or pd.isna(curr_long):
            return "HOLD"

        # Bullish crossover
        if prev_short <= prev_long and curr_short > curr_long:
            return "BUY"

        # Bearish crossover
        if prev_short >= prev_long and curr_short < curr_long:
            return "SELL"

        return "HOLD"
