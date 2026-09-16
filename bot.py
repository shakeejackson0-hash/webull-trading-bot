#!/usr/bin/env python3
"""
Webull Trading Bot - Main entry point.

Uses the official webull-openapi-python-sdk.
Always start in the sandbox environment!
"""

import argparse
import uuid
import sys
from typing import Optional, List, Dict, Any

from webull.core.client import ApiClient
from webull.trade.trade_client import TradeClient
from webull.data.data_client import DataClient
from webull.data.common.category import Category
from webull.data.common.timespan import Timespan

from config import Config
from strategies.sma_crossover import SMACrossoverStrategy


class WebullBot:
    def __init__(self):
        Config.validate()

        self.api_client = ApiClient(
            Config.APP_KEY, Config.APP_SECRET, Config.REGION
        )
        self.api_client.add_endpoint(Config.REGION, Config.ENDPOINT)

        self.trade_client = TradeClient(self.api_client)
        self.data_client = DataClient(self.api_client)

        self.account_id = Config.ACCOUNT_ID or self._get_first_account_id()

    def _get_first_account_id(self) -> str:
        res = self.trade_client.account_v2.get_account_list()
        if res.status_code != 200:
            raise RuntimeError(f"Failed to fetch accounts: {res.status_code} {res.text}")

        accounts = res.json()
        if not accounts:
            raise RuntimeError("No accounts found for this API key")

        # Response structure may vary; try common keys
        if isinstance(accounts, list):
            account = accounts[0]
        elif isinstance(accounts, dict) and "data" in accounts:
            account = accounts["data"][0]
        else:
            account = accounts

        account_id = (
            account.get("account_id")
            or account.get("accountId")
            or account.get("id")
        )
        if not account_id:
            raise RuntimeError(f"Could not extract account_id from: {account}")

        print(f"Using account_id: {account_id}")
        return str(account_id)

    def list_accounts(self) -> None:
        res = self.trade_client.account_v2.get_account_list()
        print(f"Status: {res.status_code}")
        print(res.json())

    def get_balance(self) -> None:
        # Try common account info endpoints
        try:
            res = self.trade_client.account_v2.get_account_balance(self.account_id)
            print(f"Status: {res.status_code}")
            print(res.json())
        except Exception as e:
            print(f"Balance endpoint error (may differ by region/version): {e}")
            print("Try checking the official docs for the exact method name.")

    def get_positions(self) -> None:
        try:
            res = self.trade_client.account_v2.get_account_position(self.account_id)
            print(f"Status: {res.status_code}")
            print(res.json())
        except Exception as e:
            print(f"Positions endpoint error: {e}")

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: str,
        limit_price: str,
        dry_run: bool = True,
    ) -> None:
        client_order_id = uuid.uuid4().hex
        order = {
            "combo_type": "NORMAL",
            "client_order_id": client_order_id,
            "symbol": symbol.upper(),
            "instrument_type": "EQUITY",
            "market": "US",
            "order_type": "LIMIT",
            "limit_price": str(limit_price),
            "quantity": str(quantity),
            "support_trading_session": "CORE",
            "side": side.upper(),
            "time_in_force": "DAY",
            "entrust_type": "QTY",
        }

        print(f"Order payload: {order}")

        if dry_run:
            print("[DRY-RUN] Order would be placed. Remove --dry-run to execute.")
            return

        res = self.trade_client.order_v3.place_order(self.account_id, [order])
        print(f"Status: {res.status_code}")
        print(res.json())

    def fetch_history_bars(
        self, symbol: str, timespan: str = "M5", count: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch historical bars. Adjust parameters based on SDK version."""
        try:
            res = self.data_client.market_data.get_history_bar(
                symbol.upper(),
                Category.US_STOCK.name,
                timespan,  # e.g. Timespan.M5.name if available
            )
            if res.status_code == 200:
                data = res.json()
                # Normalize to list of dicts
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
                if isinstance(data, list):
                    return data
                return [data]
            else:
                print(f"History bar error: {res.status_code} {res.text}")
                return []
        except Exception as e:
            print(f"Error fetching bars: {e}")
            return []

    def run_strategy(
        self, symbol: str, dry_run: bool = True, qty: str = "1"
    ) -> None:
        print(f"Running SMA crossover strategy on {symbol}...")

        bars = self.fetch_history_bars(symbol)
        if not bars:
            print("No bar data available. Check market data subscription / sandbox limits.")
            return

        strategy = SMACrossoverStrategy(short_window=10, long_window=30)
        signal = strategy.generate_signal(bars)
        print(f"Signal: {signal}")

        if signal == "HOLD":
            print("No action.")
            return

        # For a real price you would fetch the latest quote.
        # Here we use a placeholder; replace with actual last price in production.
        last_close = bars[-1].get("close") or bars[-1].get("c") or "0"
        print(f"Last close (approx): {last_close}")

        side = signal  # BUY or SELL
        self.place_order(
            symbol=symbol,
            side=side,
            quantity=qty,
            limit_price=str(last_close),
            dry_run=dry_run,
        )


def main():
    parser = argparse.ArgumentParser(description="Webull Trading Bot")
    parser.add_argument(
        "--action",
        choices=["accounts", "balance", "positions", "place", "run"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument("--symbol", default=Config.DEFAULT_SYMBOL)
    parser.add_argument("--side", choices=["BUY", "SELL"], default="BUY")
    parser.add_argument("--qty", default="1")
    parser.add_argument("--price", default="0")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without placing real orders (strongly recommended)",
    )

    args = parser.parse_args()

    try:
        bot = WebullBot()
    except Exception as e:
        print(f"Failed to initialize bot: {e}")
        sys.exit(1)

    if args.action == "accounts":
        bot.list_accounts()
    elif args.action == "balance":
        bot.get_balance()
    elif args.action == "positions":
        bot.get_positions()
    elif args.action == "place":
        if args.price == "0":
            print("Please provide --price for limit orders")
            sys.exit(1)
        bot.place_order(
            symbol=args.symbol,
            side=args.side,
            quantity=args.qty,
            limit_price=args.price,
            dry_run=args.dry_run,
        )
    elif args.action == "run":
        bot.run_strategy(
            symbol=args.symbol, dry_run=args.dry_run, qty=args.qty
        )


if __name__ == "__main__":
    main()
