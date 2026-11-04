// Dual brand themes for the study channel (requirement 5.3).
//
// ARCHIVAL_LAB_PAPER = warm archival drafting paper (LIGHT) — the default for
//   GAME_THEORY_PARADOXES / EVERYDAY_ALGORITHMS / MONEY_AND_MARKETS.
// QUANTUM_SIM_HUD    = deep obsidian oscilloscope console (DARK) — the default
//   for HARDWARE_AND_PHYSICS / CRYPTO_AND_SECURITY / CS_AND_AI_INTERNALS.

import type React from "react";
import type {
  ThemeId,
  GraphNodeStatus,
  GridCellState,
  StackStatus,
  PacketColor,
} from "../types/schema";

export interface Theme {
  id: ThemeId;
  mode: "light" | "dark";
  canvasBg: string;
  canvasBg2: string;
  gridColor: string;
  gridKind: "rule" | "dot";
  panelBg: string;
  ink: string; // border / outline ink
  borderStyle: string; // full CSS border shorthand
  hardShadow: string; // offset block shadow (paper) or glow (hud)
  textPrimary: string;
  textMuted: string;
  textOnAccent: string;
  accentPrimary: string;
  accentSecondary: string;
  accentPositive: string;
  accentWarning: string;
  accentCritical: string;
  fontHeading: string;
  fontMono: string;
  nodeStatusColors: Record<GraphNodeStatus, string>;
  cellStateColors: Record<GridCellState, string>;
  stackStatusColors: Record<StackStatus, string>;
  packetColors: Record<PacketColor, string>;
  shikiTheme: string;
}

export const ARCHIVAL_LAB_PAPER: Theme = {
  id: "ARCHIVAL_LAB_PAPER",
  mode: "light",
  canvasBg: "#F4F1EA",
  canvasBg2: "#ECE7DB",
  gridColor: "#E2DDD2",
  gridKind: "rule",
  panelBg: "#FBFAF5",
  ink: "#18181B",
  borderStyle: "2px solid #18181B",
  hardShadow: "4px 4px 0px #18181B",
  textPrimary: "#18181B",
  textMuted: "#6B6459",
  textOnAccent: "#FFFFFF",
  accentPrimary: "#FF4F00", // International Orange
  accentSecondary: "#0047AB", // Cobalt
  accentPositive: "#0A7D4B",
  accentWarning: "#B45309",
  accentCritical: "#C81E1E",
  fontHeading: "'Space Grotesk', 'Helvetica Neue', Arial, sans-serif",
  fontMono: "'IBM Plex Mono', 'Consolas', monospace",
  nodeStatusColors: {
    neutral: "#6B6459",
    active: "#0047AB",
    optimal_path: "#0A7D4B",
    bottleneck: "#C81E1E",
    eliminated: "#B8B0A2",
  },
  cellStateColors: {
    default: "#8A8276",
    active_focus: "#FF4F00",
    comparing: "#0047AB",
    optimal_hit: "#0A7D4B",
    eliminated: "#B8B0A2",
  },
  stackStatusColors: {
    idle: "#8A8276",
    processing: "#0047AB",
    success: "#0A7D4B",
    critical_fault: "#C81E1E",
  },
  packetColors: {
    cyan: "#0047AB",
    orange: "#FF4F00",
    crimson: "#C81E1E",
    emerald: "#0A7D4B",
  },
  shikiTheme: "github-light",
};

export const QUANTUM_SIM_HUD: Theme = {
  id: "QUANTUM_SIM_HUD",
  mode: "dark",
  canvasBg: "#090D16",
  canvasBg2: "#0C121F",
  gridColor: "#1E293B",
  gridKind: "dot",
  panelBg: "#0E1626",
  ink: "#1E293B",
  borderStyle: "1px solid #24324A",
  hardShadow: "0 0 30px rgba(56,189,248,0.12)",
  textPrimary: "#E5EEF7",
  textMuted: "#64748B",
  textOnAccent: "#05060A",
  accentPrimary: "#38BDF8", // Cyan
  accentSecondary: "#10B981", // Emerald
  accentPositive: "#10B981",
  accentWarning: "#F59E0B", // Amber
  accentCritical: "#FB7185",
  fontHeading: "'Space Grotesk', 'Segoe UI', sans-serif",
  fontMono: "'JetBrains Mono', 'Consolas', monospace",
  nodeStatusColors: {
    neutral: "#64748B",
    active: "#38BDF8",
    optimal_path: "#10B981",
    bottleneck: "#FB7185",
    eliminated: "#3A475C",
  },
  cellStateColors: {
    default: "#64748B",
    active_focus: "#38BDF8",
    comparing: "#F59E0B",
    optimal_hit: "#10B981",
    eliminated: "#3A475C",
  },
  stackStatusColors: {
    idle: "#64748B",
    processing: "#38BDF8",
    success: "#10B981",
    critical_fault: "#FB7185",
  },
  packetColors: {
    cyan: "#38BDF8",
    orange: "#F59E0B",
    crimson: "#FB7185",
    emerald: "#10B981",
  },
  shikiTheme: "github-dark",
};

export const THEMES: Record<ThemeId, Theme> = {
  ARCHIVAL_LAB_PAPER,
  QUANTUM_SIM_HUD,
};

export const getTheme = (id: ThemeId): Theme => THEMES[id] ?? ARCHIVAL_LAB_PAPER;

// CSS background for the canvas grid, given a theme. `rule` = millimeter
// drafting grid (fine + coarse lines), `dot` = dot-matrix.
export const gridBackground = (theme: Theme): React.CSSProperties => {
  if (theme.gridKind === "dot") {
    return {
      backgroundColor: theme.canvasBg,
      backgroundImage: `radial-gradient(${theme.gridColor} 1.5px, transparent 1.5px)`,
      backgroundSize: "26px 26px",
    };
  }
  // Millimeter paper: fine 1px grid every 20px + a heavier line every 100px.
  return {
    backgroundColor: theme.canvasBg,
    backgroundImage: [
      `linear-gradient(${theme.gridColor} 1px, transparent 1px)`,
      `linear-gradient(90deg, ${theme.gridColor} 1px, transparent 1px)`,
      `linear-gradient(${theme.gridColor} 1px, transparent 1px)`,
      `linear-gradient(90deg, ${theme.gridColor} 1px, transparent 1px)`,
    ].join(", "),
    backgroundSize: "100px 100px, 100px 100px, 20px 20px, 20px 20px",
  };
};
