You have access to our existing `swe-youtube-agent` codebase. We are creating a second, standalone repository called `study-youtube-agent` for a high-retention "Visual Logic, Applied Math, Everyday Tech, Hardware, & Market Mechanics" YouTube channel (inspired by the conceptual clarity of 3Blue1Brown, Primer, Branch Education, and PolyMatter, rendered 100% programmatically in Remotion).

Please scaffold and build `study-youtube-agent` end-to-end by reusing the core infrastructure from `swe-youtube-agent` while implementing the architectural specifications below.

---

# Project Specification: `study-youtube-agent` (Autonomous Visual Concept & Simulation Engine)

## 1. Core Infrastructure to Reuse Directly from `swe-youtube-agent`
Copy and preserve these foundational modules from `swe-youtube-agent`:
1. **`audio_engine.py`**: Keep the Kokoro-82M (`kokoro-onnx`) / `edge-tts` voiceover synthesizer and `faster-whisper` (`base.en`, `int8` CPU) word-level timestamp alignment pipeline.
2. **`telegram_gate.py`, `youtube_publisher.py` & `auth_youtube.py`**: Keep the Telegram Human-in-the-Loop (HITL) preview/approval workflow and the YouTube Data API v3 uploader (`videos.insert`, `thumbnails.set`, `commentThreads.insert`).
3. **`thumbnail_generator.py`**: Keep the Playwright headless Chromium HTML-to-PNG renderer (`1280x720`).
4. **Remotion Core (`video-engine/`)**: Keep the Remotion v4 (`1920x1080`, `60fps`) setup, the **3-Zone Asymmetric Bento HUD** master layout (`MasterComposition.tsx`), `elkjs` deterministic graph layout engine, and `shiki` syntax/formula highlighter.

---

## 2. What to Replace: From "News Scraper" to "6-Track Cross-Disciplinary Curriculum Engine"

Instead of scraping 24-hour developer news, this channel runs on an evergreen **365-Day High-Curiosity Syllabus** paired with Wikipedia/technical reference grounding via Jina Reader.

### 2.1 Replace `ingest_scout.py` with `curriculum_manager.py`
Create `agent-backend/data/curriculum_syllabus.json` pre-populated with at least 60 high-CTR evergreen topics distributed evenly across these **6 viral tracks**:

1. **`EVERYDAY_ALGORITHMS` (How Daily Tech Works Under the Hood):**
   - How Shazam Identifies Any Song in 3 Seconds (Spectrogram Audio Fingerprinting)
   - How QR Codes Survive Being 30% Destroyed (Reed-Solomon Error Correction)
   - How Google Maps Finds the Fastest Route Across 1 Billion Roads in 40ms (Contraction Hierarchies & A*)
   - How GPS Satellites Use Einstein's Relativity to Pinpoint Your Phone to 3 Meters
   - How Uber & Ola Calculate Dynamic Surge Pricing in Real Time
   - How Netflix Streams 4K Video on Slow Wi-Fi Without Buffering (Adaptive Bitrate & AV1 Codec)
   - How Noise-Canceling Headphones Erase Sound Using 180° Destructive Wave Interference
   - How Spam Filters Catch 99.9% of Phishing Emails Using Naive Bayes Probability

2. **`GAME_THEORY_PARADOXES` (Math, Logic & Counter-Intuitive Traps):**
   - Braess's Paradox: Why Adding a New Highway Lane Makes Traffic Worse
   - Survivorship Bias: How World War II Bullet Holes Changed Applied Statistics
   - The Monty Hall Paradox: Why Switching Doors Doubles Your Winning Odds (Simulated 1,000 Times)
   - The Prisoner's Dilemma & Tit-for-Tat: Why Nice Strategies Win in Evolutionary Game Theory
   - Simpson's Paradox: How the Same Data Proves Two Opposite Conclusions
   - The Inspection Paradox: Why Your Bus Is Always Late and Every Flight Feels Full
   - Vickrey Sealed-Bid Auctions: How Google & Meta Price Billions of Ads Per Second
   - The Birthday Paradox: Why Only 23 People Give a 50% Chance of a Shared Birthday

3. **`MONEY_AND_MARKETS` (Financial Engineering, Probability & Economic Plumbing):**
   - How Airlines Legally Overbook Flights Using Binomial Probability Distributions
   - What Happens in the 1,200 Milliseconds After You Swipe a Credit Card (Auth, Clearing & Interchange)
   - How India's UPI Settles 500 Million Daily Peer-to-Peer Transactions With Zero MDR Fees
   - How Casinos Guarantee Profit Using the Law of Large Numbers and House Edge Math
   - How Market Makers & High-Frequency Traders Profit From a $0.01 Bid-Ask Spread
   - How Insurance & Reinsurance Pools Price 1-in-100-Year Catastrophes
   - How Central Bank Repo Rate Changes Ripple Through Mortgages, Bonds, and Inflation
   - How Fractional Reserve Banking Creates Money Through Multiplier Loops

4. **`HARDWARE_AND_PHYSICS` (Physical Engineering & Silicon Marvels):**
   - How ASML Uses Extreme Ultraviolet (EUV) Laser Droplets to Print 2nm Transistors
   - How Undersea Fiber Optic Cables Carry 99% of Global Internet Traffic Using Light Wavelengths (DWDM)
   - How Solid-State and Lithium-Ion Batteries Move Ions Without Catching Fire
   - How Starlink Satellites Steer Internet Beams Without Moving Parts (Phased Array Antennas)
   - How SSDs Store Terabytes of Data by Trapping Electrons in Quantum Flash Cells (NAND Gate Physics)
   - How Capacitive Smartphone Touchscreens Track Your Finger in 120Hz Grids
   - How E-Ink Displays Hold Text for Weeks Using Zero Electricity (Electrophoretic Microcapsules)

5. **`CRYPTO_AND_SECURITY` (Information Theory, Ciphers & Trust):**
   - Zero-Knowledge Proofs: How to Prove You Know a Password Without Ever Revealing It
   - The SHA-256 Avalanche Effect: Why Changing 1 Bit Scrambles the Entire Hash
   - Diffie-Hellman Key Exchange: How Two Strangers Create a Secret Key in Public
   - How the WWII Enigma Machine Worked—And the Flaw That Let Alan Turing Break It
   - How WhatsApp & Signal Encrypt Billions of Messages (The Double Ratchet Protocol)
   - Why Quantum Computers Threaten RSA Encryption (Shor's Algorithm vs Lattice Cryptography)

6. **`CS_AND_AI_INTERNALS` (Core Computing & AI Demystified for Everyone):**
   - How Large Language Models Predict the Next Word Using Self-Attention Matrices
   - How Database B+ Trees Find 1 Record Out of 100 Million in 3 Disk Seeks
   - Bloom Filters: How Chrome Checks If a URL Is Malicious Using Almost Zero Memory
   - How Git Stores Thousands of Code Versions Without Duplicating Files (Merkle DAGs)
   - How TCP Congestion Control Prevents the Global Internet From Collapsing
   - How AI Image Generators Turn Random Static Noise Into Photorealistic Art (Diffusion Math)

**Selection Logic in `curriculum_manager.py`:**
- If `--topic "..."` is passed via CLI or GitHub Actions `workflow_dispatch`, use that custom prompt directly and classify it into the closest track.
- Otherwise, query `seen_topics.db` and pick the next unpublished topic from `curriculum_syllabus.json` using **strict round-robin track rotation** (`Track 1 -> Track 2 -> Track 3 -> Track 4 -> Track 5 -> Track 6`), ensuring the channel stays fresh and appeals to both STEM/CS audiences and mainstream curious viewers.

### 2.2 Replace `article_scraper.py` with `reference_gatherer.py`
- Given the chosen topic title and reference query, fetch clean factual Markdown via `https://r.jina.ai/https://en.wikipedia.org/wiki/{slug}` (plus a secondary search via DuckDuckGo/Google News RSS if needed) so Gemini 2.5 Flash is grounded in real equations, physical units, historical numbers, and step-by-step mechanics.

---

## 3. Strict Data Contract: `script_generator.py` $\leftrightarrow$ `video-engine/src/types/schema.ts`

Both the Python backend (`script_generator.py`) and Remotion frontend (`schema.ts`) must enforce this universal simulation schema (`render_payload.json`):

```python
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class WordTimestamp(BaseModel):
    word: str
    start_sec: float
    end_sec: float

class StateWatch(BaseModel):
    label: str = Field(description="Variable, metric, or parameter name, e.g. 'Switching Win %', 'Wave Phase', 'Disk Seeks', 'Expected Value'")
    value: str = Field(description="Current value at this step, e.g. '66.7% (2/3)', '180° Inverted', '3 Hops', '+$14.20'")
    changed: bool = Field(default=False, description="True if updated in this scene so HUD flashes highlight")

class ConceptHUD(BaseModel):
    track_badge: str = Field(description="e.g. 'GAME THEORY // PARADOX' or 'EVERYDAY TECH // AUDIO'")
    core_formula_or_law: str = Field(description="Key equation, complexity, or principle, e.g. 'P(Win|Switch) = 2/3', 'O(log_b N)', 'E = hf'")
    real_world_scale: str = Field(description="Concrete scale metric, e.g. '40ms across 1B roads' or '99.98% Noise Reduction'")
    governing_rule: str = Field(description="1-sentence invariant explaining why this step works")
    state_watches: List[StateWatch] = Field(description="3 to 5 live simulation parameters updating each scene")

class GridCellItem(BaseModel):
    index_label: str = Field(description="e.g. 'Door #1', 'Bit 04', 'Seat 180', 'Freq 820Hz'")
    value: str = Field(description="e.g. '🐐 Goat', '🚗 Car', '0x4F', '+1.0 dB'")
    state: Literal["default", "active_focus", "comparing", "optimal_hit", "eliminated"] = "default"
    pointer_tags: List[str] = Field(default_factory=list, description="e.g. ['Your Pick', 'Host Opens', 'Pointer L']")

class SequenceGridPayload(BaseModel):
    title: str
    cells: List[GridCellItem]
    highlight_range_start: Optional[int] = None
    highlight_range_end: Optional[int] = None
    step_caption: str = Field(description="Action summary, e.g. 'Host eliminates Door #3 -> 2/3 probability concentrates on Door #2'")

class GraphNode(BaseModel):
    id: str
    label: str
    sublabel: str = Field(description="e.g. 'Delay: 12ms', 'Fee: 0.3%', 'Payoff: (-5, -5)'")
    icon_slug: Optional[str] = None
    tier: int = Field(default=1, description="1 to 5 for left-to-right or top-to-bottom layout")
    status: Literal["neutral", "active", "optimal_path", "bottleneck", "eliminated"] = "neutral"

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = Field(default=None, description="Flow label, probability, or cost, e.g. 'p = 0.67' or '+45 mins'")
    packet_color: Literal["cyan", "orange", "crimson", "emerald"] = "cyan"
    animate_packets: bool = True

class StackLayerBlock(BaseModel):
    layer_label: str = Field(description="e.g. 'L1: Acoustic Mic', 'L2: ADC Chip', 'L3: Inverted Speaker Wave'")
    detail_text: str = Field(description="e.g. 'Samples ambient 200Hz engine drone every 20 microseconds'")
    metric_badge: str = Field(description="e.g. '-32 dB' or '0.02ms'")
    status: Literal["idle", "processing", "success", "critical_fault"] = "processing"

class FormulaOrCodePayload(BaseModel):
    language: str = Field(description="'python', 'sql', 'math', or 'text'")
    title: str
    naive_or_before: str = Field(description="Intuitive/wrong assumption or brute-force formula/code")
    optimal_or_after: str = Field(description="Actual mathematical proof, optimal algorithm, or physical equation")
    takeaway_caption: str

class TradeoffRow(BaseModel):
    dimension: str = Field(description="e.g. 'Lookup Speed', 'Expected Payout', 'Power Draw'")
    baseline_option: str = Field(description="e.g. 'Stick with Door #1 (33.3%)' or 'LCD Backlight'")
    clever_option: str = Field(description="e.g. 'Switch to Door #2 (66.7%)' or 'E-Ink Microcapsules'")
    winner: Literal["baseline", "clever"] = "clever"

class SceneSpec(BaseModel):
    scene_id: int
    chapter_title: str = Field(description="Short 2-4 word progress label, e.g. '01 THE PARADOX', '02 TOY SIMULATION'")
    narration_text: str = Field(description="Engaging, crystal-clear spoken narration (18 to 32 words)")
    start_sec: float = 0.0
    duration_sec: float = 8.0
    visual_type: Literal["SequenceGridDryRun", "SystemAndFlowGraph", "LayeredHardwareStack", "FormulaAndCodeProof", "ComparisonMatrix"]
    camera_focus_node_id: Optional[str] = None
    hud: ConceptHUD
    sequence_grid: Optional[SequenceGridPayload] = None
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    stack_layers: List[StackLayerBlock] = Field(default_factory=list)
    formula_proof: Optional[FormulaOrCodePayload] = None
    comparison_rows: List[TradeoffRow] = Field(default_factory=list)
    callout_keywords: List[str] = Field(default_factory=list)

class ThumbnailSpec(BaseModel):
    headline_text: str = Field(description="Strictly 3 to 4 bold high-curiosity words, e.g. 'ADD ROAD = MORE TRAFFIC?' or '3 SECONDS TO MATCH'")
    badge_text: str = Field(description="e.g. 'GAME THEORY' or 'HOW IT WORKS'")
    left_label: str = Field(description="e.g. '4 Lanes: 45 Min' or 'Raw Audio Wave'")
    right_label: str = Field(description="e.g. '5 Lanes: 62 Min!' or 'Hash Spectrogram'")
    connector_style: Literal["vs_bolt", "upgrade_arrow", "broken_arrow"]

class VideoRenderPayload(BaseModel):
    track_category: Literal[
        "EVERYDAY_ALGORITHMS",
        "GAME_THEORY_PARADOXES",
        "MONEY_AND_MARKETS",
        "HARDWARE_AND_PHYSICS",
        "CRYPTO_AND_SECURITY",
        "CS_AND_AI_INTERNALS"
    ]
    theme_id: Literal["ARCHIVAL_LAB_PAPER", "QUANTUM_SIM_HUD"]
    youtube_title: str = Field(description="High-CTR curiosity-gap title under 70 characters")
    youtube_description: str
    youtube_tags: List[str]
    pinned_comment: str = Field(description="Interactive brain-teaser or counter-intuitive question that drives debate in comments")
    source_url: str
    thumbnail: ThumbnailSpec
    scenes: List[SceneSpec]
    words: List[WordTimestamp] = Field(default_factory=list)
    total_duration_sec: float = 0.0
```

---

## 4. Prompt Engineering Rules in `script_generator.py` (The 4-Act Visual Curiosity Arc)

Configure Gemini 2.5 Flash to structure every video (8 to 10 scenes, ~75 to 115 seconds total) around this 4-act storytelling arc:
1. **Act 1 — The Counter-Intuitive Hook (Scenes 1–2):** Open with a concrete paradox or everyday miracle backed by hard numbers (*"In 1990, Stuttgart closed a major downtown highway—and city-wide traffic immediately got faster. Here is the mathematical trap called Braess's Paradox that fools civil engineers."*).
2. **Act 2 — The Toy Model Simulation (Scenes 3–6):** Never stay abstract. Construct a concrete, small-scale simulation using numbers a viewer can follow on screen (e.g., 4,000 drivers choosing between 2 bridges, 3 Monty Hall doors, 200 airline seats with a 5% no-show rate, or 4 spectrogram frequency peaks in Shazam). Mutate the `sequence_grid`, `nodes`, and `hud.state_watches` across consecutive scenes so the viewer watches the math/system play out step by step.
3. **Act 3 — The Formula & Real-World Scale (Scenes 7–8):** Show the underlying equation or code (`FormulaAndCodeProof`) and the head-to-head comparison (`ComparisonMatrix`).
4. **Act 4 — The Comment Brain-Teaser (Final Scene & Pinned Comment):** Pose a twist on the scenario (*"What happens to this equilibrium if tolls are dynamic instead of fixed? Drop your prediction in the comments!"*).

---

## 5. Remotion Visual Engine Specifications (`video-engine/src/`)

### 5.1 Zone B Upgrade: `ZoneBConceptHUD.tsx` (Right 26% Live Simulation Sidebar)
- **Panel 1 (Domain & Law Card):** Displays `hud.track_badge`, a large monospace box for **`hud.core_formula_or_law`**, and `hud.real_world_scale`.
- **Panel 2 (Live Simulation Parameter Watches):** Renders `hud.state_watches` as an interactive lab readout. Whenever `watch.changed === true` in the current scene, trigger a smooth spring highlight pulse on that row.
- **Panel 3 (Governing Rule Callout):** Displays `hud.governing_rule` inside a high-contrast callout frame.

### 5.2 Zone A Universal Scene Components (`video-engine/src/components/scenes/`)
1. **`SequenceGridDryRun.tsx` (`visual_type === "SequenceGridDryRun"`):**
   - Renders `sequence_grid.cells` as crisp interactive cards/boxes (works for array indices, Monty Hall doors, airline seats, frequency bins, or SHA-256 bit blocks).
   - Animates pointer badges (`pointer_tags`) sliding smoothly across cells and highlights active ranges (`highlight_range_start` to `highlight_range_end`).
2. **`SystemAndFlowGraph.tsx` (`visual_type === "SystemAndFlowGraph"`):**
   - Uses `elkjs` auto-layout to render game-theory payoff trees, traffic road networks, credit-card clearing hops, or B+ trees with animated SVG packets and camera zoom (`camera_focus_node_id`).
3. **`LayeredHardwareStack.tsx` (`visual_type === "LayeredHardwareStack"`):**
   - Renders physical or logical layers (`stack_layers`) with animated signal waves passing vertically through layers (ideal for Noise-Canceling Headphones, EUV Lithography, OSI/TCP stacks, or OLED/E-Ink cross-sections).
4. **`FormulaAndCodeProof.tsx` & `ComparisonMatrix.tsx`:**
   - Uses `shiki` and large clean typography to contrast the Naive Intuition vs. Mathematical/Engineering Reality.

### 5.3 Dual Brand Themes (`src/styles/themes.ts`)
- **`ARCHIVAL_LAB_PAPER`** *(Default for `GAME_THEORY_PARADOXES`, `EVERYDAY_ALGORITHMS`, `MONEY_AND_MARKETS`)*: Warm archival drafting paper (`#F4F1EA`), millimeter grid lines (`#E2DDD2`), stark ink borders (`2px solid #18181B`), hard offset shadows (`4px 4px 0px #18181B`), International Orange (`#FF4F00`) and Cobalt (`#0047AB`).
- **`QUANTUM_SIM_HUD`** *(Default for `HARDWARE_AND_PHYSICS`, `CRYPTO_AND_SECURITY`, `CS_AND_AI_INTERNALS`)*: Deep obsidian (`#090D16`), dot-matrix grid, laboratory oscilloscope frames (`#1E293B`), Cyan (`#38BDF8`), Emerald (`#10B981`), and Amber (`#F59E0B`).

---

## 6. Verification & End-to-End Dry Run
1. Populate `video-engine/public/assets/render_payload.json` with a complete 6-scene mock payload explaining **Braess's Paradox (Why Adding a Road Makes Traffic Worse)** using `SystemAndFlowGraph`, `SequenceGridDryRun`, `FormulaAndCodeProof`, and `ComparisonMatrix`.
2. Run `npm run render` in `video-engine/` and verify that `final_video.mp4` compiles cleanly at `1920x1080` 60fps.
3. Verify that `python main.py --dry-run` in `agent-backend/` selects the next topic from `curriculum_syllabus.json`, fetches reference context via Jina Reader, generates the Pydantic JSON via Gemini 2.5 Flash, synthesizes voiceover + word timestamps, renders `thumbnail.png`, and compiles the final MP4.