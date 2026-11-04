"""Evergreen curriculum selection (replaces the news scraper).

Picks the next topic to produce from `data/curriculum_syllabus.json`:

* `--topic "..."`  -> use that custom prompt directly, classify it into the
  closest track via Gemini.
* otherwise         -> STRICT round-robin track rotation (Track 1 -> ... ->
  Track 6 -> Track 1), choosing the first not-yet-published topic in the active
  track, skipping anything recorded in `seen_topics.db`.

Dedup reuses the existing `db.py` (SHA-256 of a stable `study://track/slug`
URL + fuzzy title match).
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

try:
    from . import config, db, script_generator
except ImportError:  # pragma: no cover - script execution
    import config  # type: ignore
    import db  # type: ignore
    import script_generator  # type: ignore


@dataclass
class Topic:
    title: str
    track: str
    reference_query: str
    wiki_slug: str

    @property
    def source_url(self) -> str:
        """Stable URL used for dedup AND as the payload's source_url.

        Prefers the real Wikipedia article so the published video links to a
        genuine reference; falls back to a synthetic study:// URL otherwise.
        """
        if self.wiki_slug:
            return config.WIKIPEDIA_URL.format(slug=self.wiki_slug)
        return f"study://{self.track.lower()}/{_slugify(self.title)}"


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "topic"


def _load_syllabus() -> List[dict]:
    with open(config.CURRICULUM_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    topics = data.get("topics", [])
    if not topics:
        raise SystemExit("curriculum_syllabus.json has no topics.")
    return topics


def _published_count() -> int:
    """How many topics have been published so far (drives the rotation cursor)."""
    try:
        db.init_db()
        with sqlite3.connect(config.DB_PATH) as conn:
            return int(conn.execute("SELECT COUNT(*) FROM seen_topics").fetchone()[0])
    except Exception:  # noqa: BLE001
        return 0


def _topic_from_row(row: dict) -> Topic:
    return Topic(
        title=row["title"],
        track=row["track"],
        reference_query=row.get("reference_query", row["title"]),
        wiki_slug=row.get("wiki_slug", ""),
    )


def pick_topic(custom_topic: Optional[str] = None) -> Topic:
    """Return the next Topic to produce."""
    db.init_db()

    if custom_topic:
        track = script_generator.classify_topic(custom_topic)
        print(f"[curriculum] Custom topic classified into track: {track}")
        return Topic(
            title=custom_topic.strip(),
            track=track,
            reference_query=custom_topic.strip(),
            wiki_slug="",
        )

    syllabus = _load_syllabus()
    by_track = {t: [] for t in config.TRACKS}
    for row in syllabus:
        by_track.setdefault(row["track"], []).append(row)

    # Strict rotation: the active track advances by one every published video.
    start = _published_count() % len(config.TRACKS)
    for offset in range(len(config.TRACKS)):
        track = config.TRACKS[(start + offset) % len(config.TRACKS)]
        for row in by_track.get(track, []):
            topic = _topic_from_row(row)
            if not db.is_topic_seen(topic.source_url, topic.title):
                if offset:
                    print(
                        f"[curriculum] Track {config.TRACKS[start]} exhausted; "
                        f"rotating to {track}."
                    )
                print(f"[curriculum] Next up [{track}]: {topic.title}")
                return topic

    raise SystemExit(
        "All curriculum topics have been published. Add more to "
        "curriculum_syllabus.json or clear seen_topics.db."
    )


if __name__ == "__main__":
    import sys

    picked = pick_topic(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"{picked.track} :: {picked.title} :: {picked.source_url}")
