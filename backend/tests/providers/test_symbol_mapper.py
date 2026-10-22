import pytest

from app.providers.symbol_mapper import from_vendor, normalize_internal, to_vendor


def test_symbol_round_trip_all_supported_exchanges():
    for internal, vendor in (("SH.600000", "600000.SH"), ("SZ.000630", "000630.SZ"), ("BJ.430047", "430047.BJ")):
        assert to_vendor(internal) == vendor
        assert from_vendor(vendor) == internal


def test_ambiguous_symbol_is_rejected():
    with pytest.raises(ValueError): normalize_internal("000630")
