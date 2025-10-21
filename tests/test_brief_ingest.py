from pathlib import Path

from mark_lang.brief_ingest import BriefIngestor


def test_from_text_derives_title():
    ingestor = BriefIngestor()
    brief = ingestor.from_text("Acme Expansion\nGoals: Grow")
    assert brief.title.startswith("Acme Expansion")
    assert brief.source == "inline"


def test_from_path_reads_file(tmp_path: Path):
    file_path = tmp_path / "brief.txt"
    file_path.write_text("Goals: Expand\nAudience: SMEs", encoding="utf-8")
    ingestor = BriefIngestor()
    brief = ingestor.from_path(file_path)
    assert brief.title == "brief"
    assert "Goals" in brief.content
