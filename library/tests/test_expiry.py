"""Tests for ExpiryTracker."""

import pytest
from datetime import datetime, timedelta
from pantry_manager.expiry import ExpiryTracker


class TestExpiryTracker:
    def setup_method(self):
        self.tracker = ExpiryTracker(days_threshold=3)

    def _date_str(self, days_from_now):
        return (datetime.now() + timedelta(days=days_from_now)).strftime("%Y-%m-%d")

    def test_check_expiry_expired_item(self):
        items = [{"name": "Milk", "expiry_date": self._date_str(-2)}]
        result = self.tracker.check_expiry(items)
        assert len(result["expired"]) == 1
        assert result["expired"][0]["name"] == "Milk"

    def test_check_expiry_expiring_soon(self):
        items = [{"name": "Bread", "expiry_date": self._date_str(2)}]
        result = self.tracker.check_expiry(items)
        assert len(result["expiring_soon"]) == 1

    def test_check_expiry_fresh_item(self):
        items = [{"name": "Cheese", "expiry_date": self._date_str(10)}]
        result = self.tracker.check_expiry(items)
        assert len(result["fresh"]) == 1

    def test_check_expiry_no_date(self):
        items = [{"name": "Rice", "expiry_date": ""}]
        result = self.tracker.check_expiry(items)
        assert len(result["fresh"]) == 1

    def test_check_expiry_mixed(self):
        items = [
            {"name": "Milk", "expiry_date": self._date_str(-1)},
            {"name": "Bread", "expiry_date": self._date_str(1)},
            {"name": "Cheese", "expiry_date": self._date_str(15)},
        ]
        result = self.tracker.check_expiry(items)
        assert len(result["expired"]) == 1
        assert len(result["expiring_soon"]) == 1
        assert len(result["fresh"]) == 1

    def test_check_expiry_custom_threshold(self):
        items = [{"name": "Yogurt", "expiry_date": self._date_str(5)}]
        result = self.tracker.check_expiry(items, days_threshold=7)
        assert len(result["expiring_soon"]) == 1

    def test_get_days_until_expiry_future(self):
        days = self.tracker.get_days_until_expiry(self._date_str(5))
        assert days == 5

    def test_get_days_until_expiry_past(self):
        days = self.tracker.get_days_until_expiry(self._date_str(-3))
        assert days == -3

    def test_get_days_until_expiry_none(self):
        assert self.tracker.get_days_until_expiry("") is None
        assert self.tracker.get_days_until_expiry(None) is None

    def test_get_days_until_expiry_invalid(self):
        assert self.tracker.get_days_until_expiry("bad-date") is None

    def test_is_expired_true(self):
        assert self.tracker.is_expired(self._date_str(-1)) is True

    def test_is_expired_false(self):
        assert self.tracker.is_expired(self._date_str(5)) is False

    def test_is_expired_no_date(self):
        assert self.tracker.is_expired("") is False

    def test_format_expiry_message_all_fresh(self):
        items = [{"name": "Rice", "expiry_date": self._date_str(30)}]
        msg = self.tracker.format_expiry_message(items)
        assert msg == "All items are fresh!"

    def test_format_expiry_message_mixed(self):
        items = [
            {"name": "Milk", "expiry_date": self._date_str(-1)},
            {"name": "Bread", "expiry_date": self._date_str(2)},
        ]
        msg = self.tracker.format_expiry_message(items)
        assert "EXPIRED: Milk" in msg
        assert "Expiring soon: Bread" in msg
