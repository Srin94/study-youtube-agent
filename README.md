# First Principles — Autonomous Study-Video Agent

A standalone pipeline that turns one evergreen STEM concept per day into a
high-retention, 100%-programmatic explainer video (Remotion, 1920×1080 @ 60fps)
in the lineage of 3Blue1Brown, Primer and Branch Education — then gates it
through a Telegram human review before publishing to YouTube.

Sibling of `swe-youtube-agent`; it reuses that project's proven audio, thumbnail,
Telegram and YouTube infrastructure and replaces the news scraper with a
6-track evergreen curriculum engine and a universal concept-simulation contract.

## The six curriculum tracks

Topics rotate strictly Track 1 → Track 6 → Track 1 (see `curriculum_syllabus.json`):

1. `EVERYDAY_ALGORITHMS` — how daily tech works under the hood
2. `GAME_THEORY_PARADOXES` — math, logic & counter-intuitive traps
3. `MONEY_AND_MARKETS` — financial engineering, probability & economic plumbing
4. `HARDWARE_AND_PHYSICS` — physical engineering & silicon marvels
5. `CRYPTO_AND_SECURITY` — information theory, ciphers & trust
6. `CS_AND_AI_INTERNALS` — core computing & AI demystified

## Pipeline

```
curriculum_manager → reference_gatherer (Jina/Wikipedia) → script_generator (Gemini)
  → audio_engine (Kokoro/edge-tts + faster-whisper) → thumbnail_generator (Playwright)
  → Remotion render (StudyMasterVideo) → telegram_gate → youtube_publisher
```

Every video is structured on the **4-Act Visual Curiosity Arc**: the
counter-intuitive hook, a concrete toy-model simulation, the formula & real-world
scale, and a comment brain-teaser. Each scene carries a live **ConceptHUD**
(Zone B) plus one of five universal Zone-A visuals: `SequenceGridDryRun`,
`SystemAndFlowGraph`, `LayeredHardwareStack`, `FormulaAndCodeProof`,
`ComparisonMatrix`.

## Data contract

`agent-backend/src/script_generator.py` (Pydantic) and
`video-engine/src/types/schema.ts` (TypeScript) are a one-to-one mirror of the
`VideoRenderPayload` contract and MUST stay in lock-step.

## Run it

```bash
# Backend deps
pip install -r agent-backend/requirements.txt
playwright install chromium

# Video engine deps
cd video-engine && npm install && cd ..
```

Copy `.env.example` to `.env` and fill in `GEMINI_API_KEY` (plus Telegram /
YouTube credentials for publishing).

```bash
# Render the bundled Braess's Paradox mock (no LLM, no secrets needed)
cd video-engine && npm run render

# Full local dry-run — next curriculum topic, real Gemini, NO publish, NO Telegram
cd agent-backend && python main.py --dry-run --skip-approval

# A specific topic
python main.py --topic "How Bloom Filters Work" --dry-run --skip-approval
```

`--skip-approval` bypasses the Telegram gate for local testing — always pair it
with `--dry-run` so nothing is ever published. The daily GitHub Action
(`.github/workflows/daily_study_video.yml`) runs the full gated pipeline.

## Themes

- `ARCHIVAL_LAB_PAPER` (light, warm drafting paper) — tracks 1–3.
- `QUANTUM_SIM_HUD` (dark obsidian oscilloscope) — tracks 4–6.
