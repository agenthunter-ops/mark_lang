# DNB Brand Document Ingestion System

## Overview

This system processes DNB marketing documents (PowerPoint, Word, PDF, Excel) in Norwegian, translates them to English, and extracts brand guidelines and marketing principles into a structured JSON format.

## Components

### 1. Document Processor (`document_processor.py`)
- Extracts text from multiple file formats:
  - PowerPoint (`.pptx`)
  - Word (`.docx`)
  - PDF (`.pdf`)
  - Excel (`.xlsx`, `.xls`)
- Handles slides, paragraphs, tables, and multi-page content
- Returns structured dictionaries with extracted content

### 2. Text Translator (`translator.py`)
- Translates Norwegian content to English using Google Translate
- Handles long documents by chunking text intelligently
- Preserves document structure during translation
- Supports batch processing of multiple documents

### 3. Brand Guidelines Extractor (`brand_guidelines_extractor.py`)
- Analyzes translated documents to identify brand elements:
  - Tone of voice
  - Visual style
  - Messaging principles
  - Target audiences
  - Brand values
  - Compliance requirements
  - Campaign themes
  - Content guidelines
  - Channel-specific guidelines
- Uses keyword matching and pattern recognition
- Outputs structured `BrandGuidelinesExtracted` model

### 4. Ingestion Workflow (`ingest_brand_documents.py`)
- Orchestrates the complete pipeline:
  1. Document extraction
  2. Translation
  3. Guidelines extraction
  4. JSON output generation
- Command-line interface for easy execution
- Progress tracking and error handling

## Installation

The required dependencies are already installed:
```bash
pip install python-pptx python-docx pdfplumber openpyxl deep-translator
```

## Usage

### Basic Usage - Process a Directory

```bash
python -m mark_lang.ingest_brand_documents "path/to/documents" --output examples/brand_guidelines.json
```

### Process Specific Files

```bash
python -m mark_lang.ingest_brand_documents --files file1.pptx file2.docx file3.pdf --output guidelines.json
```

### Save Translated Documents

```bash
python -m mark_lang.ingest_brand_documents "path/to/documents" --save-translated --translated-dir examples/translated
```

### Real Example (Already Run)

```bash
python -m mark_lang.ingest_brand_documents "C:\Users\AD16521\Downloads\OneDrive_2025-10-03 (1)\Underlag Brief og konsepter" --save-translated
```

This command processed 13 DNB marketing documents and generated:
- `examples/dnb_brand_guidelines.json` - Structured brand guidelines
- `examples/translated/` - Translated versions of all documents

## Output Format

The generated JSON file contains:

```json
{
  "dnb": {
    "tone_of_voice": "Professional and trustworthy communication style...",
    "visual_style": "Corporate, clean, minimal design...",
    "compliance_notes": "Legal and regulatory requirements...",
    "messaging_principles": ["Principle 1", "Principle 2", ...],
    "target_audiences": ["Audience 1", "Audience 2", ...],
    "brand_values": ["Value 1", "Value 2", ...],
    "campaign_themes": ["Theme 1", "Theme 2", ...],
    "content_guidelines": ["Guideline 1", "Guideline 2", ...],
    "channel_specific": {
      "email": "Email-specific guidance...",
      "social": "Social media guidance...",
      ...
    }
  }
}
```

## Integration with Existing System

The extracted guidelines can be used with the existing `mark_lang` CLI:

```bash
python -m mark_lang.ui.cli examples/brief.txt --brand dnb --guidelines examples/dnb_brand_guidelines.json
```

This will:
1. Process the business brief
2. Load DNB brand guidelines from the generated JSON
3. Create a campaign plan aligned with the extracted guidelines

## Processed Documents

The system successfully processed these DNB documents:
1. `2024 TV-aksjonen Materielloversikt.xlsx` - Campaign materials overview
2. `2025 VIPPS DNB Materielloversikt.xlsx` - VIPPS campaign materials
3. `24-01 - Forretningsbrief - huninvesterer - Akademi.docx` - Business brief
4. `24-05 - Forretningsbrief - TV-aksjonen.docx` - TV campaign brief
5. `25 - Vipps Pay - Dreiebok.pdf` - Vipps Pay script
6. `250404 Mal kreativ brief byrå.pdf` - Creative brief template
7. `Debrief DNB Huninvesterer 8. mars_15.02.24.pdf` - Campaign debrief
8. `DNB TV-aksjonen_Hver krone teller_manus 25-09-2024.pdf` - TV campaign script
9. `DNB TV-askjonen_Debrief_29.08.24.pdf` - TV campaign debrief
10. `DNB_Tæpp_Debrief_301024.pdf` - Campaign debrief
11. `DNB_Tæpp_Debrief_301024.pptx` - Campaign debrief presentation
12. `Kreativ Brief Huninvesterer Forbilder wow mars 2024.pptx` - Creative brief
13. `Kreativ Brief TRY - DNB TV-aksjonen 2024.pptx` - TV campaign creative brief

## Improvements for Future

To enhance the guidelines extraction:

1. **Add AI/LLM Integration**: Use OpenAI or similar to better understand context
2. **Manual Refinement**: Review and refine the extracted guidelines
3. **Template System**: Create templates for different campaign types
4. **Version Control**: Track changes in brand guidelines over time
5. **Validation Rules**: Add rules to ensure guidelines are complete and accurate

## API Usage (Programmatic)

```python
from mark_lang.document_processor import DocumentProcessor
from mark_lang.translator import TextTranslator
from mark_lang.brand_guidelines_extractor import BrandGuidelinesExtractor

# Initialize components
doc_processor = DocumentProcessor()
translator = TextTranslator(source_lang="no", target_lang="en")
extractor = BrandGuidelinesExtractor()

# Process documents
doc = doc_processor.process_file("document.pptx")
translated = translator.translate_document(doc)
guidelines = extractor.extract_from_documents([translated])

# Save results
extractor.to_json(guidelines, "output.json")
```

## Notes

- Translation may take time for large documents (uses Google Translate API)
- Some PDF files may have extraction warnings (color space issues) - these are normal
- PowerPoint files with complex table structures may have partial extraction
- The system automatically handles errors and continues processing remaining files
