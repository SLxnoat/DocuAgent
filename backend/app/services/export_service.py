"""
Export Service — Phase 7 Media Engine
======================================
Converts Markdown content into:
  • Markdown  (.md)  — pass-through with UTF-8 encoding
  • HTML      (.html) — Pandoc conversion with base64-inlined screenshots
  • PDF       (.pdf)  — WeasyPrint HTML→PDF with custom print stylesheet

All exported files are written to ``exports/{job_id}/manual_{job_id}.{ext}``
and are served by the ``/api/v1/export`` endpoint as binary streams.
"""

from __future__ import annotations

import base64
import logging
import re
from pathlib import Path

import pypandoc
from weasyprint import CSS, HTML

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

SUPPORTED_FORMATS = {"markdown", "html", "pdf"}

CONTENT_TYPES: dict[str, str] = {
    "markdown": "text/markdown; charset=utf-8",
    "html": "text/html; charset=utf-8",
    "pdf": "application/pdf",
}

FILE_EXTENSIONS: dict[str, str] = {
    "markdown": "md",
    "html": "html",
    "pdf": "pdf",
}


def get_export_path(job_id: str, fmt: str) -> Path:
    """Return the canonical export file path for a given job and format."""
    ext = FILE_EXTENSIONS[fmt]
    exports_dir = Path(settings.exports_dir).resolve() / job_id
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir / f"manual_{job_id}.{ext}"


def export_document(
    job_id: str,
    markdown_content: str,
    fmt: str,
    *,
    assets_dir: Path | None = None,
    force: bool = False,
) -> Path:
    """
    Convert ``markdown_content`` into the requested ``fmt`` and persist to disk.

    Args:
        job_id:           Unique job identifier.
        markdown_content: Raw Markdown string (UTF-8).
        fmt:              One of ``"markdown"``, ``"html"``, ``"pdf"``.
        assets_dir:       Override the assets base directory (used in tests).
        force:            Re-generate even if the output file already exists.

    Returns:
        Path to the generated output file.

    Raises:
        ValueError: If ``fmt`` is not supported.
        RuntimeError: If Pandoc or WeasyPrint conversion fails.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported export format '{fmt}'. "
            f"Must be one of: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    out_path = get_export_path(job_id, fmt)

    if out_path.exists() and not force:
        logger.debug("Export cache hit: %s", out_path)
        return out_path

    _assets_dir = assets_dir or (Path(settings.assets_dir).resolve() / job_id)

    if fmt == "markdown":
        _export_markdown(markdown_content, out_path)
    elif fmt == "html":
        _export_html(job_id, markdown_content, out_path, _assets_dir)
    else:  # pdf
        _export_pdf(job_id, markdown_content, out_path, _assets_dir)

    logger.info("Export complete: job=%s format=%s path=%s", job_id, fmt, out_path)
    return out_path


# ---------------------------------------------------------------------------
# Format exporters
# ---------------------------------------------------------------------------


def _export_markdown(markdown_content: str, out_path: Path) -> None:
    """Write the Markdown source as-is (UTF-8)."""
    out_path.write_text(markdown_content, encoding="utf-8")


def _export_html(
    job_id: str,
    markdown_content: str,
    out_path: Path,
    assets_dir: Path,
) -> None:
    """
    Convert Markdown → standalone HTML using Pandoc, then inline all
    referenced screenshot PNGs as base64 data-URIs so the file is
    fully self-contained.
    """
    html_body = _pandoc_md_to_html(markdown_content)
    html_with_images = _inline_images(html_body, assets_dir)
    standalone = _wrap_html(
        title=f"DocuAgent Manual — {job_id}",
        body=html_with_images,
        include_style=True,
    )
    out_path.write_text(standalone, encoding="utf-8")


def _export_pdf(
    job_id: str,
    markdown_content: str,
    out_path: Path,
    assets_dir: Path,
) -> None:
    """
    Convert Markdown → HTML (with inlined images) → PDF via WeasyPrint.
    Uses the custom print stylesheet at ``app/templates/pdf_style.css``.
    """
    html_body = _pandoc_md_to_html(markdown_content)
    html_with_images = _inline_images(html_body, assets_dir)
    standalone = _wrap_html(
        title=f"DocuAgent Manual — {job_id}",
        body=html_with_images,
        include_style=False,  # WeasyPrint loads css file directly
    )

    css_path = Path(__file__).parent.parent / "templates" / "pdf_style.css"
    css = CSS(filename=str(css_path))

    try:
        HTML(string=standalone, base_url=str(assets_dir)).write_pdf(
            str(out_path),
            stylesheets=[css],
            presentational_hints=True,
        )
    except Exception as exc:
        logger.exception("WeasyPrint PDF generation failed for job %s", job_id)
        raise RuntimeError(f"PDF generation failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Pandoc conversion
# ---------------------------------------------------------------------------


def _pandoc_md_to_html(markdown_content: str) -> str:
    """
    Convert Markdown → HTML body fragment.

    Strategy:
    1. Try pypandoc (Pandoc binary) — produces the best GFM rendering.
    2. Fall back to the ``markdown`` Python library with extra extensions
       if the Pandoc binary is not available on this system.

    Raises:
        RuntimeError: If both conversion strategies fail.
    """
    # ── Strategy 1: pypandoc ──────────────────────────────────────────────────
    try:
        html = pypandoc.convert_text(
            markdown_content,
            to="html5",
            format="gfm",  # GitHub-Flavoured Markdown
            extra_args=[
                "--wrap=none",
                "--syntax-highlighting=none",
                "--standalone=false",
            ],
        )
        return html
    except OSError:
        logger.info("Pandoc binary not found — falling back to Python 'markdown' library.")
    except Exception as exc:
        logger.warning("Pandoc conversion failed (%s) — falling back.", exc)

    # ── Strategy 2: Python markdown library ──────────────────────────────────
    try:
        import markdown as md_lib

        extensions = [
            "tables",
            "fenced_code",
            "codehilite",
            "nl2br",
            "toc",
            "attr_list",
            "def_list",
            "footnotes",
        ]
        html = md_lib.markdown(
            markdown_content,
            extensions=extensions,
            extension_configs={
                "codehilite": {"css_class": "highlight", "guess_lang": False},
                "toc": {"permalink": False},
            },
        )
        return html
    except ImportError:
        pass
    except Exception as exc:
        logger.warning("Python markdown library conversion failed: %s", exc)

    raise RuntimeError(
        "Markdown-to-HTML conversion failed: neither Pandoc nor the 'markdown' "
        "Python package is available. Install pandoc or run: pip install markdown"
    )


# ---------------------------------------------------------------------------
# Base64 image inlining
# ---------------------------------------------------------------------------

_IMG_SRC_RE = re.compile(
    r'(<img\b[^>]*?\bsrc=)(["\'])([^"\']+?)(\2)',
    re.IGNORECASE,
)


def _inline_images(html: str, assets_dir: Path) -> str:
    """
    Replace every ``<img src="...">`` whose ``src`` points to a local asset
    with a base64-encoded data-URI so the HTML is fully self-contained.
    """

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        prefix, quote, src, suffix = match.groups()
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)

        img_path = _resolve_asset(src, assets_dir)
        if img_path is None or not img_path.exists():
            logger.warning("Inline image not found — leaving as-is: %s", src)
            return match.group(0)

        try:
            b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
            data_uri = f"data:image/png;base64,{b64}"
            return f"{prefix}{quote}{data_uri}{suffix}"
        except OSError as exc:
            logger.warning("Could not read image %s: %s", img_path, exc)
            return match.group(0)

    return _IMG_SRC_RE.sub(_replace, html)


def _resolve_asset(src: str, assets_dir: Path) -> Path | None:
    """
    Try to resolve an image src string to an absolute Path.

    Handles:
    - ``assets/{job_id}/step_001.png``   (relative from project root)
    - ``step_001.png``                   (filename only → look in assets_dir)
    - ``/assets/{job_id}/step_001.png``  (absolute-style server path)
    """
    src_path = Path(src.lstrip("/"))

    # Case 1: full relative path from project root
    absolute = (Path(settings.assets_dir).resolve().parent / src_path).resolve()
    if absolute.exists():
        return absolute

    # Case 2: just the filename
    candidate = (assets_dir / src_path.name).resolve()
    if candidate.exists():
        return candidate

    # Case 3: relative to assets_dir
    candidate2 = (assets_dir / src_path).resolve()
    if candidate2.exists():
        return candidate2

    return None


# ---------------------------------------------------------------------------
# HTML wrapper
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="generator" content="DocuAgent AI" />
  <title>{title}</title>
  {style_block}
</head>
<body>
{body}
</body>
</html>
"""

_EMBEDDED_CSS = """<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
          font-size: 16px; line-height: 1.6; color: #1f2937; background: #fff; }}
  body {{ max-width: 860px; margin: 0 auto; padding: 2rem 1.5rem; }}
  h1 {{ font-size: 2rem; border-bottom: 3px solid #2563eb; padding-bottom: .4rem; margin-bottom: 1rem; }}
  h2 {{ font-size: 1.4rem; border-bottom: 1px solid #e5e7eb; padding-bottom: .2rem; }}
  h3 {{ font-size: 1.1rem; }}
  code {{ font-family: "SFMono-Regular", Menlo, Consolas, monospace; font-size: .875em;
          background: #f3f4f6; color: #be185d; padding: .1em .3em; border-radius: 3px; }}
  pre {{ background: #f3f4f6; border-left: 4px solid #2563eb; padding: .8rem 1rem;
         overflow-x: auto; border-radius: 4px; }}
  pre code {{ background: none; color: inherit; padding: 0; }}
  blockquote {{ border-left: 4px solid #6366f1; background: #f5f3ff; color: #3730a3;
                margin: 1rem 0; padding: .6rem 1rem; border-radius: 0 4px 4px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  thead {{ background: #1e40af; color: #fff; }}
  th, td {{ padding: .45rem .75rem; border: 1px solid #e5e7eb; text-align: left; }}
  tbody tr:nth-child(even) {{ background: #f9fafb; }}
  img {{ max-width: 100%; height: auto; border: 1px solid #e5e7eb;
         border-radius: 6px; display: block; margin: 1rem auto;
         box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 2rem 0; }}
</style>"""


def _wrap_html(title: str, body: str, *, include_style: bool) -> str:
    """Wrap an HTML body fragment in a full HTML5 document."""
    style_block = _EMBEDDED_CSS if include_style else ""
    return _HTML_TEMPLATE.format(title=title, style_block=style_block, body=body)


# ---------------------------------------------------------------------------
# Thumbnail generator (Phase 7 — 8.2 Media Pipeline P1)
# ---------------------------------------------------------------------------


def generate_thumbnail(
    source_path: Path,
    *,
    width: int = 320,
    height: int = 200,
) -> Path | None:
    """
    Create a ``{stem}_thumb.jpg`` JPEG thumbnail next to the source PNG.

    Args:
        source_path: Absolute path to the source PNG screenshot.
        width:       Maximum thumbnail width in pixels.
        height:      Maximum thumbnail height in pixels.

    Returns:
        Path to the generated thumbnail, or ``None`` if generation failed.
    """
    try:
        from PIL import Image

        thumb_path = source_path.with_name(source_path.stem + "_thumb.jpg")
        if thumb_path.exists():
            return thumb_path

        with Image.open(source_path) as img:
            img_rgb = img.convert("RGB")
            img_rgb.thumbnail((width, height), Image.LANCZOS)
            img_rgb.save(thumb_path, "JPEG", quality=82, optimize=True)

        logger.debug("Thumbnail generated: %s", thumb_path)
        return thumb_path

    except Exception as exc:
        logger.warning("Thumbnail generation failed for %s: %s", source_path, exc)
        return None
