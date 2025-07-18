- Author: Alexander Stevens
- Date: Saturday, July 18, 2025  10:13:00 PM
- Forked from Hugh Alessi: https://github.com/halessi/DCF

# Financial Forecasting Project

A Python-based Discounted Cash Flow (DCF) analysis tool that automatically fetches financial data and calculates intrinsic stock valuations.
Uses primitive underlying DCF modeling to compare intrinsic per share price to current share price.

## What I've Already Done in This Project

### Code Quality & Development Setup
- **Set up pre-commit hooks** with comprehensive code quality checks:
  - **Ruff** for fast Python linting and formatting
  - **Automatic code formatting** on every commit
  - **Import sorting** and **trailing whitespace** cleanup
  - **YAML validation** and **large file detection**
  - **End-of-file** fixers

### Code Improvements
- **Fixed all linting issues** across the codebase:
  - Removed star imports (`from ... import *`) and replaced with explicit imports
  - Fixed function and variable naming to follow PEP8 (snake_case)
  - Resolved long lines (E501) by breaking up docstrings and comments
  - Fixed bare except statements with specific exception handling
  - Updated variable names to lowercase (e.g., `PV_flow` → `pv_flow`)
  - Suppressed appropriate warnings for financial modeling functions

### Project Structure
```
financial_forecasting/
├── app/
│   ├── main.py              # Main application entry point
│   ├── modeling/
│   │   ├── data.py          # Financial data fetching from APIs
│   │   └── dcf.py           # DCF calculation logic
│   └── visualization/
│       ├── plot.py          # Data visualization functions
│       └── printouts.py     # Formatted output functions
├── .pre-commit-config.yaml  # Pre-commit configuration
├── ruff.toml               # Ruff linting configuration
└── pyproject.toml          # Project dependencies
```

## Setup

### Prerequisites
- Python 3.8+
- Financial Modeling Prep API key (free tier available)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -e .` or `uv sync`
3. Set up pre-commit: `pre-commit install`
4. Set your API key: `export APIKEY=your_api_key_here`

### Development
- **Pre-commit hooks** run automatically on every commit
- **Ruff** provides fast linting and formatting
- **Code quality** is enforced through automated checks

## API Key

Get a free API key from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/).

## License

This project is forked from the original DCF project by Hugh Alessi. See the original repository for licensing information.
