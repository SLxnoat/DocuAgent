"""
Integration tests for Export Engine pipeline (Markdown, HTML, PDF).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.services.export_service import (
    export_document,
    generate_thumbnail,
)


@pytest.fixture
def temp_export_dirs(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        assets_dir = Path(tmpdir) / "assets"
        exports_dir = Path(tmpdir) / "exports"
        assets_dir.mkdir()
        exports_dir.mkdir()

        import app.config as cfg

        monkeypatch.setattr(cfg.settings, "assets_dir", str(assets_dir))
        monkeypatch.setattr(cfg.settings, "exports_dir", str(exports_dir))

        yield assets_dir, exports_dir


def test_export_pipeline_all_formats(temp_export_dirs):
    """Verify that export_document generates valid Markdown, HTML, and PDF files."""
    assets_dir, _exports_dir = temp_export_dirs
    job_id = "test-export-job-999"

    # Create a mock screenshot in assets
    job_assets = assets_dir / job_id
    job_assets.mkdir(parents=True, exist_ok=True)
    screenshot_file = job_assets / "step_000.png"

    from PIL import Image

    img = Image.new("RGB", (800, 600), color=(20, 100, 200))
    img.save(screenshot_file, "PNG")

    sample_md = f"""# Integration Test Manual

## Prerequisites
- Test environment setup
- Active user session

## System Overview
Comprehensive integration test for DocuAgent export pipeline.

## Step-by-Step Walkthrough

### Step 1: Verification
Verify that screenshot images are embedded into standalone documents.
![Step 0]({screenshot_file})

> 💡 Tip: Screenshots should be inlined as base64 in standalone HTML distributions.

## Troubleshooting
Check output directory permissions if exports fail.
"""

    # 1. Test Markdown export
    md_path = export_document(job_id, sample_md, "markdown", force=True)
    assert md_path.exists()
    assert md_path.suffix == ".md"
    content = md_path.read_text(encoding="utf-8")
    assert "# Integration Test Manual" in content

    # 2. Test HTML export (with base64 image inlining)
    html_path = export_document(job_id, sample_md, "html", force=True)
    assert html_path.exists()
    assert html_path.suffix == ".html"
    html_content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_content
    assert "data:image/png;base64," in html_content  # Verifies base64 inlining

    # 3. Test PDF export (WeasyPrint)
    pdf_path = export_document(job_id, sample_md, "pdf", force=True)
    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 2000
    with pdf_path.open("rb") as f:
        header = f.read(4)
    assert header == b"%PDF"

    # 4. Test Thumbnail generation
    thumb_path = generate_thumbnail(screenshot_file, width=320, height=200)
    assert thumb_path is not None
    assert thumb_path.exists()
    assert thumb_path.suffix == ".jpg"
