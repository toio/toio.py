# Contributing to toio.py

Welcome to toio.py! We appreciate your interest in contributing to our project.
Before contributing to toio.py, please read our [Code of Conduct](./CODE_OF_CONDUCT.md)

## Getting started with development

### Setup

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

2. Clone the toio.py repository

```
git clone https://github.com/toio/toio.py
```

3. Run `uv sync` in toio.py repository

```
cd toio.py
uv sync
```

### Lint and format

#### Mandatory:

[`black`](https://black.readthedocs.io/en/stable/) and [`isort`](https://pycqa.github.io/isort/) is used in this project.

```
uv run black
uv run isort
```

#### Optional:

Checking with [`flake8`](https://flake8.pycqa.org/en/latest/) or [`mypy`](https://www.mypy-lang.org/) is recommended.

```
uv run flake8
```

```
uv run mypy
```


### 


## License

By contributing your code,
- you agree to license your contribution under the MIT License; and
- you represent that (i) your contribution is entirely your original work, and (ii) you are legally entitled to make your contribution.
Please note if your employer has rights to intellectual property in your contribution, partially or wholly, you must secure permission from your employer to make your contribution on behalf of that employer before submitting your contribution.
