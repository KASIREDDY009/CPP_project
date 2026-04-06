# pantry-manager-nci

Kitchen inventory management utilities for SmartPantry application.

## Features
- Pantry item validation and management
- Expiry date tracking and alerts
- Food category classification
- Nutrition label detection helpers

## Installation
```bash
pip install pantry-manager-nci
```

## Usage
```python
from pantry_manager import PantryManager, ExpiryTracker

manager = PantryManager()
item = manager.create_item("Milk", "Dairy", quantity=2, unit="L", expiry_date="2026-04-15")

tracker = ExpiryTracker()
expiring = tracker.check_expiry([item], days_threshold=3)
```
