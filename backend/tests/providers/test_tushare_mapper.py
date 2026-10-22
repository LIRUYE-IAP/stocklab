from app.providers.tushare_mapper import map_board, map_daily, map_daily_basic


def test_tushare_daily_units_are_normalized_to_shares_and_cny():
    row = map_daily({"trade_date": "20260908", "open": 10, "high": 11, "low": 9, "close": 10.5, "pre_close": 10, "change": .5, "pct_chg": 5, "vol": 1234.5, "amount": 6789.2})
    assert row["volume_shares"] == 123450
    assert row["amount_cny"] == 6789200


def test_tushare_daily_basic_units_are_normalized():
    row = map_daily_basic({"trade_date": "20260908", "total_share": 100, "float_share": 80, "free_share": 60, "total_mv": 1200, "circ_mv": 900})
    assert row["total_share_shares"] == 1_000_000
    assert row["total_market_cap_cny"] == 12_000_000


def test_unknown_board_is_not_guessed():
    assert map_board("SH", None, "900001") == "UNKNOWN"
