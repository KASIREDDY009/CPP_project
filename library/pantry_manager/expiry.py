"""Expiry date tracking and notification utilities."""

from datetime import datetime, timedelta


class ExpiryTracker:
    """Tracks food item expiry dates and generates alerts."""

    def __init__(self, days_threshold=3):
        self.days_threshold = days_threshold

    def check_expiry(self, items, days_threshold=None):
        """Check items for expiry status.

        Returns dict with 'expired', 'expiring_soon', and 'fresh' lists.
        """
        threshold = days_threshold or self.days_threshold
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff = today + timedelta(days=threshold)

        result = {"expired": [], "expiring_soon": [], "fresh": []}

        for item in items:
            expiry = item.get("expiry_date", "")
            if not expiry:
                result["fresh"].append(item)
                continue

            try:
                exp_date = datetime.strptime(expiry, "%Y-%m-%d")
                if exp_date < today:
                    result["expired"].append(item)
                elif exp_date <= cutoff:
                    result["expiring_soon"].append(item)
                else:
                    result["fresh"].append(item)
            except ValueError:
                result["fresh"].append(item)

        return result

    def get_days_until_expiry(self, expiry_date):
        """Get number of days until an item expires."""
        if not expiry_date:
            return None
        try:
            exp = datetime.strptime(expiry_date, "%Y-%m-%d")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return (exp - today).days
        except ValueError:
            return None

    def format_expiry_message(self, items):
        """Format a notification message for expiring items."""
        result = self.check_expiry(items)
        parts = []

        if result["expired"]:
            names = [i["name"] for i in result["expired"]]
            parts.append(f"EXPIRED: {', '.join(names)}")

        if result["expiring_soon"]:
            names = [i["name"] for i in result["expiring_soon"]]
            parts.append(f"Expiring soon: {', '.join(names)}")

        if not parts:
            return "All items are fresh!"

        return "\n".join(parts)

    def is_expired(self, expiry_date):
        """Check if a specific date has passed."""
        days = self.get_days_until_expiry(expiry_date)
        if days is None:
            return False
        return days < 0
