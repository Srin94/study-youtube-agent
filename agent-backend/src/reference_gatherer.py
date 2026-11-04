"""Factual reference gathering (replaces the article scraper).

Given a chosen Topic, fetch clean factual Markdown so Gemini is grounded in real
equations, units, historical numbers and step-by-step mechanics.

Primary path: Jina Reader over the topic's Wikipedia article
(`https://r.jina.ai/https://en.wikipedia.org/wiki/{slug}`). Secondary: a Google
News RSS search for the reference query (resolved + Jina-read). Fallback: direct
fetch + BeautifulSoup. Output is truncated to the model's token budget.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

try:
    from . import config
    from .curriculum_manager import Topic
except ImportError:  # pragma: no cover
    import config  # type: ignore
    from curriculum_manager import Topic  # type: ignore


@dataclass
class Reference:
    url: str
    markdown: str
    method: str  # "jina-wiki" | "jina-news" | "soup" | "empty"

    @property
    def ok(self) -> bool:
        return len(self.markdown) >= config.MIN_ARTICLE_CHARS


def _truncate(text: str) -> str:
    text = text.strip()
    if len(text) <= config.MAX_ARTICLE_CHARS:
        return text
    cut = text.rfind("\n", 0, config.MAX_ARTICLE_CHARS)
    if cut < config.MAX_ARTICLE_CHARS * 0.6:
        cut = config.MAX_ARTICLE_CHARS
    return text[:cut].strip() + "\n\n...[truncated]"


def _fetch_jina(url: str) -> str:
    jina_url = config.JINA_READER_PREFIX + url
    with httpx.Client(timeout=config.JINA_TIMEOUT_SECONDS, follow_redirects=True) as client:
        resp = client.get(
            jina_url,
            headers={"X-Return-Format": "markdown", "User-Agent": config.USER_AGENT},
        )
        resp.raise_for_status()
        return resp.text or ""


def _fetch_soup(url: str) -> str:
    with httpx.Client(timeout=config.JINA_TIMEOUT_SECONDS, follow_redirects=True) as client:
        resp = client.get(url, headers={"User-Agent": config.USER_AGENT})
        resp.raise_for_status()
        html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    parts: list[str] = []
    title = soup.find("h1") or soup.find("title")
    if title:
        parts.append(f"# {title.get_text(strip=True)}")
    root = soup.find("article") or soup.find("main") or soup.body or soup
    for el in root.find_all(["h2", "h3", "p", "li"]):
        if el.name in ("h2", "h3"):
            parts.append(f"\n## {el.get_text(strip=True)}")
        elif el.name == "li":
            text = el.get_text(" ", strip=True)
            if text:
                parts.append(f"- {text}")
        else:
            text = el.get_text(" ", strip=True)
            if len(text) > 30:
                parts.append(text)
    return "\n\n".join(parts)


def _news_search_markdown(query: str) -> str:
    """Best-effort secondary: Jina-read a Google News RSS search page."""
    from urllib.parse import quote_plus

    rss = config.GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    try:
        return _fetch_jina(rss)
    except Exception as exc:  # noqa: BLE001
        print(f"[reference] news search failed: {exc}")
        return ""


def gather(topic: Topic) -> Reference:
    """Return grounded markdown for a topic (Wikipedia-first)."""
    # 1. Jina Reader over the Wikipedia article.
    if topic.wiki_slug:
        wiki_url = config.WIKIPEDIA_URL.format(slug=topic.wiki_slug)
        try:
            md = _fetch_jina(wiki_url)
            if len(md.strip()) >= config.MIN_ARTICLE_CHARS:
                print(f"[reference] jina-wiki {len(md)} chars <- {wiki_url}")
                return Reference(url=wiki_url, markdown=_truncate(md), method="jina-wiki")
        except Exception as exc:  # noqa: BLE001
            print(f"[reference] Jina Wikipedia failed: {exc}")
        # BeautifulSoup fallback straight off Wikipedia.
        try:
            md = _fetch_soup(wiki_url)
            if len(md.strip()) >= config.MIN_ARTICLE_CHARS:
                print(f"[reference] soup-wiki {len(md)} chars <- {wiki_url}")
                return Reference(url=wiki_url, markdown=_truncate(md), method="soup")
        except Exception as exc:  # noqa: BLE001
            print(f"[reference] soup Wikipedia failed: {exc}")

    # 2. Secondary: news search for the reference query.
    md = _news_search_markdown(topic.reference_query)
    if len(md.strip()) >= config.MIN_ARTICLE_CHARS:
        print(f"[reference] jina-news {len(md)} chars for '{topic.reference_query}'")
        return Reference(url=topic.source_url, markdown=_truncate(md), method="jina-news")

    # 3. Nothing substantial — hand back the title so generation still runs.
    print("[reference] no substantial reference; generating from title only.")
    return Reference(url=topic.source_url, markdown=topic.title, method="empty")


if __name__ == "__main__":
    import sys
    from curriculum_manager import pick_topic  # type: ignore

    t = pick_topic(sys.argv[1] if len(sys.argv) > 1 else None)
    ref = gather(t)
    print(f"method={ref.method} ok={ref.ok} chars={len(ref.markdown)}")
    print(ref.markdown[:600])
