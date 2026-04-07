from setuptools import setup, find_packages

setup(
    name="recipe-manager-nci",
    version="1.0.0",
    description="SmartPantry - Kitchen inventory management utilities for tracking food items, expiry dates, and categories",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kasireddy",
    author_email="kasireddy9424@gmail.com",
    url="https://github.com/KASIREDDY009/CPP_project",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.26.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
