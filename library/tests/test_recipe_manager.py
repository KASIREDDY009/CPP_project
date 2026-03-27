"""
test_recipe_manager.py - Unit tests for the recipe_manager library.

Run with: pytest tests/test_recipe_manager.py -v
"""

import json
import sys
import os

# Ensure the library package is importable when running from the library dir
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from recipe_manager.models import Ingredient, Recipe, VALID_CATEGORIES
from recipe_manager.validator import RecipeValidator
from recipe_manager.nutrition import NutritionEstimator
from recipe_manager.planner import MealPlanner
from recipe_manager.formatter import RecipeFormatter


# ------------------------------------------------------------------ #
#  Helpers - reusable fixtures
# ------------------------------------------------------------------ #

def _sample_ingredient(name="flour", quantity=200, unit="grams"):
    return Ingredient(name=name, quantity=quantity, unit=unit)


def _sample_recipe(**overrides):
    defaults = {
        "title": "Pancakes",
        "description": "Fluffy pancakes",
        "category": "breakfast",
        "ingredients": [
            {"name": "flour", "quantity": 200, "unit": "grams"},
            {"name": "egg", "quantity": 2, "unit": "whole"},
            {"name": "milk", "quantity": 300, "unit": "ml"},
        ],
        "instructions": ["Mix ingredients", "Cook on skillet"],
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
    }
    defaults.update(overrides)
    return Recipe(**defaults)


# ================================================================== #
#  Ingredient tests
# ================================================================== #

class TestIngredient:
    def test_creation(self):
        ing = _sample_ingredient()
        assert ing.name == "flour"
        assert ing.quantity == 200
        assert ing.unit == "grams"

    def test_invalid_empty_name(self):
        try:
            Ingredient("", 1, "g")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_invalid_negative_quantity(self):
        try:
            Ingredient("flour", -1, "g")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_to_dict_and_from_dict(self):
        ing = _sample_ingredient()
        d = ing.to_dict()
        restored = Ingredient.from_dict(d)
        assert ing == restored

    def test_repr(self):
        ing = _sample_ingredient()
        assert "flour" in repr(ing)


# ================================================================== #
#  Recipe tests
# ================================================================== #

class TestRecipe:
    def test_creation_with_dicts(self):
        recipe = _sample_recipe()
        assert recipe.title == "Pancakes"
        assert len(recipe.ingredients) == 3
        assert isinstance(recipe.ingredients[0], Ingredient)

    def test_creation_with_objects(self):
        recipe = _sample_recipe(
            ingredients=[_sample_ingredient("butter", 50, "grams")]
        )
        assert recipe.ingredients[0].name == "butter"

    def test_total_time(self):
        recipe = _sample_recipe(prep_time=10, cook_time=20)
        assert recipe.total_time == 30

    def test_to_dict_and_from_dict(self):
        recipe = _sample_recipe()
        d = recipe.to_dict()
        restored = Recipe.from_dict(d)
        assert restored.title == recipe.title
        assert restored.recipe_id == recipe.recipe_id

    def test_categories_list(self):
        assert "breakfast" in VALID_CATEGORIES
        assert "dessert" in VALID_CATEGORIES


# ================================================================== #
#  Validator tests
# ================================================================== #

class TestRecipeValidator:
    def setup_method(self):
        self.v = RecipeValidator()

    def test_valid_recipe(self):
        data = _sample_recipe().to_dict()
        is_valid, errors = self.v.validate_recipe(data)
        assert is_valid is True
        assert errors == []

    def test_missing_title(self):
        data = _sample_recipe().to_dict()
        data["title"] = ""
        is_valid, errors = self.v.validate_recipe(data)
        assert is_valid is False
        assert any("Title" in e for e in errors)

    def test_invalid_category(self):
        valid, msg = self.v.validate_category("brunch")
        assert valid is False

    def test_valid_category(self):
        valid, msg = self.v.validate_category("lunch")
        assert valid is True

    def test_validate_ingredient_valid(self):
        valid, errs = self.v.validate_ingredient(
            {"name": "salt", "quantity": 5, "unit": "grams"}
        )
        assert valid is True

    def test_validate_ingredient_invalid(self):
        valid, errs = self.v.validate_ingredient(
            {"name": "", "quantity": -1, "unit": ""}
        )
        assert valid is False
        assert len(errs) == 3

    def test_sanitize_input_strips_tags(self):
        dirty = '<script>alert("xss")</script>Hello'
        assert self.v.sanitize_input(dirty) == 'alert("xss")Hello'

    def test_sanitize_input_html(self):
        assert self.v.sanitize_input("<b>Bold</b>") == "Bold"

    def test_sanitize_non_string(self):
        assert self.v.sanitize_input(123) == ""


# ================================================================== #
#  Nutrition tests
# ================================================================== #

class TestNutritionEstimator:
    def setup_method(self):
        self.ne = NutritionEstimator()

    def test_estimate_calories(self):
        ingredients = [{"name": "rice", "quantity": 200, "unit": "grams"}]
        cal = self.ne.estimate_calories(ingredients)
        assert cal == 260.0  # 130 cal/100g * 2

    def test_unknown_ingredient_zero(self):
        cal = self.ne.estimate_calories([{"name": "unobtainium", "quantity": 100, "unit": "grams"}])
        assert cal == 0.0

    def test_nutrition_summary_keys(self):
        ingredients = [_sample_ingredient("chicken", 100, "grams")]
        summary = self.ne.get_nutrition_summary(ingredients)
        assert "calories" in summary
        assert "protein" in summary
        assert "carbs" in summary
        assert "fat" in summary

    def test_categorize_light(self):
        assert self.ne.categorize_recipe(150) == "light"

    def test_categorize_moderate(self):
        assert self.ne.categorize_recipe(450) == "moderate"

    def test_categorize_hearty(self):
        assert self.ne.categorize_recipe(800) == "hearty"


# ================================================================== #
#  Planner tests
# ================================================================== #

class TestMealPlanner:
    def setup_method(self):
        self.mp = MealPlanner()
        self.recipes = [_sample_recipe(), _sample_recipe(title="Salad", category="lunch")]

    def test_weekly_plan_has_seven_days(self):
        plan = self.mp.generate_weekly_plan(self.recipes)
        assert len(plan) == 7

    def test_weekly_plan_meals_per_day(self):
        plan = self.mp.generate_weekly_plan(self.recipes, meals_per_day=2)
        for day_meals in plan.values():
            assert len(day_meals) == 2

    def test_empty_recipes_raises(self):
        try:
            self.mp.generate_weekly_plan([])
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_shopping_list_aggregation(self):
        shopping = self.mp.get_shopping_list(self.recipes)
        # Both recipes have flour 200g, should aggregate to 400g
        assert shopping["flour"]["quantity"] == 400

    def test_suggest_by_category(self):
        results = self.mp.suggest_recipes(self.recipes, category="lunch")
        assert all(r.category == "lunch" for r in results)

    def test_suggest_by_max_time(self):
        results = self.mp.suggest_recipes(self.recipes, max_time=25)
        assert results == []  # both are 30 min total


# ================================================================== #
#  Formatter tests
# ================================================================== #

class TestRecipeFormatter:
    def setup_method(self):
        self.fmt = RecipeFormatter()
        self.recipe = _sample_recipe()

    def test_to_text(self):
        text = self.fmt.to_text(self.recipe)
        assert "PANCAKES" in text
        assert "flour" in text

    def test_to_html(self):
        html = self.fmt.to_html(self.recipe)
        assert "<h2>Pancakes</h2>" in html
        assert "recipe-card" in html

    def test_to_json_valid(self):
        j = self.fmt.to_json(self.recipe)
        data = json.loads(j)
        assert data["title"] == "Pancakes"

    def test_summary(self):
        s = self.fmt.summary(self.recipe)
        assert "Pancakes" in s
        assert "breakfast" in s
        assert "30 min" in s
