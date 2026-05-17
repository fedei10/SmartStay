"""Unit tests for _keep() state-merge helper and BookingState field behaviour."""
import pytest

from app.agents.booking.nodes import _keep


class TestKeepHelper:
    """_keep(new_val, existing_val) → new_val when not None, else existing."""

    def test_new_value_wins(self):
        assert _keep("Paris", "London") == "Paris"

    def test_existing_preserved_when_new_is_none(self):
        assert _keep(None, "London") == "London"

    def test_both_none_returns_none(self):
        assert _keep(None, None) is None

    def test_falsy_int_zero_is_still_truthy_new(self):
        # 0 guests is edge-case but _keep should return 0 not existing
        # (0 is falsy but not None)
        assert _keep(0, 2) == 0

    def test_empty_string_is_new_value(self):
        # Empty string is not None so it should win
        assert _keep("", "London") == ""

    def test_new_int_wins(self):
        assert _keep(2, 1) == 2

    def test_preserves_existing_int(self):
        assert _keep(None, 3) == 3
