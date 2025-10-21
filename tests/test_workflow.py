from mark_lang.brief_ingest import BriefIngestor
from mark_lang.brand_center.api_client import BrandCenterClient, BrandGuidelines
from mark_lang.creative_brief import CreativeBriefExtractor
from mark_lang.workflows.creative_campaign import CreativeCampaignWorkflow


class StubBrandClient(BrandCenterClient):
    def __init__(self):
        pass

    def fetch_guidelines(self, brand_id: str) -> BrandGuidelines:  # type: ignore[override]
        return BrandGuidelines(
            tone_of_voice="Insightful",
            visual_style="Minimalist",
            compliance_notes="Archive all campaign assets for 7 years",
        )


def test_workflow_generates_campaign_plan():
    workflow = CreativeCampaignWorkflow(
        brand_client=StubBrandClient(),
        brief_extractor=CreativeBriefExtractor(),
        brief_ingestor=BriefIngestor(),
    )
    brief_text = (
        "Goals: Capture market share\nAudience: Finance leaders\n"
        "Messaging: Focus on resilience\nTimeframe: Q3 rollout"
    )
    state = workflow.run(brief_text, title="Strategic push", brand_id="dnb")
    assert state.creative_brief is not None
    assert state.campaign_plan is not None
    assert any(channel["channel"] == "email" for channel in state.campaign_plan["channels"])
