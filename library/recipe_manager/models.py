"""
models.py - Data models for recipes and ingredients.

Provides Ingredient and Recipe classes with serialisation support
and validation-ready structure.
"""

import uuid
from datetime import datetime

# Allowed recipe categories
VALID_CATEGORIES = ["breakfast", "lunch", "dinner", "snack", "dessert"]


class Ingredient:
    """Represents a single ingredient with quantity and unit."""

    def __init__(self, name: str, quantity: float, unit: str):
        """
        Initialise an Ingredient.

        Args:
            name: Ingredient name (e.g. 'flour').
            quantity: Numeric amount (must be positive).
            unit: Measurement unit (e.g. 'grams', 'cups').

        Raises:
            ValueError: If name/unit is empty or quantity is not positive.
        """
        if not name or not name.strip():
            raise ValueError("Ingredient name cannot be empty.")
        if quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        if not unit or not unit.strip():
            raise ValueError("Unit cannot be empty.")

        self.name = name.strip()
        self.quantity = float(quantity)
        self.unit = unit.strip()

    def to_dict(self) -> dict:
        """Serialise the ingredient to a dictionary."""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Ingredient":
        """
        Create an Ingredient from a dictionary.

        Args:
            data: Dict with keys 'name', 'quantity', 'unit'.

        Returns:
            A new Ingredient instance.
        """
        return cls(
            name=data["name"],
            quantity=data["quantity"],
            unit=data["unit"],
        )

    def __repr__(self) -> str:
        return f"Ingredient(name='{self.name}', quantity={self.quantity}, unit='{self.unit}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ingredient):
            return False
        return (self.name == other.name
                and self.quantity == other.quantity
                and self.unit == other.unit)


class Recipe:
    """Represents a complete recipe with metadata, ingredients, and instructions."""

    def __init__(
        self,
        title: str,
        description: str,
        category: str,
        ingredients: list,
        instructions: list,
        prep_time: int = 0,
        cook_time: int = 0,
        servings: int = 1,
        image_url: str = "",
        detected_labels: list = None,
        recipe_id: str = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        """
        Initialise a Recipe.

        Args:
            title: Recipe title.
            description: Short description.
            category: One of VALID_CATEGORIES.
            ingredients: List of Ingredient objects or dicts.
            instructions: List of instruction strings.
            prep_time: Preparation time in minutes.
            cook_time: Cooking time in minutes.
            servings: Number of servings.
            image_url: Optional URL to a recipe image.
            detected_labels: Optional list of image labels (e.g. from Rekognition).
            recipe_id: Unique ID (auto-generated if omitted).
            created_at: ISO timestamp (auto-generated if omitted).
            updated_at: ISO timestamp (auto-generated if omitted).
        """
        self.recipe_id = recipe_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.category = category.lower()
        self.instructions = instructions
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.servings = servings
        self.image_url = image_url
        self.detected_labels = detected_labels or []

        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

        # Accept both Ingredient objects and raw dicts
        self.ingredients = []
        for item in ingredients:
            if isinstance(item, Ingredient):
                self.ingredients.append(item)
            elif isinstance(item, dict):
                self.ingredients.append(Ingredient.from_dict(item))
            else:
                raise TypeError("Ingredients must be Ingredient instances or dicts.")

    @property
    def total_time(self) -> int:
        """Return total time (prep + cook) in minutes."""
        return self.prep_time + self.cook_time

    def to_dict(self) -> dict:
        """Serialise the recipe to a dictionary."""
        return {
            "recipe_id": self.recipe_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "ingredients": [i.to_dict() for i in self.ingredients],
            "instructions": self.instructions,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "servings": self.servings,
            "total_time": self.total_time,
            "image_url": self.image_url,
            "detected_labels": self.detected_labels,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """
        Create a Recipe from a dictionary.

        Args:
            data: Dict containing recipe fields.

        Returns:
            A new Recipe instance.
        """
        return cls(
            recipe_id=data.get("recipe_id"),
            title=data["title"],
            description=data.get("description", ""),
            category=data["category"],
            ingredients=data.get("ingredients", []),
            instructions=data.get("instructions", []),
            prep_time=data.get("prep_time", 0),
            cook_time=data.get("cook_time", 0),
            servings=data.get("servings", 1),
            image_url=data.get("image_url", ""),
            detected_labels=data.get("detected_labels", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return f"Recipe(title='{self.title}', category='{self.category}')"
