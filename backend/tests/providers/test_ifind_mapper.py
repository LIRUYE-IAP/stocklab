from app.core.config import Settings
from app.providers.ifind import IFindProvider


def test_ifind_optional_fields_remain_null_instead_of_fabricated():
    provider = IFindProvider(Settings())
    payload = {"errorcode": 0, "data": {"tables": [{"thscode": ["000630.SZ"], "table": {"latest": [5.86], "open": [5.66]}}]}}
    quote = provider._parse(payload, ["SZ.000630"])["SZ.000630"]
    assert quote.price == 5.86
    assert quote.high is None
    assert quote.bid_price_1 is None
    assert "supplier_trade_time_unavailable" in quote.quality_flags
