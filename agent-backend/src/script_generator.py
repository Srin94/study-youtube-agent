"""Structured concept-video script generation via Gemini (structured output).

`generate_script(topic_title, source_url, reference_markdown, track_category)`
produces a fully-typed `VideoRenderPayload` — the strict JSON contract shared
with Remotion (`video-engine/src/types/schema.ts`) — using
`response_schema=VideoRenderPayload` for native structured output.

The Pydantic models below ARE the canonical data contract. The TypeScript
interfaces in `video-engine/src/types/schema.ts` mirror them one-to-one.
"""

from __future__ import annotations

import json
import re
import time
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

try:
    from . import config
except ImportError:  # pragma: no cover
    import config  # type: ignore


# ===========================================================================
# Strict data contract (mirrors video-engine/src/types/schema.ts)
# ===========================================================================
class WordTimestamp(BaseModel):
    word: str
    start_sec: float
    end_sec: float


class StateWatch(BaseModel):
    label: str = Field(
        description="Variable/metric/parameter name, e.g. 'Switching Win %', "
        "'Wave Phase', 'Disk Seeks', 'Expected Value'"
    )
    value: str = Field(
        description="Current value at this step, e.g. '66.7% (2/3)', "
        "'180 deg Inverted', '3 Hops', '+$14.20'"
    )
    changed: bool = Field(
        default=False,
        description="True if this value UPDATED in this scene so the HUD row "
        "flashes a highlight pulse.",
    )


class ConceptHUD(BaseModel):
    track_badge: str = Field(
        description="e.g. 'GAME THEORY // PARADOX' or 'EVERYDAY TECH // AUDIO'"
    )
    core_formula_or_law: str = Field(
        description="Key equation, complexity, or principle, e.g. "
        "'P(Win|Switch) = 2/3', 'O(log_b N)', 'E = hf'"
    )
    real_world_scale: str = Field(
        description="Concrete scale metric, e.g. '40ms across 1B roads' or "
        "'99.98% Noise Reduction'"
    )
    governing_rule: str = Field(
        description="1-sentence invariant explaining why this step works"
    )
    state_watches: List[StateWatch] = Field(
        default_factory=list,
        description="3 to 5 live simulation parameters updating each scene",
    )


class GridCellItem(BaseModel):
    index_label: str = Field(
        description="e.g. 'Door #1', 'Bit 04', 'Seat 180', 'Freq 820Hz'"
    )
    value: str = Field(description="e.g. 'Goat', 'Car', '0x4F', '+1.0 dB'")
    state: Literal[
        "default", "active_focus", "comparing", "optimal_hit", "eliminated"
    ] = "default"
    pointer_tags: List[str] = Field(
        default_factory=list,
        description="e.g. ['Your Pick', 'Host Opens', 'Pointer L']",
    )


class SequenceGridPayload(BaseModel):
    title: str
    cells: List[GridCellItem]
    highlight_range_start: Optional[int] = None
    highlight_range_end: Optional[int] = None
    step_caption: str = Field(
        description="Action summary, e.g. 'Host eliminates Door #3 -> 2/3 "
        "probability concentrates on Door #2'"
    )


class GraphNode(BaseModel):
    id: str
    label: str
    sublabel: str = Field(
        description="e.g. 'Delay: 12ms', 'Fee: 0.3%', 'Payoff: (-5, -5)'"
    )
    icon_slug: Optional[str] = None
    tier: int = Field(
        default=1, description="1 to 5 for left-to-right / top-to-bottom layout"
    )
    status: Literal[
        "neutral", "active", "optimal_path", "bottleneck", "eliminated"
    ] = "neutral"


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = Field(
        default=None,
        description="Flow label, probability, or cost, e.g. 'p = 0.67' or '+45 mins'",
    )
    packet_color: Literal["cyan", "orange", "crimson", "emerald"] = "cyan"
    animate_packets: bool = True


class StackLayerBlock(BaseModel):
    layer_label: str = Field(
        description="e.g. 'L1: Acoustic Mic', 'L2: ADC Chip', "
        "'L3: Inverted Speaker Wave'"
    )
    detail_text: str = Field(
        description="e.g. 'Samples ambient 200Hz engine drone every 20 microseconds'"
    )
    metric_badge: str = Field(description="e.g. '-32 dB' or '0.02ms'")
    status: Literal["idle", "processing", "success", "critical_fault"] = "processing"


class FormulaOrCodePayload(BaseModel):
    language: str = Field(description="'python', 'sql', 'math', or 'text'")
    title: str
    naive_or_before: str = Field(
        description="Intuitive/wrong assumption or brute-force formula/code"
    )
    optimal_or_after: str = Field(
        description="Actual mathematical proof, optimal algorithm, or physical equation"
    )
    takeaway_caption: str


class TradeoffRow(BaseModel):
    dimension: str = Field(
        description="e.g. 'Lookup Speed', 'Expected Payout', 'Power Draw'"
    )
    baseline_option: str = Field(
        description="e.g. 'Stick with Door #1 (33.3%)' or 'LCD Backlight'"
    )
    clever_option: str = Field(
        description="e.g. 'Switch to Door #2 (66.7%)' or 'E-Ink Microcapsules'"
    )
    winner: Literal["baseline", "clever"] = "clever"


class SceneSpec(BaseModel):
    scene_id: int
    chapter_title: str = Field(
        description="Short 2-4 word progress label, e.g. '01 THE PARADOX', "
        "'02 TOY SIMULATION'"
    )
    narration_text: str = Field(
        description="Engaging, crystal-clear spoken narration (18 to 32 words)"
    )
    start_sec: float = 0.0
    duration_sec: float = 8.0
    visual_type: Literal[
        "SequenceGridDryRun",
        "SystemAndFlowGraph",
        "LayeredHardwareStack",
        "FormulaAndCodeProof",
        "ComparisonMatrix",
    ]
    camera_focus_node_id: Optional[str] = None
    hud: ConceptHUD
    sequence_grid: Optional[SequenceGridPayload] = None
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    stack_layers: List[StackLayerBlock] = Field(default_factory=list)
    formula_proof: Optional[FormulaOrCodePayload] = None
    comparison_rows: List[TradeoffRow] = Field(default_factory=list)
    callout_keywords: List[str] = Field(
        default_factory=list,
        description="2-3 exact words in narration_text to highlight on screen",
    )


class ThumbnailSpec(BaseModel):
    headline_text: str = Field(
        description="Strictly 3 to 4 bold high-curiosity words, e.g. "
        "'ADD ROAD = MORE TRAFFIC?' or '3 SECONDS TO MATCH'"
    )
    badge_text: str = Field(description="e.g. 'GAME THEORY' or 'HOW IT WORKS'")
    left_label: str = Field(description="e.g. '4 Lanes: 45 Min' or 'Raw Audio Wave'")
    right_label: str = Field(
        description="e.g. '5 Lanes: 62 Min!' or 'Hash Spectrogram'"
    )
    connector_style: Literal["vs_bolt", "upgrade_arrow", "broken_arrow"] = "vs_bolt"


TrackCategory = Literal[
    "EVERYDAY_ALGORITHMS",
    "GAME_THEORY_PARADOXES",
    "MONEY_AND_MARKETS",
    "HARDWARE_AND_PHYSICS",
    "CRYPTO_AND_SECURITY",
    "CS_AND_AI_INTERNALS",
]

# Track -> default theme (spec 5.3).
_ARCHIVAL_TRACKS = {
    "GAME_THEORY_PARADOXES",
    "EVERYDAY_ALGORITHMS",
    "MONEY_AND_MARKETS",
}


def theme_for_track(track: str) -> str:
    return "ARCHIVAL_LAB_PAPER" if track in _ARCHIVAL_TRACKS else "QUANTUM_SIM_HUD"


class VideoRenderPayload(BaseModel):
    track_category: TrackCategory
    theme_id: Literal["ARCHIVAL_LAB_PAPER", "QUANTUM_SIM_HUD"]
    youtube_title: str = Field(
        description="High-CTR curiosity-gap title under 70 characters"
    )
    youtube_description: str
    youtube_tags: List[str]
    pinned_comment: str = Field(
        description="Interactive brain-teaser or counter-intuitive question that "
        "drives debate in comments"
    )
    source_url: str
    thumbnail: ThumbnailSpec
    scenes: List[SceneSpec]
    words: List[WordTimestamp] = Field(default_factory=list)
    total_duration_sec: float = 0.0


# ===========================================================================
# Gemini client helpers
# ===========================================================================
def _get_client():
    """Lazily construct a google-genai client (import + key validation)."""
    try:
        from google import genai  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "google-genai is not installed. `pip install google-genai`."
        ) from exc
    return genai.Client(api_key=config.require_gemini())


_RETRYABLE_MARKERS = (
    "503", "UNAVAILABLE", "500", "502", "504",
    "OVERLOAD", "HIGH DEMAND", "429", "RESOURCE_EXHAUSTED",
)
_RETRY_DELAYS = (4, 10, 25, 60)  # seconds between attempts


def _is_retryable(exc: Exception) -> bool:
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    if code in (500, 502, 503, 504, 429):
        return True
    msg = str(exc).upper()
    return any(marker in msg for marker in _RETRYABLE_MARKERS)


def _generate_resilient(client, **kwargs):
    """Call Gemini generate_content with backoff on transient overload."""
    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            return client.models.generate_content(**kwargs)
        except Exception as exc:  # noqa: BLE001
            if attempt == len(_RETRY_DELAYS) or not _is_retryable(exc):
                raise
            wait = _RETRY_DELAYS[attempt]
            print(
                f"[script] Gemini transient error ({exc}); "
                f"retry {attempt + 1}/{len(_RETRY_DELAYS)} in {wait}s..."
            )
            time.sleep(wait)


# ---------------------------------------------------------------------------
# Topic -> track classification (for --topic custom prompts)
# ---------------------------------------------------------------------------
class _TrackChoice(BaseModel):
    track: TrackCategory = Field(description="The single closest track for this topic")


_CLASSIFY_PROMPT = """Classify this study-video topic into the single closest \
track. Tracks:
- EVERYDAY_ALGORITHMS: how daily tech works under the hood (Shazam, QR codes, GPS, streaming).
- GAME_THEORY_PARADOXES: math, logic, counter-intuitive traps (Monty Hall, Braess, Simpson's).
- MONEY_AND_MARKETS: financial engineering, probability, economic plumbing (overbooking, UPI, HFT).
- HARDWARE_AND_PHYSICS: physical engineering & silicon (EUV, fiber optics, batteries, SSD, E-Ink).
- CRYPTO_AND_SECURITY: information theory, ciphers, trust (ZK proofs, SHA-256, Diffie-Hellman, Enigma).
- CS_AND_AI_INTERNALS: core computing & AI (LLM attention, B+ trees, Bloom filters, TCP, diffusion).
Return only the track id."""


def classify_topic(title: str) -> str:
    """Best-effort Gemini classification of a custom topic into a track."""
    try:
        client = _get_client()
        resp = _generate_resilient(
            client,
            model=config.GEMINI_MODEL,
            contents=f"{_CLASSIFY_PROMPT}\n\nTOPIC: {title}",
            config={
                "response_mime_type": "application/json",
                "response_schema": _TrackChoice,
                "temperature": 0.1,
            },
        )
        return _TrackChoice.model_validate_json(resp.text).track
    except Exception as exc:  # noqa: BLE001
        print(f"[script] Track classification failed ({exc}); defaulting.")
        return "CS_AND_AI_INTERNALS"


# ---------------------------------------------------------------------------
# The 4-Act Visual Curiosity Arc prompt
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """You are the showrunner AND principal educator for a premium, \
high-retention visual explainer YouTube channel in the lineage of 3Blue1Brown, \
Primer, Branch Education and PolyMatter. You convert a factual reference into a \
tightly-paced, intensely visual 75-115 second video as a strict JSON \
VideoRenderPayload. Every claim must be grounded in the supplied reference \
(real equations, physical units, historical numbers, step-by-step mechanics).

THE 4-ACT VISUAL CURIOSITY ARC (structure every video this way; 8 to 10 scenes):
- ACT 1 - THE COUNTER-INTUITIVE HOOK (scenes 1-2): open on a concrete paradox or \
everyday miracle backed by HARD NUMBERS (e.g. 'In 1990 Stuttgart closed a major \
downtown road and traffic got FASTER'). State the provocative promise immediately. \
Never 'Welcome back' / 'Hey everyone' / 'In today's video'.
- ACT 2 - THE TOY MODEL SIMULATION (scenes 3-6): NEVER stay abstract. Build a \
concrete small-scale simulation with numbers the viewer can follow on screen \
(e.g. 4,000 drivers choosing 2 bridges, 3 Monty Hall doors, 200 airline seats at \
5% no-show, 4 Shazam frequency peaks). MUTATE sequence_grid.cells, nodes, and \
hud.state_watches across CONSECUTIVE scenes so the viewer literally watches the \
math play out step by step. Re-use the same cell/node ids across scenes and flip \
their `state`/`status` as the simulation advances.
- ACT 3 - THE FORMULA & REAL-WORLD SCALE (scenes 7-8): show the underlying \
equation or code with FormulaAndCodeProof (naive intuition vs real proof) and the \
head-to-head trade-off with ComparisonMatrix.
- ACT 4 - THE COMMENT BRAIN-TEASER (final scene + pinned_comment): pose a twist \
on the scenario that invites a prediction ('What happens to this equilibrium if \
tolls are dynamic instead of fixed? Drop your prediction below!').

ZONE B - CONCEPT HUD (every scene, mandatory): fill `hud` with:
- track_badge like 'GAME THEORY // PARADOX' or 'EVERYDAY TECH // AUDIO'.
- core_formula_or_law: the key equation / complexity / principle for this beat.
- real_world_scale: one concrete scale metric.
- governing_rule: one sentence on why this step works.
- state_watches: 3 to 5 live parameters. Set changed=true on EXACTLY the watches \
whose value updated THIS scene, so their row pulses. Keep the same labels across \
scenes and evolve their values — this is the running simulation readout.

ZONE A - pick ONE visual_type per scene and FULLY populate its payload (an empty \
payload renders blank and is unacceptable):
- SequenceGridDryRun -> sequence_grid: crisp cells (array indices, Monty doors, \
airline seats, frequency bins, SHA bit blocks). Use pointer_tags for moving \
labels and highlight_range_start/end for the active window. Mutate across scenes.
- SystemAndFlowGraph -> nodes (tier 1..5) + edges (packet_color, animate_packets). \
For payoff trees, road networks, clearing hops, B+ trees. Set camera_focus_node_id \
to the node under discussion. Keep node label <= 16 chars, sublabel <= 22 chars.
- LayeredHardwareStack -> stack_layers (L1..Ln) with metric_badge + status, for \
signal/physical stacks (noise-canceling, EUV, OSI/TCP, OLED/E-Ink cross-sections).
- FormulaAndCodeProof -> formula_proof: naive_or_before vs optimal_or_after. Keep \
each line <= 46 chars and <= 6 lines per side so nothing overflows.
- ComparisonMatrix -> comparison_rows: dimension, baseline_option, clever_option, \
winner. 3 to 5 rows.
VARY the visual_type beat to beat. Prefer SequenceGridDryRun / SystemAndFlowGraph \
for Act 2 (the simulation), FormulaAndCodeProof + ComparisonMatrix for Act 3. \
Use LayeredHardwareStack for physical/hardware topics.

OUTPUT META:
- track_category: use the TRACK given in the user content EXACTLY.
- theme_id: ARCHIVAL_LAB_PAPER for GAME_THEORY_PARADOXES / EVERYDAY_ALGORITHMS / \
MONEY_AND_MARKETS; QUANTUM_SIM_HUD for HARDWARE_AND_PHYSICS / CRYPTO_AND_SECURITY \
/ CS_AND_AI_INTERNALS.
- youtube_title: curiosity-gap, under 70 chars. youtube_description: 2-3 sentences \
+ chapter timestamps. youtube_tags: 8-12. pinned_comment: the Act-4 brain-teaser.
- thumbnail: headline_text = 3-4 BOLD words; badge_text; left_label vs right_label \
(the two sides of the contrast); connector_style vs_bolt | upgrade_arrow | broken_arrow.
- callout_keywords: 2-3 words that appear VERBATIM in that scene's narration_text.
- narration_text: 18-32 spoken words per scene, crystal-clear, no fluff.

Leave start_sec/duration_sec/words at defaults — the audio engine fills exact \
timestamps later. Return ONLY the JSON payload."""


def generate_script(
    topic_title: str,
    source_url: str,
    reference_markdown: str,
    track_category: str,
) -> VideoRenderPayload:
    """Generate a fully-typed VideoRenderPayload from a grounded reference."""
    client = _get_client()
    user_content = (
        f"TRACK: {track_category}\n"
        f"SOURCE URL: {source_url}\n"
        f"TOPIC TITLE: {topic_title}\n\n"
        f"FACTUAL REFERENCE (markdown, may be truncated):\n{reference_markdown}"
    )
    resp = _generate_resilient(
        client,
        model=config.GEMINI_MODEL,
        contents=[_SYSTEM_PROMPT, user_content],
        config={
            "response_mime_type": "application/json",
            "response_schema": VideoRenderPayload,
            "temperature": 0.8,
        },
    )
    payload = VideoRenderPayload.model_validate_json(resp.text)

    # Force the track we actually selected, and enforce the theme rule.
    payload.track_category = track_category  # type: ignore[assignment]
    payload.theme_id = theme_for_track(track_category)  # type: ignore[assignment]
    payload.source_url = payload.source_url or source_url

    _repair_scenes(payload)
    _renumber_scenes(payload)
    _seed_provisional_timings(payload)
    return payload


# ---------------------------------------------------------------------------
# Deterministic safety nets (so no scene / HUD ever renders empty)
# ---------------------------------------------------------------------------
def _ensure_hud(sc: "SceneSpec") -> None:
    """Guarantee 3+ state watches and non-empty HUD text so Zone B never blanks."""
    hud = sc.hud
    if not hud.track_badge.strip():
        hud.track_badge = "STUDY // CONCEPT"
    if not hud.core_formula_or_law.strip():
        hud.core_formula_or_law = "—"
    if not hud.real_world_scale.strip():
        hud.real_world_scale = "—"
    if not hud.governing_rule.strip():
        hud.governing_rule = sc.chapter_title or "The core idea."
    if len(hud.state_watches) < 3:
        existing = len(hud.state_watches)
        for i in range(existing, 3):
            hud.state_watches.append(
                StateWatch(label=f"Parameter {i + 1}", value="—", changed=False)
            )
    # Cap at 5 to keep the panel clean.
    hud.state_watches = hud.state_watches[:5]


def _fallback_formula(sc: "SceneSpec") -> FormulaOrCodePayload:
    hud = sc.hud
    return FormulaOrCodePayload(
        language="text",
        title=sc.chapter_title or "The Mechanism",
        naive_or_before=hud.governing_rule or "The intuitive guess.",
        optimal_or_after=hud.core_formula_or_law or "The real rule.",
        takeaway_caption=hud.real_world_scale or "Why it works at scale.",
    )


def _fallback_matrix(sc: "SceneSpec") -> List[TradeoffRow]:
    hud = sc.hud
    return [
        TradeoffRow(
            dimension="Intuition",
            baseline_option="What feels true",
            clever_option=hud.core_formula_or_law or "What is true",
            winner="clever",
        ),
        TradeoffRow(
            dimension="Outcome",
            baseline_option="Naive result",
            clever_option=hud.real_world_scale or "Real result",
            winner="clever",
        ),
    ]


def _scene_is_empty(sc: "SceneSpec") -> bool:
    vt = sc.visual_type
    if vt == "SequenceGridDryRun":
        return sc.sequence_grid is None or not sc.sequence_grid.cells
    if vt == "SystemAndFlowGraph":
        return len(sc.nodes) < 2
    if vt == "LayeredHardwareStack":
        return not sc.stack_layers
    if vt == "FormulaAndCodeProof":
        return sc.formula_proof is None
    if vt == "ComparisonMatrix":
        return not sc.comparison_rows
    return False


def _repair_scenes(payload: VideoRenderPayload) -> None:
    """Guarantee each scene's HUD and Zone-A visual have data.

    An empty detail scene is rebuilt from its HUD (always fillable) as either a
    FormulaAndCodeProof or a ComparisonMatrix, alternating so two identical
    visuals never land back-to-back.
    """
    for i, sc in enumerate(payload.scenes):
        _ensure_hud(sc)
        if not _scene_is_empty(sc):
            continue
        prev_type = payload.scenes[i - 1].visual_type if i > 0 else None
        if prev_type != "FormulaAndCodeProof":
            sc.visual_type = "FormulaAndCodeProof"
            sc.formula_proof = _fallback_formula(sc)
        else:
            sc.visual_type = "ComparisonMatrix"
            sc.comparison_rows = _fallback_matrix(sc)
        print(
            f"[script] Scene {sc.scene_id} had an empty visual; "
            f"repaired to {sc.visual_type}."
        )


def _renumber_scenes(payload: VideoRenderPayload) -> None:
    for i, sc in enumerate(payload.scenes, start=1):
        sc.scene_id = i


def _seed_provisional_timings(payload: VideoRenderPayload) -> None:
    """Rough timing estimate (~2.6 words/sec) before real TTS alignment."""
    cursor = 0.0
    for scene in payload.scenes:
        words = max(1, len(scene.narration_text.split()))
        dur = round(words / 2.6, 2)
        scene.start_sec = round(cursor, 2)
        scene.duration_sec = dur
        cursor += dur + config.SCENE_GAP_MS / 1000.0
    payload.total_duration_sec = round(cursor, 2)


def save_payload(payload: VideoRenderPayload, path=None) -> None:
    path = path or config.RENDER_PAYLOAD_PATH
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload.model_dump(), fh, indent=2, ensure_ascii=False)
    print(f"[script] Wrote render payload -> {path}")


if __name__ == "__main__":
    print(json.dumps(VideoRenderPayload.model_json_schema(), indent=2)[:1500])
