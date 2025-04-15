#!/usr/bin/env python3
"""
Script de instalação para o LinkedIn Profile Hunter
"""

from setuptools import setup, find_packages

setup(
    name="linkedin-profile-hunter",
    version="0.1.0",
    description="Uma aplicação em Python que busca, analisa e extrai informações profissionais de uma pessoa a partir de dados básicos",
    author="Seu Nome",
    author_email="seu-email@exemplo.com",
    packages=find_packages(),
    install_requires=[
        "crawl4ai",
        "playwright",
        "pandas",
        "beautifulsoup4",
        "python-dotenv",
        "google-generativeai>=0.3.0",
        "fuzzywuzzy[speedup]",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "flake8",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
