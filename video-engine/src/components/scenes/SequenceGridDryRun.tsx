import React from "react";
import { spring, interpolate } from "remotion";
import type { SceneSpec } from "../../types/schema";
import type { Theme } from "../../styles/themes";

interface Props {
  scene: SceneSpec;
  theme: Theme;
  localFrame: number;
  fps: number;
}

// Renders sequence_grid.cells as crisp interactive cards (array indices, Monty
// Hall doors, airline seats, frequency bins, SHA bit blocks). Pointer badges
// slide in and the active range glows. (requirement 5.2.1)
export const SequenceGridDryRun: React.FC<Props> = ({ scene, theme, localFrame, fps }) => {
  const grid = scene.sequence_grid;
  const paper = theme.mode === "light";
  if (!grid || grid.cells.length === 0) {
    return null;
  }

  const n = grid.cells.length;
  const cols = Math.min(n, Math.ceil(Math.sqrt(n * 1.4)));
  const inRange = (i: number) =>
    grid.highlight_range_start != null &&
    grid.highlight_range_end != null &&
    i >= grid.highlight_range_start &&
    i <= grid.highlight_range_end;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <div
        style={{
          fontFamily: theme.fontHeading,
          fontSize: 30,
          fontWeight: 700,
          color: theme.textPrimary,
        }}
      >
        {grid.title}
      </div>

      <div
        style={{
          flex: 1,
          display: "grid",
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gap: 18,
          alignContent: "center",
        }}
      >
        {grid.cells.map((cell, i) => {
          const enter = spring({
            frame: localFrame - i * 3,
            fps,
            config: { damping: 15, stiffness: 150 },
          });
          const accent = theme.cellStateColors[cell.state];
          const lit = cell.state !== "default" && cell.state !== "eliminated";
          const eliminated = cell.state === "eliminated";
          const ring = inRange(i);
          return (
            <div
              key={`${cell.index_label}-${i}`}
              style={{
                position: "relative",
                minHeight: 112,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                padding: "14px 12px",
                background: paper
                  ? lit
                    ? `${accent}18`
                    : "#FFFFFF"
                  : lit
                    ? `${accent}1E`
                    : "rgba(255,255,255,0.03)",
                border: `${paper ? 2 : 1.5}px solid ${
                  lit ? accent : paper ? theme.ink : "#223049"
                }`,
                borderRadius: paper ? 4 : 12,
                boxShadow: lit
                  ? `0 0 ${18}px ${accent}66${paper ? "" : ""}` +
                    (paper ? `, ${theme.hardShadow}` : "")
                  : ring
                    ? `0 0 0 3px ${theme.accentSecondary}55`
                    : paper
                      ? theme.hardShadow
                      : "none",
                opacity: eliminated ? 0.4 : Math.min(1, enter * 1.2),
                transform: `translateY(${(1 - enter) * 18}px) scale(${0.9 + enter * 0.1})`,
              }}
            >
              <div
                style={{
                  fontFamily: theme.fontMono,
                  fontSize: 13,
                  letterSpacing: 1,
                  textTransform: "uppercase",
                  color: theme.textMuted,
                }}
              >
                {cell.index_label}
              </div>
              <div
                style={{
                  fontFamily: theme.fontHeading,
                  fontSize: n > 24 ? 20 : 30,
                  fontWeight: 800,
                  color: lit ? accent : theme.textPrimary,
                  textAlign: "center",
                  textDecoration: eliminated ? "line-through" : "none",
                  lineHeight: 1.05,
                  wordBreak: "break-word",
                }}
              >
                {cell.value}
              </div>

              {/* Pointer badges slide in above the cell. */}
              {cell.pointer_tags.map((tag, t) => {
                const pIn = spring({
                  frame: localFrame - 10 - t * 6,
                  fps,
                  config: { damping: 16, stiffness: 140 },
                });
                return (
                  <div
                    key={tag}
                    style={{
                      position: "absolute",
                      top: -16 - t * 30,
                      fontFamily: theme.fontMono,
                      fontSize: 13,
                      fontWeight: 700,
                      letterSpacing: 0.5,
                      padding: "4px 10px",
                      borderRadius: 999,
                      whiteSpace: "nowrap",
                      color: theme.textOnAccent,
                      background: theme.accentPrimary,
                      boxShadow: `0 4px 14px ${theme.accentPrimary}55`,
                      opacity: pIn,
                      transform: `translateY(${(1 - pIn) * 10}px)`,
                    }}
                  >
                    {tag}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>

      <div
        style={{
          fontFamily: theme.fontMono,
          fontSize: 20,
          color: theme.textMuted,
          borderTop: `1px solid ${paper ? "#D9D3C6" : "#1C2840"}`,
          paddingTop: 14,
        }}
      >
        <span style={{ color: theme.accentPrimary, fontWeight: 700 }}>▸ </span>
        {grid.step_caption}
      </div>
    </div>
  );
};
