import React from "react";
import { spring } from "remotion";
import type { SceneSpec } from "../../types/schema";
import type { Theme } from "../../styles/themes";

interface Props {
  scene: SceneSpec;
  theme: Theme;
  localFrame: number;
  fps: number;
}

// Head-to-head trade-off table: baseline vs clever, winner highlighted.
// (requirement 5.2.4 — ComparisonMatrix)
export const ComparisonMatrix: React.FC<Props> = ({ scene, theme, localFrame, fps }) => {
  const rows = scene.comparison_rows;
  const paper = theme.mode === "light";
  if (!rows || rows.length === 0) return null;

  const cell = (text: string, win: boolean, align: "left" | "center") => (
    <div
      style={{
        flex: align === "left" ? "0 0 300px" : 1,
        padding: "18px 22px",
        fontFamily: align === "left" ? theme.fontMono : theme.fontHeading,
        fontSize: align === "left" ? 19 : 22,
        fontWeight: win ? 800 : 600,
        color: win ? theme.textOnAccent : theme.textPrimary,
        background: win ? theme.accentPositive : "transparent",
        borderRadius: win ? (paper ? 3 : 8) : 0,
        textAlign: align,
        display: "flex",
        alignItems: "center",
        justifyContent: align === "center" ? "center" : "flex-start",
        gap: 10,
      }}
    >
      {win ? <span style={{ fontSize: 20 }}>✓</span> : null}
      <span style={{ wordBreak: "break-word" }}>{text}</span>
    </div>
  );

  return (
    <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", gap: 14 }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "stretch", gap: 10 }}>
        {["DIMENSION", "BASELINE", "CLEVER MOVE"].map((h, i) => (
          <div
            key={h}
            style={{
              flex: i === 0 ? "0 0 300px" : 1,
              padding: "12px 22px",
              fontFamily: theme.fontMono,
              fontSize: 16,
              letterSpacing: 2,
              fontWeight: 700,
              textTransform: "uppercase",
              color: i === 2 ? theme.accentPrimary : theme.textMuted,
              textAlign: i === 0 ? "left" : "center",
            }}
          >
            {h}
          </div>
        ))}
      </div>

      {rows.map((row, i) => {
        const enter = spring({ frame: localFrame - i * 6, fps, config: { damping: 18, stiffness: 140 } });
        return (
          <div
            key={`${row.dimension}-${i}`}
            style={{
              display: "flex",
              alignItems: "stretch",
              gap: 10,
              background: paper ? "#FFFFFF" : "rgba(255,255,255,0.03)",
              border: theme.borderStyle,
              borderRadius: paper ? 4 : 12,
              boxShadow: paper ? theme.hardShadow : "none",
              overflow: "hidden",
              opacity: Math.min(1, enter * 1.2),
              transform: `translateY(${(1 - enter) * 22}px)`,
            }}
          >
            {cell(row.dimension, false, "left")}
            {cell(row.baseline_option, row.winner === "baseline", "center")}
            {cell(row.clever_option, row.winner === "clever", "center")}
          </div>
        );
      })}
    </div>
  );
};
