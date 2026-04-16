"""Tests for RucLookup facade."""

import pytest

from xfep.lookup.errors import NotFoundError
from xfep.lookup.models import RucInfo
from xfep.lookup.ruc import RucLookup


async def test_valid_ruc_delegates_to_provider(mock_provider):
    lookup = RucLookup(provider=mock_provider)
    result = await lookup.get("20100017491")
    assert isinstance(result, RucInfo)
    assert result.ruc == "20100017491"
    assert result.razon_social == "SUNAT"


async def test_invalid_ruc_too_short_raises_value_error(mock_provider):
    lookup = RucLookup(provider=mock_provider)
    with pytest.raises(ValueError, match="RUC must be 11 digits"):
        await lookup.get("123")


async def test_invalid_ruc_not_digits_raises_value_error(mock_provider):
    lookup = RucLookup(provider=mock_provider)
    with pytest.raises(ValueError, match="RUC must be 11 digits"):
        await lookup.get("2010001ABC1")


async def test_invalid_ruc_empty_raises_value_error(mock_provider):
    lookup = RucLookup(provider=mock_provider)
    with pytest.raises(ValueError, match="RUC must be 11 digits"):
        await lookup.get("")


async def test_ruc_not_found_propagates_error(mock_provider):
    lookup = RucLookup(provider=mock_provider)
    with pytest.raises(NotFoundError):
        await lookup.get("99999999999")
