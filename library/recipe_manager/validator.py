"""
validator.py - Input validation and sanitisation for recipe data.

Provides the RecipeValidator class to ensure data integrity before
persisting recipes to a database or returning them via an API.
"""

import re
from recipe_manager.models import VALID_CATEGORIES


class RecipeValidator:
    """Validates and sanitises recipe and ingredient data."""

    # Regex to strip HTML / script tags
    _TAG_PATTERN = re.compile(r"<[^>]+>")

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def validate_recipe(self, data: dict) -> tuple:
        """
        Validate a full recipe payload.

        Args:
            data: Dictionary of recipe fields.

        Returns:
            Tuple of (is_valid: bool, errors: list[str]).
        """
        errors = []

        # Title
        if not data.get("title") or not str(data["title"]).strip():
            errors.append("Title is required.")

        # Description (optional but must be string if present)
        if "description" in data and not isinstance(data["description"], str):
            errors.append("Description must be a string.")

        # Category
        cat_valid, cat_err = self.validate_category(data.get("category", ""))
        if not cat_valid:
            errors.append(cat_err)

        # Ingredients
        ingredients = data.get("ingredients", [])
        if not ingredients:
            errors.append("At least one ingredient is required.")
        else:
            for idx, ing in enumerate(ingredients):
                ing_valid, ing_errors = self.validate_ingredient(ing)
                if not ing_valid:
                    for e in ing_errors:
                        errors.append(f"Ingredient {idx + 1}: {e}")

        # Instructions
        instructions = data.get("instructions", [])
        if not instructions:
            errors.append("At least one instruction step is required.")

        # Numeric fields
        for field in ("prep_time", "cook_time", "servings"):
            value = data.get(field, 0)
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"{field} must be a non-negative number.")

        if data.get("servings", 1) < 1:
            errors.append("Servings must be at least 1.")

        return (len(errors) == 0, errors)

    def validate_ingredient(self, data: dict) -> tuple:
        """
        Validate a single ingredient dict.

        Args:
            data: Dict with 'name', 'quantity', 'unit'.

        Returns:
            Tuple of (is_valid: bool, errors: list[str]).
        """
        errors = []

        if not isinstance(data, dict):
            return (False, ["Ingredient must be a dictionary."])

        if not data.get("name") or not str(data["name"]).strip():
            errors.append("Name is required.")

        qty = data.get("quantity", None)
        if qty is None or not isinstance(qty, (int, float)) or qty <= 0:
            errors.append("Quantity must be a positive number.")

        if not data.get("unit") or not str(data["unit"]).strip():
            errors.append("Unit is required.")

        return (len(errors) == 0, errors)

    def validate_category(self, category: str) -> tuple:
        """
        Check that a category is in the allowed list.

        Args:
            category: Category string to validate.

        Returns:
            Tuple of (is_valid: bool, error_message: str | None).
        """
        if not category:
            return (False, "Category is required.")
        if category.lower() not in VALID_CATEGORIES:
            return (False, f"Category must be one of: {', '.join(VALID_CATEGORIES)}.")
        return (True, None)

    def sanitize_input(self, text: str) -> str:
        """
        Strip HTML and script tags from user-supplied text.

        Args:
            text: Raw input string.

        Returns:
            Sanitised string with all HTML tags removed.
        """
        if not isinstance(text, str):
            return ""
        return self._TAG_PATTERN.sub("", text).strip()
