// TypeScript mirror of the Python Pydantic VideoRenderPayload contract in
// agent-backend/src/script_generator.py. These two MUST stay in lock-step.
//
// This is the universal "concept & simulation" contract for the study channel:
// every scene carries a live ConceptHUD (Zone B) plus exactly one Zone-A visual
// payload selected by `visual_type`.

export interface WordTimestamp {
  word: string;
  start_sec: number;
  end_sec: number;
}

// ---------------------------------------------------------------------------
// Zone B — the live concept HUD
// ---------------------------------------------------------------------------
export interface StateWatch {
  label: string; // e.g. "Switching Win %", "Wave Phase", "Disk Seeks"
  value: string; // e.g. "66.7% (2/3)", "180° Inverted", "3 Hops"
  changed: boolean; // true => HUD flashes a highlight pulse on this row
}

export interface ConceptHUD {
  track_badge: string; // "GAME THEORY // PARADOX"
  core_formula_or_law: string; // "P(Win|Switch) = 2/3", "O(log_b N)", "E = hf"
  real_world_scale: string; // "40ms across 1B roads"
  governing_rule: string; // 1-sentence invariant for this step
  state_watches: StateWatch[]; // 3 to 5 live params updating each scene
}

// ---------------------------------------------------------------------------
// Zone A — five universal visual payloads
// ---------------------------------------------------------------------------
export type GridCellState =
  | "default"
  | "active_focus"
  | "comparing"
  | "optimal_hit"
  | "eliminated";

export interface GridCellItem {
  index_label: string; // "Door #1", "Bit 04", "Seat 180"
  value: string; // "Goat", "Car", "0x4F", "+1.0 dB"
  state: GridCellState;
  pointer_tags: string[]; // ["Your Pick", "Host Opens"]
}

export interface SequenceGridPayload {
  title: string;
  cells: GridCellItem[];
  highlight_range_start?: number | null;
  highlight_range_end?: number | null;
  step_caption: string;
}

export type GraphNodeStatus =
  | "neutral"
  | "active"
  | "optimal_path"
  | "bottleneck"
  | "eliminated";

export interface GraphNode {
  id: string;
  label: string;
  sublabel: string; // "Delay: 12ms", "Fee: 0.3%", "Payoff: (-5,-5)"
  icon_slug?: string | null;
  tier: number; // 1..5 left-to-right / top-to-bottom layer
  status: GraphNodeStatus;
}

export type PacketColor = "cyan" | "orange" | "crimson" | "emerald";

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string | null; // "p = 0.67", "+45 mins"
  packet_color: PacketColor;
  animate_packets: boolean;
}

export type StackStatus = "idle" | "processing" | "success" | "critical_fault";

export interface StackLayerBlock {
  layer_label: string; // "L1: Acoustic Mic", "L2: ADC Chip"
  detail_text: string;
  metric_badge: string; // "-32 dB", "0.02ms"
  status: StackStatus;
}

export interface FormulaOrCodePayload {
  language: string; // "python" | "sql" | "math" | "text"
  title: string;
  naive_or_before: string; // intuitive/wrong assumption or brute-force
  optimal_or_after: string; // actual proof / optimal algorithm / equation
  takeaway_caption: string;
}

export type TradeoffWinner = "baseline" | "clever";

export interface TradeoffRow {
  dimension: string; // "Lookup Speed", "Expected Payout"
  baseline_option: string; // "Stick with Door #1 (33.3%)"
  clever_option: string; // "Switch to Door #2 (66.7%)"
  winner: TradeoffWinner;
}

export type VisualType =
  | "SequenceGridDryRun"
  | "SystemAndFlowGraph"
  | "LayeredHardwareStack"
  | "FormulaAndCodeProof"
  | "ComparisonMatrix";

export interface SceneSpec {
  scene_id: number;
  chapter_title: string; // "01 THE PARADOX"
  narration_text: string; // 18-32 spoken words
  start_sec: number;
  duration_sec: number;
  visual_type: VisualType;
  camera_focus_node_id?: string | null;
  hud: ConceptHUD;
  sequence_grid?: SequenceGridPayload | null;
  nodes: GraphNode[];
  edges: GraphEdge[];
  stack_layers: StackLayerBlock[];
  formula_proof?: FormulaOrCodePayload | null;
  comparison_rows: TradeoffRow[];
  callout_keywords: string[];
}

export type ConnectorStyle = "vs_bolt" | "upgrade_arrow" | "broken_arrow";

export interface ThumbnailSpec {
  headline_text: string; // strictly 3-4 bold words
  badge_text: string; // "GAME THEORY", "HOW IT WORKS"
  left_label: string; // "4 Lanes: 45 Min"
  right_label: string; // "5 Lanes: 62 Min!"
  connector_style: ConnectorStyle;
}

export type TrackCategory =
  | "EVERYDAY_ALGORITHMS"
  | "GAME_THEORY_PARADOXES"
  | "MONEY_AND_MARKETS"
  | "HARDWARE_AND_PHYSICS"
  | "CRYPTO_AND_SECURITY"
  | "CS_AND_AI_INTERNALS";

export type ThemeId = "ARCHIVAL_LAB_PAPER" | "QUANTUM_SIM_HUD";

export interface VideoRenderPayload {
  track_category: TrackCategory;
  theme_id: ThemeId;
  youtube_title: string; // curiosity-gap, < 70 chars
  youtube_description: string;
  youtube_tags: string[];
  pinned_comment: string; // interactive brain-teaser
  source_url: string;
  thumbnail: ThumbnailSpec;
  scenes: SceneSpec[];
  words: WordTimestamp[];
  total_duration_sec: number;
}
