"""
Workflow script to process DNB marketing documents and extract brand guidelines.

This script:
1. Reads marketing documents (PowerPoint, Word, PDF, Excel)
2. Translates Norwegian content to English
3. Extracts brand guidelines and marketing principles
4. Saves structured guidelines to JSON

Usage:
    python -m mark_lang.ingest_brand_documents <path_to_documents_directory>
    
Or with specific files:
    python -m mark_lang.ingest_brand_documents --files file1.pptx file2.docx ...
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .brand_guidelines_extractor import BrandGuidelinesExtractor
from .document_processor import DocumentProcessor
from .translator import TextTranslator


class BrandDocumentIngestionWorkflow:
    """Orchestrate the document ingestion and guidelines extraction process."""

    def __init__(self):
        """Initialize the workflow with necessary components."""
        self.doc_processor = DocumentProcessor()
        self.translator = TextTranslator(source_lang="no", target_lang="en")
        self.guidelines_extractor = BrandGuidelinesExtractor()
    
    def process_files(self, file_paths: List[str | Path]) -> dict:
        """
        Process specific files.
        
        Args:
            file_paths: List of paths to document files
            
        Returns:
            Dictionary with processing results
        """
        print(f"Processing {len(file_paths)} files...")
        
        # Step 1: Extract text from documents
        print("\n[1/4] Extracting text from documents...")
        documents = []
        for file_path in file_paths:
            try:
                print(f"  - Processing: {Path(file_path).name}")
                doc = self.doc_processor.process_file(file_path)
                documents.append(doc)
            except Exception as e:
                print(f"  ! Error processing {Path(file_path).name}: {e}")
        
        if not documents:
            print("No documents were successfully processed.")
            return {"error": "No documents processed"}
        
        print(f"  ✓ Successfully processed {len(documents)} documents")
        
        # Step 2: Translate documents
        print("\n[2/4] Translating Norwegian content to English...")
        translated_docs = []
        for i, doc in enumerate(documents, 1):
            print(f"  - Translating document {i}/{len(documents)}: {doc['file_name']}")
            try:
                translated = self.translator.translate_document(doc)
                translated_docs.append(translated)
            except Exception as e:
                print(f"  ! Translation error for {doc['file_name']}: {e}")
                # Include untranslated document as fallback
                translated_docs.append(doc)
        
        print(f"  ✓ Translation completed")
        
        # Step 3: Extract brand guidelines
        print("\n[3/4] Extracting brand guidelines...")
        guidelines = self.guidelines_extractor.extract_from_documents(translated_docs)
        print(f"  ✓ Guidelines extracted")
        
        # Step 4: Display results
        print("\n[4/4] Results:")
        print(f"  - Tone of Voice: {guidelines.tone_of_voice[:100]}...")
        print(f"  - Visual Style: {guidelines.visual_style[:100]}...")
        print(f"  - Target Audiences: {len(guidelines.target_audiences)} identified")
        print(f"  - Brand Values: {len(guidelines.brand_values)} identified")
        print(f"  - Campaign Themes: {len(guidelines.campaign_themes)} identified")
        
        return {
            "documents_processed": len(documents),
            "guidelines": guidelines,
            "translated_documents": translated_docs
        }
    
    def process_directory(self, directory_path: str | Path) -> dict:
        """
        Process all supported documents in a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            Dictionary with processing results
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all supported files
        supported_extensions = [".pptx", ".docx", ".pdf", ".xlsx", ".xls"]
        file_paths = [
            f for f in directory_path.iterdir()
            if f.is_file() and f.suffix.lower() in supported_extensions
        ]
        
        if not file_paths:
            print(f"No supported documents found in {directory_path}")
            return {"error": "No files found"}
        
        return self.process_files(file_paths)
    
    def save_guidelines(self, guidelines, output_path: str | Path) -> None:
        """
        Save extracted guidelines to JSON file.
        
        Args:
            guidelines: BrandGuidelinesExtracted object
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.guidelines_extractor.to_json(guidelines, str(output_path))
        print(f"\n✓ Guidelines saved to: {output_path}")
    
    def save_translated_documents(self, documents: List[dict], output_dir: str | Path) -> None:
        """
        Save translated documents for reference.
        
        Args:
            documents: List of translated document dictionaries
            output_dir: Directory to save translated documents
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for doc in documents:
            file_name = Path(doc["file_name"]).stem + "_translated.json"
            output_path = output_dir / file_name
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Translated documents saved to: {output_dir}")


def main():
    """Main entry point for the brand document ingestion workflow."""
    parser = argparse.ArgumentParser(
        description="Process DNB marketing documents and extract brand guidelines"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to directory containing documents or single document file"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific files to process"
    )
    parser.add_argument(
        "--output",
        default="examples/dnb_brand_guidelines.json",
        help="Output path for guidelines JSON (default: examples/dnb_brand_guidelines.json)"
    )
    parser.add_argument(
        "--save-translated",
        action="store_true",
        help="Save translated documents to JSON files"
    )
    parser.add_argument(
        "--translated-dir",
        default="examples/translated",
        help="Directory to save translated documents (default: examples/translated)"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.path and not args.files:
        parser.error("Either provide a path or use --files to specify documents")
    
    # Initialize workflow
    workflow = BrandDocumentIngestionWorkflow()
    
    # Process documents
    if args.files:
        results = workflow.process_files(args.files)
    else:
        path = Path(args.path)
        if path.is_file():
            results = workflow.process_files([path])
        else:
            results = workflow.process_directory(path)
    
    # Check for errors
    if "error" in results:
        print(f"\n✗ Error: {results['error']}")
        return 1
    
    # Save guidelines
    workflow.save_guidelines(results["guidelines"], args.output)
    
    # Optionally save translated documents
    if args.save_translated:
        workflow.save_translated_documents(
            results["translated_documents"],
            args.translated_dir
        )
    
    print("\n✓ Brand document ingestion completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
