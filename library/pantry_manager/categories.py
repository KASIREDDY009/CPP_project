"""Food category classification utilities."""


class CategoryClassifier:
    """Classifies food items into categories based on keywords and Rekognition labels."""

    CATEGORY_KEYWORDS = {
        "Fruit": ["apple", "banana", "orange", "grapes", "strawberry", "mango",
                   "pineapple", "watermelon", "lemon", "lime", "berry", "kiwi",
                   "peach", "pear", "cherry", "plum", "melon", "fruit"],
        "Vegetable": ["broccoli", "carrot", "tomato", "potato", "onion", "pepper",
                      "lettuce", "spinach", "cucumber", "cabbage", "corn", "peas",
                      "beans", "mushroom", "garlic", "celery", "vegetable"],
        "Dairy": ["milk", "cheese", "yogurt", "butter", "cream", "egg",
                  "curd", "paneer", "ghee", "dairy"],
        "Meat": ["chicken", "beef", "pork", "fish", "seafood", "steak",
                 "sausage", "bacon", "lamb", "turkey", "shrimp", "meat"],
        "Bakery": ["bread", "cake", "cookie", "pastry", "muffin", "croissant",
                   "bagel", "donut", "pie", "biscuit", "bakery"],
        "Beverage": ["juice", "water", "soda", "coffee", "tea", "wine",
                     "beer", "milk", "smoothie", "drink", "beverage"],
        "Snack": ["chips", "candy", "chocolate", "popcorn", "nuts", "crackers",
                  "granola", "pretzel", "trail mix", "snack"],
        "Grain": ["rice", "pasta", "cereal", "flour", "oats", "wheat",
                  "quinoa", "barley", "noodle", "grain"],
    }

    def classify(self, name):
        """Classify a food item by name into a category."""
        name_lower = name.lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        return "Other"

    def classify_from_labels(self, labels):
        """Classify from Rekognition labels list."""
        for label in labels:
            category = self.classify(label)
            if category != "Other":
                return category
        return "Other"

    def get_all_categories(self):
        """Return list of all valid categories."""
        return list(self.CATEGORY_KEYWORDS.keys()) + ["Other"]

    def get_keywords(self, category):
        """Get keywords for a specific category."""
        return self.CATEGORY_KEYWORDS.get(category, [])
