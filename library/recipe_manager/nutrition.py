"""
nutrition.py - Approximate nutrition estimation for recipes.

Uses a built-in lookup table of common ingredients to provide
calorie and macronutrient estimates. Values are approximate and
intended for informational purposes only.
"""


class NutritionEstimator:
    """Estimates nutritional information from a list of ingredients."""

    # Approximate values per 100 g: (calories, protein_g, carbs_g, fat_g)
    _NUTRITION_DB = {
        "flour":        (364, 10, 76, 1),
        "sugar":        (387, 0, 100, 0),
        "butter":       (717, 1, 0, 81),
        "egg":          (155, 13, 1, 11),
        "eggs":         (155, 13, 1, 11),
        "milk":         (42, 3, 5, 1),
        "rice":         (130, 3, 28, 0),
        "pasta":        (131, 5, 25, 1),
        "chicken":      (239, 27, 0, 14),
        "beef":         (250, 26, 0, 15),
        "salmon":       (208, 20, 0, 13),
        "potato":       (77, 2, 17, 0),
        "tomato":       (18, 1, 4, 0),
        "onion":        (40, 1, 9, 0),
        "garlic":       (149, 6, 33, 1),
        "olive oil":    (884, 0, 0, 100),
        "cheese":       (402, 25, 1, 33),
        "bread":        (265, 9, 49, 3),
        "carrot":       (41, 1, 10, 0),
        "broccoli":     (34, 3, 7, 0),
        "spinach":      (23, 3, 4, 0),
        "banana":       (89, 1, 23, 0),
        "apple":        (52, 0, 14, 0),
        "lemon":        (29, 1, 9, 0),
        "salt":         (0, 0, 0, 0),
        "pepper":       (251, 10, 64, 3),
        "cream":        (340, 2, 3, 36),
        "yogurt":       (59, 10, 4, 0),
        "honey":        (304, 0, 82, 0),
        "mushroom":     (22, 3, 3, 0),
        "shrimp":       (99, 24, 0, 0),
        "tofu":         (76, 8, 2, 5),
        "avocado":      (160, 2, 9, 15),
        "corn":         (86, 3, 19, 1),
        "beans":        (347, 21, 63, 1),
        "lentils":      (116, 9, 20, 0),
        "coconut milk": (230, 2, 6, 24),
        "soy sauce":    (53, 8, 5, 0),
    }

    # Rough conversion factors to grams for common units
    _UNIT_TO_GRAMS = {
        "g":          1,
        "grams":      1,
        "gram":       1,
        "kg":         1000,
        "ml":         1,
        "l":          1000,
        "litre":      1000,
        "litres":     1000,
        "cup":        240,
        "cups":       240,
        "tbsp":       15,
        "tablespoon": 15,
        "tsp":        5,
        "teaspoon":   5,
        "oz":         28,
        "ounce":      28,
        "lb":         454,
        "pound":      454,
        "piece":      100,
        "pieces":     100,
        "whole":      100,
        "slice":      30,
        "slices":     30,
        "clove":      5,
        "cloves":     5,
        "pinch":      1,
    }

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def estimate_calories(self, ingredients: list) -> float:
        """
        Estimate total calories for a list of ingredients.

        Args:
            ingredients: List of Ingredient objects or dicts with
                         'name', 'quantity', 'unit'.

        Returns:
            Estimated total calories (float).
        """
        total = 0.0
        for ing in ingredients:
            name, qty, unit = self._extract(ing)
            grams = self._to_grams(qty, unit)
            cal_per_100 = self._lookup(name)[0]
            total += cal_per_100 * (grams / 100)
        return round(total, 1)

    def get_nutrition_summary(self, ingredients: list) -> dict:
        """
        Return a macronutrient summary for a list of ingredients.

        Args:
            ingredients: List of Ingredient objects or dicts.

        Returns:
            Dict with keys 'calories', 'protein', 'carbs', 'fat'.
        """
        totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        for ing in ingredients:
            name, qty, unit = self._extract(ing)
            grams = self._to_grams(qty, unit)
            cal, protein, carbs, fat = self._lookup(name)
            factor = grams / 100
            totals["calories"] += cal * factor
            totals["protein"] += protein * factor
            totals["carbs"] += carbs * factor
            totals["fat"] += fat * factor

        # Round everything
        return {k: round(v, 1) for k, v in totals.items()}

    def categorize_recipe(self, calories: float) -> str:
        """
        Categorise a recipe by calorie count.

        Args:
            calories: Total estimated calories.

        Returns:
            'light' (< 300), 'moderate' (300-600), or 'hearty' (> 600).
        """
        if calories < 300:
            return "light"
        elif calories <= 600:
            return "moderate"
        else:
            return "hearty"

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _extract(self, ingredient) -> tuple:
        """Return (name, quantity, unit) from an Ingredient or dict."""
        if isinstance(ingredient, dict):
            return ingredient["name"], ingredient["quantity"], ingredient["unit"]
        return ingredient.name, ingredient.quantity, ingredient.unit

    def _to_grams(self, quantity: float, unit: str) -> float:
        """Convert a quantity + unit to approximate grams."""
        factor = self._UNIT_TO_GRAMS.get(unit.lower(), 100)
        return quantity * factor

    def _lookup(self, name: str) -> tuple:
        """Look up nutrition data; return zeros if ingredient is unknown."""
        key = name.lower().strip()
        return self._NUTRITION_DB.get(key, (0, 0, 0, 0))
