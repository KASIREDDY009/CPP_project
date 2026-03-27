"""Setup script for the recipe-manager-nci package."""

from setuptools import setup, find_packages

setup(
    name="recipe-manager-nci",
    version="1.0.0",
    author="Kasi Reddy",
    author_email="kasi.reddy@example.com",
    description="A comprehensive recipe management library for cloud-based applications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kasi-reddy/recipe-manager-nci",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
