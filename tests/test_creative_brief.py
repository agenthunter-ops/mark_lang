from mark_lang.brief_ingest import BusinessBrief
from mark_lang.creative_brief import CreativeBriefExtractor, DEFAULT_VALUES


def test_extract_creative_elements():
    brief = BusinessBrief(
        title="Launch",
        content=(
            "Goals: Drive trial adoption\nAudience: Mid-market CTOs\n"
            "Messaging: Stress reliability\nTimeframe: 6-week sprint"
        ),
    )
    extractor = CreativeBriefExtractor()
    creative = extractor.extract(brief)
    assert creative.goals == "Drive trial adoption"
    assert creative.audience == "Mid-market CTOs"
    assert creative.source_title == "Launch"


def test_detect_gaps_returns_prompts():
    brief = BusinessBrief(title="Sparse", content="Goals: Drive leads")
    extractor = CreativeBriefExtractor()
    creative = extractor.extract(brief)
    prompts = extractor.detect_gaps(creative)
    expected_fields = {field for field, default in DEFAULT_VALUES.items() if creative.__dict__[field] == default}
    assert set(prompts.keys()) == expected_fields
