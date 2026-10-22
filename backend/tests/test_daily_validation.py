from app.services.data_quality import validate_daily_row


def test_valid_daily_row_passes():
    assert validate_daily_row({"open": 10, "high": 11, "low": 9, "close": 10.5, "volume_shares": 1000, "amount_cny": 10000}) == []


def test_invalid_daily_row_is_rejected_with_explainable_rules():
    errors = validate_daily_row({"open": 10, "high": 9, "low": 11, "close": 10.5, "volume_shares": -1, "amount_cny": -2})
    assert {"high_below_low", "high_below_open", "high_below_close", "low_above_open", "low_above_close", "negative_volume", "negative_amount"}.issubset(errors)
