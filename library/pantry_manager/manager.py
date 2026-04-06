"""Pantry item management utilities."""

import uuid
from datetime import datetime


class PantryManager:
    """Manages pantry items with validation and CRUD operations."""

    VALID_UNITS = ["pcs", "kg", "g", "L", "ml", "dozen", "pack", "bottle", "can", "box"]

    def __init__(self):
        self.items = []

    def create_item(self, name, category="Other", quantity=1, unit="pcs", expiry_date="", image_url=""):
        """Create a new pantry item with validation."""
        if not name or not name.strip():
            raise ValueError("Item name is required")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        if unit not in self.VALID_UNITS:
            raise ValueError(f"Invalid unit. Must be one of: {', '.join(self.VALID_UNITS)}")

        if expiry_date:
            try:
                datetime.strptime(expiry_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Expiry date must be in YYYY-MM-DD format")

        item = {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "category": category,
            "quantity": int(quantity),
            "unit": unit,
            "expiry_date": expiry_date,
            "image_url": image_url,
            "created_at": datetime.now().isoformat(),
        }
        self.items.append(item)
        return item

    def get_item(self, item_id):
        """Get item by ID."""
        for item in self.items:
            if item["id"] == item_id:
                return item
        return None

    def update_item(self, item_id, **kwargs):
        """Update an existing item."""
        item = self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")

        if "quantity" in kwargs and kwargs["quantity"] < 0:
            raise ValueError("Quantity cannot be negative")

        if "unit" in kwargs and kwargs["unit"] not in self.VALID_UNITS:
            raise ValueError(f"Invalid unit")

        for key, value in kwargs.items():
            if key in item and key != "id":
                item[key] = value
        return item

    def delete_item(self, item_id):
        """Delete an item by ID."""
        item = self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")
        self.items.remove(item)
        return True

    def search_items(self, query):
        """Search items by name."""
        query = query.lower()
        return [item for item in self.items if query in item["name"].lower()]

    def get_items_by_category(self, category):
        """Get all items in a category."""
        return [item for item in self.items if item["category"] == category]

    def get_summary(self):
        """Get pantry summary statistics."""
        categories = {}
        for item in self.items:
            cat = item["category"]
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_items": len(self.items),
            "categories": categories,
        }
