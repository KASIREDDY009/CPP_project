"""
formatter.py - Output formatting for recipes.

Provides the RecipeFormatter class to render a Recipe object as
plain text, HTML, JSON, or a short summary string.
"""

import json


class RecipeFormatter:
    """Formats Recipe objects into various output representations."""

    def to_text(self, recipe) -> str:
        """
        Render a recipe as readable plain text.

        Args:
            recipe: A Recipe object.

        Returns:
            Multi-line plain text string.
        """
        lines = [
            recipe.title.upper(),
            "=" * len(recipe.title),
            "",
            recipe.description,
            "",
            f"Category : {recipe.category.capitalize()}",
            f"Prep time: {recipe.prep_time} min",
            f"Cook time: {recipe.cook_time} min",
            f"Total    : {recipe.total_time} min",
            f"Servings : {recipe.servings}",
            "",
            "INGREDIENTS",
            "-----------",
        ]
        for ing in recipe.ingredients:
            lines.append(f"  - {ing.quantity} {ing.unit} {ing.name}")

        lines.append("")
        lines.append("INSTRUCTIONS")
        lines.append("------------")
        for idx, step in enumerate(recipe.instructions, start=1):
            lines.append(f"  {idx}. {step}")

        return "\n".join(lines)

    def to_html(self, recipe) -> str:
        """
        Render a recipe as an HTML card.

        Args:
            recipe: A Recipe object.

        Returns:
            HTML string.
        """
        ingredients_html = "\n".join(
            f"    <li>{ing.quantity} {ing.unit} {ing.name}</li>"
            for ing in recipe.ingredients
        )
        instructions_html = "\n".join(
            f"    <li>{step}</li>"
            for step in recipe.instructions
        )

        return f"""<div class="recipe-card">
  <h2>{recipe.title}</h2>
  <p class="description">{recipe.description}</p>
  <p><strong>Category:</strong> {recipe.category.capitalize()}</p>
  <p><strong>Prep:</strong> {recipe.prep_time} min | <strong>Cook:</strong> {recipe.cook_time} min | <strong>Total:</strong> {recipe.total_time} min</p>
  <p><strong>Servings:</strong> {recipe.servings}</p>
  <h3>Ingredients</h3>
  <ul>
{ingredients_html}
  </ul>
  <h3>Instructions</h3>
  <ol>
{instructions_html}
  </ol>
</div>"""

    def to_json(self, recipe) -> str:
        """
        Serialise a recipe to a JSON string.

        Args:
            recipe: A Recipe object.

        Returns:
            Pretty-printed JSON string.
        """
        return json.dumps(recipe.to_dict(), indent=2)

    def summary(self, recipe) -> str:
        """
        Return a one-line summary of a recipe.

        Args:
            recipe: A Recipe object.

        Returns:
            Summary string, e.g. 'Pancakes (breakfast) - 30 min, 4 servings'.
        """
        return (
            f"{recipe.title} ({recipe.category}) "
            f"- {recipe.total_time} min, {recipe.servings} servings"
        )
