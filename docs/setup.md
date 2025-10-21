# Setup Guide

## Prerequisites

- Python 3.11
- [Poetry](https://python-poetry.org/docs/) 1.5 or newer

## Installation

```bash
poetry install
```

This installs the core runtime dependencies (`langgraph`, `langchain`, `pydantic`, `requests`)
and the testing tools (`pytest`).

## Running Tests

```bash
poetry run pytest
```

## Command Line Interface

```bash
poetry run python -m mark_lang.ui.cli path/to/brief.txt --brand dnb --guidelines ./guidelines.json
```

The CLI prints missing-information prompts followed by the generated campaign plan. Provide a
JSON file mapping brand identifiers to tone-of-voice, visual-style, and compliance entries to
mirror the Brand Centre configuration.
