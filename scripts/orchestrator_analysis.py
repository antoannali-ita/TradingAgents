from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


def _supabase_update(analysis_id: str, payload: dict) -> None:
    url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    key = (os.getenv("SUPABASE_SECRET_KEY") or "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL/SUPABASE_SECRET_KEY are required")
    request = urllib.request.Request(
        f"{url}/rest/v1/ai_analysis?analysis_id=eq.{analysis_id}",
        data=json.dumps(payload, default=str).encode("utf-8"),
        method="PATCH",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status not in {200, 204}:
                raise RuntimeError(f"Supabase returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"Supabase HTTP {exc.code}: {detail}") from exc


def _alignment(decision) -> str:
    text = str(decision or "").upper()
    if any(word in text for word in ("SELL", "AVOID", "BEARISH")):
        return "VETO"
    if any(word in text for word in ("BUY", "BULLISH")):
        return "CONFIRM"
    if any(word in text for word in ("CAUTION", "WAIT", "RISK")):
        return "CAUTION"
    return "NEUTRAL"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--market", default="usa")
    parser.add_argument("--analysis-id", required=True)
    parser.add_argument("--source-signal-id", default="")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()

    config = DEFAULT_CONFIG.copy()
    model = f"{config.get('llm_provider')}:{config.get('deep_think_llm')}"
    _supabase_update(args.analysis_id, {
        "status": "RUNNING",
        "provider": "TRADINGAGENTS",
        "model": model,
        "started_at": datetime.now(timezone.utc).isoformat(),
    })

    try:
        graph = TradingAgentsGraph(debug=False, config=config)
        state, decision = graph.propagate(args.ticker.upper(), args.date)
        alignment = _alignment(decision)
        _supabase_update(args.analysis_id, {
            "status": "SUCCESS",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "verdict": str(decision),
            "alignment": alignment,
            "summary": str(decision),
            "raw_payload": {
                "decision": decision,
                "market": args.market.upper(),
                "analysis_date": args.date,
                "source_signal_id": args.source_signal_id or None,
                "state": state,
            },
        })
        print(json.dumps({"ticker": args.ticker.upper(), "alignment": alignment, "decision": decision}, default=str))
    except Exception as exc:
        _supabase_update(args.analysis_id, {
            "status": "FAILED",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": f"{type(exc).__name__}: {exc}"[:4000],
        })
        raise


if __name__ == "__main__":
    main()
