"""
recipe_manager - A comprehensive recipe management library for cloud-based applications.

This library provides OOP tools for managing recipes, validating input,
estimating nutrition, planning meals, and formatting recipe output.
"""

from recipe_manager.models import Ingredient, Recipe
from recipe_manager.validator import RecipeValidator
from recipe_manager.nutrition import NutritionEstimator
from recipe_manager.planner import MealPlanner
from recipe_manager.formatter import RecipeFormatter

__version__ = "1.0.0"
__author__ = "Kasi Reddy"

__all__ = [
    "Ingredient",
    "Recipe",
    "RecipeValidator",
    "NutritionEstimator",
    "MealPlanner",
    "RecipeFormatter",
]
