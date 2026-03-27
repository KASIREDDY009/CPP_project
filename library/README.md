# recipe-manager-nci

A comprehensive recipe management library for cloud-based applications.

## Features

- **Models** - `Ingredient` and `Recipe` data classes with serialisation support
- **Validation** - Input validation and HTML/script tag sanitisation
- **Nutrition** - Calorie and macronutrient estimation from ingredient lists
- **Meal Planning** - Weekly plan generation, shopping list aggregation, and recipe suggestions
- **Formatting** - Output recipes as plain text, HTML, JSON, or one-line summaries

## Installation

```bash
pip install recipe-manager-nci
```

## Quick Start

```python
from recipe_manager import Recipe, NutritionEstimator, RecipeFormatter

recipe = Recipe(
    title="Pancakes",
    description="Fluffy breakfast pancakes",
    category="breakfast",
    ingredients=[
        {"name": "flour", "quantity": 200, "unit": "grams"},
        {"name": "egg", "quantity": 2, "unit": "whole"},
        {"name": "milk", "quantity": 300, "unit": "ml"},
    ],
    instructions=["Mix ingredients", "Cook on skillet"],
    prep_time=10,
    cook_time=20,
    servings=4,
)

estimator = NutritionEstimator()
print(estimator.get_nutrition_summary(recipe.ingredients))

formatter = RecipeFormatter()
print(formatter.to_text(recipe))
```

## Running Tests

```bash
pytest tests/ -v
```

## Author

Kasi Reddy

## License

MIT
