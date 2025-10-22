# Mark Lang

Mark Lang is a modular toolkit for transforming business briefs into compliant creative
campaign plans. The project demonstrates how to combine brief ingestion, structured data
extraction, brand governance, and agentic workflows into a single developer experience.

## Documentation

- [Architecture](docs/architecture.md)
- [Setup Guide](docs/setup.md)
- [Operations Runbook](docs/operations.md)
- [Enablement Workshop](docs/workshop.md)
- [Brand Document Ingestion](docs/brand_document_ingestion.md)

## Quick Start

```bash
poetry install
poetry run pytest
poetry run python -m mark_lang.ui.cli examples/brief.txt --brand dnb
```

### Extract Brand Guidelines from Documents

Process Norwegian marketing documents to extract brand guidelines:

```bash
poetry run python -m mark_lang.ingest_brand_documents "path/to/documents" --save-translated
```

See the [Brand Document Ingestion Guide](docs/brand_document_ingestion.md) for details.

See the setup guide for CLI options and integration details.
