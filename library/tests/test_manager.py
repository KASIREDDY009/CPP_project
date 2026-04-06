"""Tests for PantryManager."""

import pytest
from pantry_manager.manager import PantryManager


class TestPantryManager:
    def setup_method(self):
        self.manager = PantryManager()

    def test_create_item_valid(self):
        item = self.manager.create_item("Milk", "Dairy", quantity=2, unit="L")
        assert item["name"] == "Milk"
        assert item["category"] == "Dairy"
        assert item["quantity"] == 2
        assert item["unit"] == "L"
        assert "id" in item

    def test_create_item_default_values(self):
        item = self.manager.create_item("Apple")
        assert item["category"] == "Other"
        assert item["quantity"] == 1
        assert item["unit"] == "pcs"

    def test_create_item_empty_name_raises(self):
        with pytest.raises(ValueError, match="Item name is required"):
            self.manager.create_item("")

    def test_create_item_whitespace_name_raises(self):
        with pytest.raises(ValueError, match="Item name is required"):
            self.manager.create_item("   ")

    def test_create_item_negative_quantity_raises(self):
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            self.manager.create_item("Milk", quantity=-1)

    def test_create_item_invalid_unit_raises(self):
        with pytest.raises(ValueError, match="Invalid unit"):
            self.manager.create_item("Milk", unit="gallons")

    def test_create_item_invalid_date_raises(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            self.manager.create_item("Milk", expiry_date="15-04-2026")

    def test_create_item_valid_date(self):
        item = self.manager.create_item("Milk", expiry_date="2026-04-15")
        assert item["expiry_date"] == "2026-04-15"

    def test_get_item(self):
        item = self.manager.create_item("Bread")
        found = self.manager.get_item(item["id"])
        assert found["name"] == "Bread"

    def test_get_item_not_found(self):
        result = self.manager.get_item("nonexistent-id")
        assert result is None

    def test_update_item(self):
        item = self.manager.create_item("Milk", quantity=1)
        updated = self.manager.update_item(item["id"], quantity=5)
        assert updated["quantity"] == 5

    def test_update_item_not_found_raises(self):
        with pytest.raises(ValueError, match="Item not found"):
            self.manager.update_item("bad-id", quantity=1)

    def test_update_item_negative_quantity_raises(self):
        item = self.manager.create_item("Milk")
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            self.manager.update_item(item["id"], quantity=-5)

    def test_delete_item(self):
        item = self.manager.create_item("Bread")
        assert self.manager.delete_item(item["id"]) is True
        assert len(self.manager.items) == 0

    def test_delete_item_not_found_raises(self):
        with pytest.raises(ValueError, match="Item not found"):
            self.manager.delete_item("bad-id")

    def test_search_items(self):
        self.manager.create_item("Whole Milk")
        self.manager.create_item("Almond Milk")
        self.manager.create_item("Bread")
        results = self.manager.search_items("milk")
        assert len(results) == 2

    def test_search_items_no_match(self):
        self.manager.create_item("Bread")
        results = self.manager.search_items("cheese")
        assert len(results) == 0

    def test_get_items_by_category(self):
        self.manager.create_item("Milk", "Dairy")
        self.manager.create_item("Cheese", "Dairy")
        self.manager.create_item("Bread", "Bakery")
        results = self.manager.get_items_by_category("Dairy")
        assert len(results) == 2

    def test_get_summary(self):
        self.manager.create_item("Milk", "Dairy")
        self.manager.create_item("Bread", "Bakery")
        self.manager.create_item("Cheese", "Dairy")
        summary = self.manager.get_summary()
        assert summary["total_items"] == 3
        assert summary["categories"]["Dairy"] == 2
        assert summary["categories"]["Bakery"] == 1

    def test_get_summary_empty(self):
        summary = self.manager.get_summary()
        assert summary["total_items"] == 0
        assert summary["categories"] == {}

    def test_name_strips_whitespace(self):
        item = self.manager.create_item("  Milk  ")
        assert item["name"] == "Milk"
