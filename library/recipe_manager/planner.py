"""
planner.py - Meal planning and shopping list utilities.

Provides the MealPlanner class for generating weekly meal plans,
aggregating shopping lists, and filtering recipe suggestions.
"""

import random


class MealPlanner:
    """Generates meal plans, shopping lists, and recipe suggestions."""

    DAYS_OF_WEEK = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]

    def generate_weekly_plan(self, recipes: list, meals_per_day: int = 3) -> dict:
        """
        Randomly assign recipes to each day of the week.

        Args:
            recipes: List of Recipe objects to choose from.
            meals_per_day: Number of meals per day (default 3).

        Returns:
            Dict mapping day name to a list of Recipe objects.

        Raises:
            ValueError: If the recipe list is empty.
        """
        if not recipes:
            raise ValueError("At least one recipe is required to generate a plan.")

        plan = {}
        for day in self.DAYS_OF_WEEK:
            plan[day] = random.choices(recipes, k=meals_per_day)
        return plan

    def get_shopping_list(self, recipes: list) -> dict:
        """
        Aggregate ingredients across multiple recipes.

        Ingredients with the same name and unit are combined by quantity.

        Args:
            recipes: List of Recipe objects.

        Returns:
            Dict keyed by ingredient name, value is dict with 'quantity' and 'unit'.
        """
        shopping = {}
        for recipe in recipes:
            for ing in recipe.ingredients:
                key = (ing.name.lower(), ing.unit.lower())
                if key in shopping:
                    shopping[key]["quantity"] += ing.quantity
                else:
                    shopping[key] = {
                        "name": ing.name,
                        "quantity": ing.quantity,
                        "unit": ing.unit,
                    }
        return {v["name"]: {"quantity": round(v["quantity"], 2), "unit": v["unit"]}
                for v in shopping.values()}

    def suggest_recipes(
        self,
        recipes: list,
        category: str = None,
        max_time: int = None,
    ) -> list:
        """
        Filter recipes by category and / or maximum total time.

        Args:
            recipes: List of Recipe objects.
            category: Optional category string to filter by.
            max_time: Optional maximum total_time in minutes.

        Returns:
            List of matching Recipe objects.
        """
        results = recipes

        if category:
            results = [r for r in results if r.category == category.lower()]

        if max_time is not None:
            results = [r for r in results if r.total_time <= max_time]

        return results
