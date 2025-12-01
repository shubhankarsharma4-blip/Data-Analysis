#!/usr/bin/env python
"""Setup script for E-commerce ETL Project."""

from setuptools import setup, find_packages

setup(
    name="ecommerce-etl-project",
    version="1.0.0",
    description="Production-grade ETL pipeline for e-commerce data",
    author="E-commerce ETL Project Contributors",
    url="https://github.com/YOUR_USERNAME/ecommerce-etl-project",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "sqlalchemy>=2.0.0",
        "streamlit>=1.50.0",
        "plotly>=6.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ecommerce-etl=run_all:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
