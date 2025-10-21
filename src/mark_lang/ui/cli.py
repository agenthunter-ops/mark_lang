"""Command line interface for generating creative briefs and campaign plans."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from ..brand_center.api_client import BrandGuidelines
from ..brief_ingest import BriefIngestor
from ..creative_brief import CreativeBriefExtractor
from ..workflows.creative_campaign import CreativeCampaignWorkflow, WorkflowState


class LocalBrandCenterClient:
    """Offline-friendly connector backed by JSON configuration files."""

    def __init__(self, guidelines: Dict[str, Dict[str, str]]) -> None:
        self.guidelines = guidelines

    def fetch_guidelines(self, brand_id: str) -> BrandGuidelines:  # pragma: no cover - simple passthrough
        payload = self.guidelines.get(
            brand_id,
            {
                "tone_of_voice": "Professional and trustworthy",
                "visual_style": "Corporate, clean, minimal",
                "compliance_notes": "Ensure alignment with DNB data privacy policies.",
            },
        )
        return BrandGuidelines(**payload)


class CLI:
    """Minimal CLI that ties the workflow together."""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description="Generate creative campaign plans")
        self.parser.add_argument("brief", help="Path to the business brief text file")
        self.parser.add_argument("--title", help="Override title for the brief")
        self.parser.add_argument("--brand", default="default", help="Brand identifier")
        self.parser.add_argument(
            "--guidelines",
            help="Path to JSON file containing brand guidelines map",
        )

    def run(self, argv: list[str] | None = None) -> WorkflowState:
        args = self.parser.parse_args(argv)
        brief_text = Path(args.brief).read_text(encoding="utf-8")
        brand_guidelines = self._load_guidelines(args.guidelines)
        workflow = CreativeCampaignWorkflow(
            brand_client=LocalBrandCenterClient(brand_guidelines),
            brief_extractor=CreativeBriefExtractor(),
            brief_ingestor=BriefIngestor(),
        )
        state = workflow.run(brief_text, title=args.title or Path(args.brief).stem, brand_id=args.brand)
        self._display(state)
        return state

    def _load_guidelines(self, path: str | None) -> Dict[str, Dict[str, str]]:
        if not path:
            return {}
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def _display(self, state: WorkflowState) -> None:  # pragma: no cover - CLI output
        print("Creative Brief Summary")
        print(json.dumps(state.creative_brief.to_dict(), indent=2))
        if state.gaps:
            print("\nMissing Information Prompts:")
            for field, prompt in state.gaps.items():
                print(f"- {field}: {prompt}")
        print("\nCampaign Plan:")
        print(json.dumps(state.campaign_plan, indent=2))


def main() -> None:  # pragma: no cover - CLI entrypoint
    CLI().run()


if __name__ == "__main__":  # pragma: no cover
    main()
