"""LangGraph-based workflow for end-to-end campaign planning."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

try:  # pragma: no cover - handled in tests via fallback
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover - optional dependency path
    END = "__end__"

    class StateGraph:  # type: ignore[override]
        """Minimal stand-in for :class:`langgraph.graph.StateGraph`."""

        def __init__(self, state_schema: type) -> None:
            self.state_schema = state_schema
            self.nodes: Dict[str, Any] = {}
            self.entry: str | None = None

        def add_node(self, name: str, func: Any) -> None:
            self.nodes[name] = {"func": func, "edges": []}

        def add_edge(self, src: str, dest: str) -> None:
            self.nodes[src]["edges"].append(dest)

        def set_entry_point(self, name: str) -> None:
            self.entry = name

        def compile(self):
            graph = self

            def runner(state: Dict[str, Any]) -> Dict[str, Any]:
                node_name = graph.entry
                while node_name and node_name != END:
                    node = graph.nodes[node_name]
                    state = node["func"](state)
                    node_name = node["edges"][0] if node["edges"] else END
                return state

            return runner


from typing import TypedDict

from ..brand_center.api_client import BrandCenterClient, BrandGuidelines
from ..brief_ingest import BriefIngestor, BusinessBrief
from ..creative_brief import CreativeBrief, CreativeBriefExtractor


class WorkflowState(TypedDict, total=False):
    brief: BusinessBrief
    brand_id: str
    creative_brief: CreativeBrief
    guidelines: BrandGuidelines
    campaign_plan: Dict[str, Any]
    gaps: Dict[str, str]


@dataclass
class WorkflowStateData:
    """Data structure for workflow state results."""
    brief: BusinessBrief
    brand_id: str
    creative_brief: CreativeBrief | None = None
    guidelines: BrandGuidelines | None = None
    campaign_plan: Dict[str, Any] | None = None
    gaps: Dict[str, str] = field(default_factory=dict)


@dataclass
class CreativeCampaignWorkflow:
    """Coordinate ingestion, extraction, guideline retrieval, and campaign generation."""

    brand_client: BrandCenterClient
    brief_extractor: CreativeBriefExtractor
    brief_ingestor: BriefIngestor

    def build(self) -> Any:
        graph = StateGraph(WorkflowState)
        graph.add_node("ingest", self._ingest)
        graph.add_node("extract", self._extract)
        graph.add_node("fetch_guidelines", self._guidelines)
        graph.add_node("campaign", self._campaign)
        graph.add_node("final", self._finalize)
        graph.add_edge("ingest", "extract")
        graph.add_edge("extract", "fetch_guidelines")
        graph.add_edge("fetch_guidelines", "campaign")
        graph.add_edge("campaign", "final")
        graph.add_edge("final", END)
        graph.set_entry_point("ingest")
        return graph.compile()

    def run(self, brief_text: str, *, title: str, brand_id: str) -> WorkflowStateData:
        runner = self.build()
        initial_brief = self.brief_ingestor.from_text(brief_text, title=title)
        initial_state: WorkflowState = {
            "brief": initial_brief,
            "brand_id": brand_id,
            "gaps": {}
        }
        result = runner.invoke(initial_state)
        return WorkflowStateData(
            brief=result["brief"],
            brand_id=result["brand_id"],
            creative_brief=result.get("creative_brief"),
            guidelines=result.get("guidelines"),
            campaign_plan=result.get("campaign_plan"),
            gaps=result.get("gaps", {})
        )

    def _ingest(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state

    def _extract(self, state: Dict[str, Any]) -> Dict[str, Any]:
        brief = state["brief"]
        creative_brief = self.brief_extractor.extract(brief)
        gaps = self.brief_extractor.detect_gaps(creative_brief)
        state.update({"creative_brief": creative_brief, "gaps": gaps})
        return state

    def _guidelines(self, state: Dict[str, Any]) -> Dict[str, Any]:
        brief: BusinessBrief = state["brief"]
        brand_id = state.get("brand_id") or (brief.tags[0] if brief.tags else "default")
        guidelines = self.brand_client.fetch_guidelines(brand_id)
        state["guidelines"] = guidelines
        return state

    def _campaign(self, state: Dict[str, Any]) -> Dict[str, Any]:
        creative_brief: CreativeBrief = state["creative_brief"]
        guidelines: BrandGuidelines = state["guidelines"]
        plan = self._build_plan(creative_brief, guidelines)
        state["campaign_plan"] = plan
        return state

    def _finalize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state

    def _build_plan(self, creative_brief: CreativeBrief, guidelines: BrandGuidelines) -> Dict[str, Any]:
        multi_channel: List[Dict[str, Any]] = [
            {
                "channel": "email",
                "message": f"{creative_brief.messaging} | Tone: {guidelines.tone_of_voice}",
                "timeline": creative_brief.timeframe,
            },
            {
                "channel": "social",
                "message": f"Snackable content mirroring '{creative_brief.goals}'",
                "visual_style": guidelines.visual_style,
            },
            {
                "channel": "web",
                "message": "Landing page focused on lead capture",
                "compliance": guidelines.compliance_notes,
            },
        ]
        return {
            "summary": creative_brief.to_dict(),
            "channels": multi_channel,
        }
