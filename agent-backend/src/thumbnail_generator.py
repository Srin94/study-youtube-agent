"""High-CTR 1280x720 thumbnail renderer (Playwright headless Chromium).

The study channel's ThumbnailSpec is a TEXT-vs-TEXT contrast card (no brand icon
slugs): a bold headline + badge on the left, and two labelled tiles joined by a
connector glyph on the right. Theme-matched colors mirror themes.ts.
"""

from __future__ import annotations

from typing import Dict

try:
    from . import config
    from .script_generator import ThumbnailSpec, VideoRenderPayload
except ImportError:  # pragma: no cover
    import config  # type: ignore
    from script_generator import ThumbnailSpec, VideoRenderPayload  # type: ignore


# Theme color maps mirror styles/themes.ts.
_THEMES: Dict[str, Dict[str, str]] = {
    # Warm archival drafting paper (LIGHT).
    "ARCHIVAL_LAB_PAPER": {
        "canvas_bg": "#F4F1EA",
        "canvas_bg2": "#ECE7DB",
        "card_bg": "#FFFFFF",
        "grid": "#E2DDD2",
        "text_primary": "#18181B",
        "text_muted": "#6B6459",
        "accent": "#FF4F00",
        "accent_2": "#0047AB",
        "accent_critical": "#C81E1E",
        "ink": "#18181B",
        "hard_shadow": "6px 6px 0px #18181B",
        "font_heading": "'Space Grotesk', 'Helvetica Neue', Arial, sans-serif",
        "font_mono": "'IBM Plex Mono', 'Consolas', monospace",
    },
    # Deep obsidian oscilloscope console (DARK).
    "QUANTUM_SIM_HUD": {
        "canvas_bg": "#090D16",
        "canvas_bg2": "#0C121F",
        "card_bg": "#0E1626",
        "grid": "#1E293B",
        "text_primary": "#E5EEF7",
        "text_muted": "#64748B",
        "accent": "#38BDF8",
        "accent_2": "#10B981",
        "accent_critical": "#FB7185",
        "ink": "#24324A",
        "hard_shadow": "0 0 40px rgba(56,189,248,0.30)",
        "font_heading": "'Space Grotesk', 'Segoe UI', sans-serif",
        "font_mono": "'JetBrains Mono', 'Consolas', monospace",
    },
}

_CONNECTOR_GLYPH = {
    "vs_bolt": "⚡",       # lightning bolt (VS)
    "broken_arrow": "↯",  # downwards zigzag arrow
    "upgrade_arrow": "→",  # rightwards arrow
}


def _headline_html(text: str) -> str:
    """Render the headline, accenting the final word for contrast."""
    words = text.strip().split()
    if not words:
        return ""
    if len(words) > 1:
        head = " ".join(words[:-1])
        return f'{head} <span class="hl">{words[-1]}</span>'
    return f'<span class="hl">{text}</span>'


def _fill_template(spec: ThumbnailSpec, theme_id: str) -> str:
    theme = _THEMES.get(theme_id, _THEMES["ARCHIVAL_LAB_PAPER"])
    with open(config.THUMBNAIL_TEMPLATE_PATH, encoding="utf-8") as fh:
        html = fh.read()

    connector_glyph = _CONNECTOR_GLYPH.get(spec.connector_style, "→")
    connector_class = "critical" if spec.connector_style == "broken_arrow" else ""

    replacements = {
        "__CANVAS_BG__": theme["canvas_bg"],
        "__CANVAS_BG2__": theme["canvas_bg2"],
        "__CARD_BG__": theme["card_bg"],
        "__GRID__": theme["grid"],
        "__TEXT_PRIMARY__": theme["text_primary"],
        "__TEXT_MUTED__": theme["text_muted"],
        "__ACCENT__": theme["accent"],
        "__ACCENT_2__": theme["accent_2"],
        "__ACCENT_CRITICAL__": theme["accent_critical"],
        "__INK__": theme["ink"],
        "__HARD_SHADOW__": theme["hard_shadow"],
        "__FONT_HEADING__": theme["font_heading"],
        "__FONT_MONO__": theme["font_mono"],
        "__CHANNEL_NAME__": config.CHANNEL_NAME.upper(),
        "__BADGE_TEXT__": spec.badge_text.upper(),
        "__HEADLINE_HTML__": _headline_html(spec.headline_text),
        "__LEFT_LABEL__": spec.left_label,
        "__RIGHT_LABEL__": spec.right_label,
        "__CONNECTOR_GLYPH__": connector_glyph,
        "__CONNECTOR_CLASS__": connector_class,
    }
    for token, value in replacements.items():
        html = html.replace(token, value)
    return html


def render_thumbnail(payload: VideoRenderPayload) -> str:
    """Render the thumbnail PNG; return its path. Requires Playwright chromium."""
    html = _fill_template(payload.thumbnail, payload.theme_id)

    filled_path = config.OUTPUT_DIR / "thumbnail_filled.html"
    filled_path.write_text(html, encoding="utf-8")

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "playwright not installed. `pip install playwright && playwright install chromium`."
        ) from exc

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(
            viewport={"width": config.THUMBNAIL_WIDTH, "height": config.THUMBNAIL_HEIGHT},
            device_scale_factor=1,
        )
        page.goto(filled_path.as_uri())
        page.wait_for_timeout(300)
        page.screenshot(
            path=str(config.THUMBNAIL_PATH),
            clip={"x": 0, "y": 0, "width": config.THUMBNAIL_WIDTH, "height": config.THUMBNAIL_HEIGHT},
        )
        browser.close()

    print(f"[thumbnail] Rendered -> {config.THUMBNAIL_PATH}")
    return str(config.THUMBNAIL_PATH)


if __name__ == "__main__":
    import json

    with open(config.RENDER_PAYLOAD_PATH, encoding="utf-8") as fh:
        p = VideoRenderPayload.model_validate(json.load(fh))
    render_thumbnail(p)
