# Mark Lang

Mark Lang is a modular toolkit for transforming business briefs into compliant creative
campaign plans. The project demonstrates how to combine brief ingestion, structured data
extraction, brand governance, and agentic workflows into a single developer experience.

## Documentation

- [Architecture](docs/architecture.md)
- [Setup Guide](docs/setup.md)
- [Operations Runbook](docs/operations.md)
- [Enablement Workshop](docs/workshop.md)

## Quick Start

```bash
poetry install
poetry run pytest
poetry run python -m mark_lang.ui.cli examples/brief.txt --brand dnb
```

See the setup guide for CLI options and integration details.
