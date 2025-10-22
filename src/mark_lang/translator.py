"""Translation module for converting Norwegian content to English."""
from __future__ import annotations

import re
from typing import Dict, List

from deep_translator import GoogleTranslator


class TextTranslator:
    """Translate Norwegian text to English with chunking support."""

    def __init__(self, source_lang: str = "no", target_lang: str = "en"):
        """
        Initialize the translator.
        
        Args:
            source_lang: Source language code (default: 'no' for Norwegian)
            target_lang: Target language code (default: 'en' for English)
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source=source_lang, target=target_lang)
        self.max_chunk_size = 4500  # Google Translate API limit
    
    def translate(self, text: str) -> str:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # If text is short enough, translate directly
        if len(text) <= self.max_chunk_size:
            try:
                return self.translator.translate(text)
            except Exception as e:
                print(f"Translation error: {e}")
                return text
        
        # For longer text, split into chunks
        return self._translate_chunks(text)
    
    def _translate_chunks(self, text: str) -> str:
        """
        Split long text into chunks and translate each chunk.
        
        Args:
            text: Long text to translate
            
        Returns:
            Translated text
        """
        # Split by paragraphs first to maintain structure
        paragraphs = text.split("\n\n")
        translated_paragraphs = []
        
        current_chunk = ""
        for para in paragraphs:
            # If adding this paragraph exceeds limit, translate current chunk
            if len(current_chunk) + len(para) + 2 > self.max_chunk_size:
                if current_chunk:
                    try:
                        translated = self.translator.translate(current_chunk)
                        translated_paragraphs.append(translated)
                    except Exception as e:
                        print(f"Translation error: {e}")
                        translated_paragraphs.append(current_chunk)
                    current_chunk = para
                else:
                    # Single paragraph is too long, split by sentences
                    translated_paragraphs.append(self._translate_long_paragraph(para))
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Translate remaining chunk
        if current_chunk:
            try:
                translated = self.translator.translate(current_chunk)
                translated_paragraphs.append(translated)
            except Exception as e:
                print(f"Translation error: {e}")
                translated_paragraphs.append(current_chunk)
        
        return "\n\n".join(translated_paragraphs)
    
    def _translate_long_paragraph(self, paragraph: str) -> str:
        """
        Translate a very long paragraph by splitting into sentences.
        
        Args:
            paragraph: Long paragraph to translate
            
        Returns:
            Translated paragraph
        """
        # Simple sentence splitter
        sentences = re.split(r'([.!?]+\s+)', paragraph)
        translated_sentences = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
            
            if len(current_chunk) + len(sentence) + len(delimiter) > self.max_chunk_size:
                if current_chunk:
                    try:
                        translated = self.translator.translate(current_chunk)
                        translated_sentences.append(translated)
                    except Exception as e:
                        print(f"Translation error: {e}")
                        translated_sentences.append(current_chunk)
                    current_chunk = sentence + delimiter
                else:
                    # Even single sentence is too long, truncate or handle
                    try:
                        translated = self.translator.translate(sentence[:self.max_chunk_size])
                        translated_sentences.append(translated)
                    except Exception as e:
                        print(f"Translation error: {e}")
                        translated_sentences.append(sentence)
            else:
                current_chunk += sentence + delimiter
        
        if current_chunk:
            try:
                translated = self.translator.translate(current_chunk)
                translated_sentences.append(translated)
            except Exception as e:
                print(f"Translation error: {e}")
                translated_sentences.append(current_chunk)
        
        return " ".join(translated_sentences)
    
    def translate_document(self, document: Dict) -> Dict:
        """
        Translate a document dictionary extracted by DocumentProcessor.
        
        Args:
            document: Document dictionary with extracted content
            
        Returns:
            Document dictionary with translated content
        """
        translated_doc = document.copy()
        
        # Translate the full text
        if "full_text" in document:
            translated_doc["full_text"] = self.translate(document["full_text"])
        
        # Translate slides for PPTX
        if "slides" in document and isinstance(document["slides"], list):
            translated_slides = []
            for slide in document["slides"]:
                translated_slide = slide.copy()
                if "content" in slide:
                    translated_slide["content"] = self.translate(slide["content"])
                translated_slides.append(translated_slide)
            translated_doc["slides"] = translated_slides
        
        # Translate pages for PDF
        if "pages" in document and isinstance(document["pages"], list):
            translated_pages = []
            for page in document["pages"]:
                translated_page = page.copy()
                if "content" in page:
                    translated_page["content"] = self.translate(page["content"])
                translated_pages.append(translated_page)
            translated_doc["pages"] = translated_pages
        
        # Translate paragraphs for DOCX
        if "paragraphs" in document and isinstance(document["paragraphs"], list):
            translated_doc["paragraphs"] = [
                self.translate(para) for para in document["paragraphs"]
            ]
        
        # Translate sheets for Excel
        if "sheets" in document and isinstance(document["sheets"], list):
            translated_sheets = []
            for sheet in document["sheets"]:
                translated_sheet = sheet.copy()
                if "content" in sheet:
                    translated_sheet["content"] = self.translate(sheet["content"])
                translated_sheets.append(translated_sheet)
            translated_doc["sheets"] = translated_sheets
        
        return translated_doc
    
    def translate_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Translate multiple documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of translated document dictionaries
        """
        return [self.translate_document(doc) for doc in documents]
