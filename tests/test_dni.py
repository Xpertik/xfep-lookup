"""Tests for DniLookup facade."""

import pytest

from xfep.lookup.dni import DniLookup
from xfep.lookup.errors import NotFoundError
from xfep.lookup.models import DniInfo


async def test_valid_dni_delegates_to_provider(mock_provider):
    lookup = DniLookup(provider=mock_provider)
    result = await lookup.get("12345678")
    assert isinstance(result, DniInfo)
    assert result.dni == "12345678"
    assert result.nombres == "JUAN"


async def test_invalid_dni_too_short_raises_value_error(mock_provider):
    lookup = DniLookup(provider=mock_provider)
    with pytest.raises(ValueError, match="DNI must be 8 digits"):
        await lookup.get("123")


async def test_invalid_dni_not_digits_raises_value_error(mock_provider):
    lookup = DniLookup(provider=mock_provider)
    with pytest.raises(ValueError, match="DNI must be 8 digits"):
        await lookup.get("ABCDEFGH")


async def test_invalid_dni_empty_raises_value_error(mock_provider):
    lookup = DniLookup(provider=mock_provider)
    with pytest.raises(ValueError, match="DNI must be 8 digits"):
        await lookup.get("")


async def test_dni_not_found_propagates_error(mock_provider):
    lookup = DniLookup(provider=mock_provider)
    with pytest.raises(NotFoundError):
        await lookup.get("99999999")
