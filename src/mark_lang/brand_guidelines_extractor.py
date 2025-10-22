"""Brand guidelines extraction module using AI to identify branding elements."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class BrandGuidelinesExtracted(BaseModel):
    """Structured brand guidelines extracted from documents."""
    
    brand_name: str = Field(default="DNB", description="Brand name")
    tone_of_voice: str = Field(default="", description="Brand tone of voice and communication style")
    visual_style: str = Field(default="", description="Visual design style and aesthetics")
    messaging_principles: List[str] = Field(default_factory=list, description="Key messaging principles")
    target_audiences: List[str] = Field(default_factory=list, description="Target audience segments")
    brand_values: List[str] = Field(default_factory=list, description="Core brand values")
    compliance_notes: str = Field(default="", description="Compliance and legal requirements")
    campaign_themes: List[str] = Field(default_factory=list, description="Recurring campaign themes")
    content_guidelines: List[str] = Field(default_factory=list, description="Content creation guidelines")
    channel_specific: Dict[str, str] = Field(default_factory=dict, description="Channel-specific guidelines")


class BrandGuidelinesExtractor:
    """Extract and structure brand guidelines from translated documents."""

    def __init__(self):
        """Initialize the extractor."""
        self.keywords = {
            "tone": ["tone", "voice", "style", "personality", "character", "communication"],
            "visual": ["visual", "design", "color", "font", "typography", "aesthetic", "look", "feel"],
            "audience": ["audience", "target", "segment", "customer", "demographic"],
            "values": ["value", "principle", "belief", "mission", "vision", "purpose"],
            "compliance": ["compliance", "legal", "regulation", "policy", "requirement", "gdpr", "privacy"],
            "messaging": ["message", "messaging", "narrative", "story", "positioning"],
            "campaign": ["campaign", "initiative", "activation", "program"],
            "content": ["content", "creative", "copy", "asset", "material"],
        }
    
    def extract_from_documents(self, documents: List[Dict]) -> BrandGuidelinesExtracted:
        """
        Extract brand guidelines from multiple documents.
        
        Args:
            documents: List of translated document dictionaries
            
        Returns:
            Structured brand guidelines
        """
        guidelines = BrandGuidelinesExtracted()
        
        # Combine all document text
        all_text = "\n\n".join(
            doc.get("full_text", "") for doc in documents if doc.get("full_text")
        )
        
        if not all_text:
            return guidelines
        
        # Extract different guideline components
        guidelines.tone_of_voice = self._extract_tone(all_text)
        guidelines.visual_style = self._extract_visual_style(all_text)
        guidelines.messaging_principles = self._extract_messaging_principles(all_text)
        guidelines.target_audiences = self._extract_audiences(all_text)
        guidelines.brand_values = self._extract_values(all_text)
        guidelines.compliance_notes = self._extract_compliance(all_text)
        guidelines.campaign_themes = self._extract_campaign_themes(all_text)
        guidelines.content_guidelines = self._extract_content_guidelines(all_text)
        guidelines.channel_specific = self._extract_channel_guidelines(all_text)
        
        return guidelines
    
    def _extract_tone(self, text: str) -> str:
        """Extract tone of voice guidelines."""
        tone_indicators = []
        
        # Look for sections mentioning tone or voice
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.keywords["tone"]):
                # Capture the line and next few lines
                context = " ".join(lines[i:min(i+3, len(lines))])
                if len(context) > 20:
                    tone_indicators.append(context)
        
        # Find descriptive adjectives
        descriptors = re.findall(
            r'\b(professional|trustworthy|friendly|warm|innovative|reliable|personal|empowering|'
            r'authentic|transparent|expert|approachable|confident|caring|dynamic|modern)\b',
            text.lower()
        )
        
        if tone_indicators:
            return "; ".join(tone_indicators[:3])
        elif descriptors:
            return f"Professional and {', '.join(set(descriptors[:5]))}"
        else:
            return "Professional and trustworthy"
    
    def _extract_visual_style(self, text: str) -> str:
        """Extract visual style guidelines."""
        visual_indicators = []
        
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.keywords["visual"]):
                context = " ".join(lines[i:min(i+2, len(lines))])
                if len(context) > 20:
                    visual_indicators.append(context)
        
        # Look for color mentions
        colors = re.findall(
            r'\b(blue|green|red|orange|yellow|white|black|gray|grey|purple|modern|clean|minimal|bold|elegant)\b',
            text.lower()
        )
        
        if visual_indicators:
            return "; ".join(visual_indicators[:2])
        elif colors:
            return f"Corporate style featuring {', '.join(set(colors[:3]))}"
        else:
            return "Corporate, clean, minimal"
    
    def _extract_messaging_principles(self, text: str) -> List[str]:
        """Extract key messaging principles."""
        principles = []
        
        # Look for bullet points or numbered lists
        bullet_pattern = r'[•\-\*]\s+([A-Z][^•\-\*\n]{20,150})'
        bullets = re.findall(bullet_pattern, text)
        
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.keywords["messaging"]):
                # Capture next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip() and len(lines[j]) > 20:
                        principles.append(lines[j].strip())
        
        # Add relevant bullets
        for bullet in bullets:
            if any(keyword in bullet.lower() for keyword in self.keywords["messaging"]):
                principles.append(bullet.strip())
        
        return list(set(principles))[:5]
    
    def _extract_audiences(self, text: str) -> List[str]:
        """Extract target audience information."""
        audiences = []
        
        # Look for audience mentions
        audience_pattern = r'(?:target|audience|segment|customer)[:\s]+([A-Za-z\s,\-]+?)(?:\.|;|\n)'
        matches = re.findall(audience_pattern, text, re.IGNORECASE)
        
        for match in matches:
            if len(match.strip()) > 10 and len(match.strip()) < 100:
                audiences.append(match.strip())
        
        # Common audience patterns
        common_audiences = re.findall(
            r'\b(investors|customers|retailers|SMB|small business|finance leaders|'
            r'operations leaders|consumers|households|women|men|youth|seniors)\b',
            text.lower()
        )
        
        audiences.extend([aud.capitalize() for aud in set(common_audiences)])
        
        return list(set(audiences))[:5]
    
    def _extract_values(self, text: str) -> List[str]:
        """Extract brand values."""
        values = []
        
        # Common brand values
        value_keywords = [
            "trust", "innovation", "integrity", "excellence", "sustainability",
            "responsibility", "transparency", "empowerment", "collaboration",
            "customer-centric", "quality", "reliability"
        ]
        
        for keyword in value_keywords:
            if keyword in text.lower():
                values.append(keyword.capitalize())
        
        # Look for explicit value statements
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.keywords["values"]):
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip() and len(lines[j]) > 15 and len(lines[j]) < 80:
                        values.append(lines[j].strip())
        
        return list(set(values))[:6]
    
    def _extract_compliance(self, text: str) -> str:
        """Extract compliance and legal requirements."""
        compliance_notes = []
        
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.keywords["compliance"]):
                context = " ".join(lines[i:min(i+3, len(lines))])
                if len(context) > 20:
                    compliance_notes.append(context)
        
        if compliance_notes:
            return "; ".join(compliance_notes[:2])
        else:
            return "Ensure alignment with DNB data privacy policies and Norwegian financial regulations."
    
    def _extract_campaign_themes(self, text: str) -> List[str]:
        """Extract recurring campaign themes."""
        themes = []
        
        # Look for campaign names and themes
        campaign_pattern = r'(?:campaign|theme|initiative)[:\s]+([A-Z][^\.;\n]{10,80})'
        matches = re.findall(campaign_pattern, text)
        
        themes.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        # Look for thematic keywords
        thematic_keywords = [
            "growth", "investment", "savings", "digital", "sustainability",
            "empowerment", "trust", "partnership", "innovation", "community"
        ]
        
        for keyword in thematic_keywords:
            if keyword in text.lower():
                themes.append(keyword.capitalize())
        
        return list(set(themes))[:8]
    
    def _extract_content_guidelines(self, text: str) -> List[str]:
        """Extract content creation guidelines."""
        guidelines = []
        
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.keywords["content"]):
                # Capture context
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip() and len(lines[j]) > 25:
                        guidelines.append(lines[j].strip())
        
        # Add common content guidelines
        if "clear" in text.lower() and "simple" in text.lower():
            guidelines.append("Use clear and simple language")
        if "authentic" in text.lower():
            guidelines.append("Maintain authentic brand voice")
        if "visual" in text.lower() and "strong" in text.lower():
            guidelines.append("Use strong visual storytelling")
        
        return list(set(guidelines))[:5]
    
    def _extract_channel_guidelines(self, text: str) -> Dict[str, str]:
        """Extract channel-specific guidelines."""
        channels = {}
        
        channel_names = ["email", "social", "web", "digital", "print", "video", "tv", "radio"]
        
        for channel in channel_names:
            channel_pattern = rf'{channel}[:\s]+([^\.;\n]{{20,150}})'
            matches = re.findall(channel_pattern, text.lower())
            if matches:
                channels[channel] = matches[0].strip().capitalize()
        
        return channels
    
    def to_json(self, guidelines: BrandGuidelinesExtracted, output_path: str) -> None:
        """
        Save guidelines to JSON file.
        
        Args:
            guidelines: Extracted guidelines
            output_path: Path to output JSON file
        """
        data = {
            "dnb": {
                "tone_of_voice": guidelines.tone_of_voice,
                "visual_style": guidelines.visual_style,
                "compliance_notes": guidelines.compliance_notes,
                "messaging_principles": guidelines.messaging_principles,
                "target_audiences": guidelines.target_audiences,
                "brand_values": guidelines.brand_values,
                "campaign_themes": guidelines.campaign_themes,
                "content_guidelines": guidelines.content_guidelines,
                "channel_specific": guidelines.channel_specific,
            }
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
