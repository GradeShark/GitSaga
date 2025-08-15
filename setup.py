"""
GitSaga - Development Context Manager
Track the story behind your code
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="gitsaga",
    version="0.1.0",
    author="GitSaga Developer",
    description="Track the story behind your code - Development context manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/gitsaga",  # Replace YOUR_USERNAME
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.7",
        "gitpython>=3.1.40",
        "rich>=13.5.2",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "saga=gitsaga.cli_wrapper:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/YOUR_USERNAME/gitsaga/issues",  # Replace YOUR_USERNAME
        "Source": "https://github.com/YOUR_USERNAME/gitsaga",  # Replace YOUR_USERNAME
    },
)