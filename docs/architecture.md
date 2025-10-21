# Architecture Overview

The Mark Lang toolkit is organized into modular components that collaborate to ingest
business briefs, extract creative requirements, apply brand governance, and output
campaign-ready plans.

## Component Layers

1. **Brief Ingestion (`mark_lang.brief_ingest`)**
   - Converts text files or inline content into `BusinessBrief` objects.
   - Normalizes metadata such as titles, tags, and source provenance.

2. **Creative Brief Extraction (`mark_lang.creative_brief`)**
   - Parses structured sections for goals, audience, messaging, and timeframe.
   - Provides defaults and prompts for missing information to accelerate
     stakeholder reviews.

3. **Brand Centre Connectors (`mark_lang.brand_center`)**
   - `BrandCenterClient` enforces authentication headers and error handling when
     retrieving guidelines from DNB's Brand Centre API.
   - Models returned data as `BrandGuidelines` for downstream consumers.

4. **LangGraph Workflows (`mark_lang.workflows`)**
   - `CreativeCampaignWorkflow` orchestrates ingestion, extraction, guideline
     retrieval, and multi-channel planning.
   - Designed to run in offline (fallback) or LangGraph-enabled environments.

5. **User Interfaces (`mark_lang.ui`)**
   - CLI (`mark_lang.ui.cli`) wraps the workflow, surfacing missing data and
     printing campaign plans for approval or export.

## Data Flow

```text
Business Brief -> Ingestor -> CreativeBriefExtractor -> BrandCenterClient
             -> CreativeCampaignWorkflow -> UI / Export
```

## Security and Privacy

- Brand Centre calls require bearer authentication and enforce strict response
  validation (`BrandCenterClient._validate_response`).
- The workflow keeps campaign data in-memory; callers can persist or sanitize
  according to DNB retention requirements.
