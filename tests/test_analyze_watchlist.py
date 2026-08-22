"""Tests for the controlled watchlist runner."""

from scripts.analyze_watchlist import asset_type


def test_asset_type_defaults_to_stock():
    assert asset_type("NVDA") == "stock"
    assert asset_type("SWDA.MI") == "stock"


def test_asset_type_detects_crypto_case_insensitively():
    assert asset_type("BTC-USD") == "crypto"
    assert asset_type("eth-usd") == "crypto"
