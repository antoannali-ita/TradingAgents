"""Run TradingAgents on one or more instruments without placing real orders.

Examples:
    python scripts/analyze_watchlist.py NVDA
    python scripts/analyze_watchlist.py NVDA INTU GOLD --date 2026-08-19

Provider and model settings are read from the existing .env variables documented
in .env.example. The script saves the full report tree for every completed run
and writes a compact watchlist summary in the results directory.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import date
from pathlib import Path

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


CRYPTO_SUFFIX = "-USD"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analisi multi-agente di uno o più titoli, ETF o crypto."
    )
    parser.add_argument("tickers", nargs="+", help="Ticker Yahoo Finance, es. NVDA VWCE.MI")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Data di analisi YYYY-MM-DD (default: oggi).",
    )
    parser.add_argument(
        "--analysts",
        nargs="+",
        choices=("market", "social", "news", "fundamentals"),
        default=("market", "social", "news", "fundamentals"),
        help="Agenti da eseguire.",
    )
    parser.add_argument(
        "--output-language",
        default="Italian",
        help="Lingua dei report finali (default: Italian).",
    )
    parser.add_argument(
        "--checkpoint",
        action="store_true",
        help="Riprende un'analisi interrotta dall'ultimo agente completato.",
    )
    return parser.parse_args()


def asset_type(ticker: str) -> str:
    return "crypto" if ticker.upper().endswith(CRYPTO_SUFFIX) else "stock"


def main() -> int:
    args = parse_args()

    config = deepcopy(DEFAULT_CONFIG)
    config["output_language"] = args.output_language
    config["checkpoint_enabled"] = args.checkpoint

    engine = TradingAgentsGraph(
        selected_analysts=tuple(args.analysts),
        debug=False,
        config=config,
    )

    summaries: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []

    for raw_ticker in args.tickers:
        ticker = raw_ticker.strip().upper()
        if not ticker:
            continue

        print(f"\n=== Analisi multi-agente: {ticker} ({args.date}) ===")
        try:
            final_state, decision = engine.propagate(
                ticker,
                args.date,
                asset_type=asset_type(ticker),
            )
            report_path = engine.save_reports(final_state, ticker)
            summaries.append(
                {
                    "ticker": ticker,
                    "date": args.date,
                    "decision": str(decision),
                    "report_path": str(report_path),
                }
            )
            print(decision)
            print(f"Report: {report_path}")
        except Exception as exc:  # continue with the rest of the watchlist
            failures.append({"ticker": ticker, "error": f"{type(exc).__name__}: {exc}"})
            print(f"ERRORE {ticker}: {type(exc).__name__}: {exc}")

    output_dir = Path(config["results_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / f"watchlist_{args.date}.json"
    summary_path.write_text(
        json.dumps({"results": summaries, "failures": failures}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nRiepilogo: {summary_path}")

    return 1 if failures and not summaries else 0


if __name__ == "__main__":
    raise SystemExit(main())
