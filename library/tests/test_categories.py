"""Tests for CategoryClassifier."""

import pytest
from pantry_manager.categories import CategoryClassifier


class TestCategoryClassifier:
    def setup_method(self):
        self.classifier = CategoryClassifier()

    def test_classify_fruit(self):
        assert self.classifier.classify("Apple") == "Fruit"
        assert self.classifier.classify("Banana") == "Fruit"

    def test_classify_vegetable(self):
        assert self.classifier.classify("Carrot") == "Vegetable"
        assert self.classifier.classify("Broccoli") == "Vegetable"

    def test_classify_dairy(self):
        assert self.classifier.classify("Milk") == "Dairy"
        assert self.classifier.classify("Cheese") == "Dairy"

    def test_classify_meat(self):
        assert self.classifier.classify("Chicken breast") == "Meat"

    def test_classify_bakery(self):
        assert self.classifier.classify("Sourdough bread") == "Bakery"

    def test_classify_beverage(self):
        assert self.classifier.classify("Coffee drink") == "Beverage"

    def test_classify_snack(self):
        assert self.classifier.classify("Chocolate bar") == "Snack"

    def test_classify_grain(self):
        assert self.classifier.classify("Brown rice") == "Grain"

    def test_classify_other(self):
        assert self.classifier.classify("XYZ Unknown Item") == "Other"

    def test_classify_case_insensitive(self):
        assert self.classifier.classify("APPLE") == "Fruit"
        assert self.classifier.classify("milk") == "Dairy"

    def test_classify_from_labels(self):
        labels = ["Food", "Apple", "Fruit"]
        assert self.classifier.classify_from_labels(labels) == "Fruit"

    def test_classify_from_labels_no_match(self):
        labels = ["Object", "Indoor", "Table"]
        assert self.classifier.classify_from_labels(labels) == "Other"

    def test_get_all_categories(self):
        cats = self.classifier.get_all_categories()
        assert "Fruit" in cats
        assert "Other" in cats
        assert len(cats) == 9

    def test_get_keywords(self):
        keywords = self.classifier.get_keywords("Fruit")
        assert "apple" in keywords
        assert len(keywords) > 0

    def test_get_keywords_invalid(self):
        keywords = self.classifier.get_keywords("NonExistent")
        assert keywords == []
