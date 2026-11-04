import React from "react";
import { spring, interpolate } from "remotion";
import type { ConceptHUD } from "../types/schema";
import type { Theme } from "../styles/themes";

interface Props {
  theme: Theme;
  hud: ConceptHUD;
  localFrame: number;
  fps: number;
}

// The right 26% live-simulation sidebar (requirement 5.1). Three stacked
// panels: Domain & Law, live State Watches (pulse on change), Governing Rule.
export const ZoneBConceptHUD: React.FC<Props> = ({ theme, hud, localFrame, fps }) => {
  const paper = theme.mode === "light";

  const panelStyle: React.CSSProperties = {
    background: theme.panelBg,
    border: theme.borderStyle,
    borderRadius: paper ? 4 : 14,
    boxShadow: theme.hardShadow,
    padding: "22px 22px",
  };

  const labelMono: React.CSSProperties = {
    fontFamily: theme.fontMono,
    fontSize: 15,
    letterSpacing: 2,
    textTransform: "uppercase",
    color: theme.textMuted,
    fontWeight: 700,
  };

  // Entrance: the HUD rises + fades in on each scene cut.
  const enter = interpolate(localFrame, [0, 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 150,
        right: 56,
        bottom: 56,
        width: 440,
        display: "flex",
        flexDirection: "column",
        gap: 20,
        zIndex: 4,
        opacity: enter,
        transform: `translateX(${interpolate(enter, [0, 1], [26, 0])}px)`,
      }}
    >
      {/* Panel 1 — Domain & Law card */}
      <div style={panelStyle}>
        <div style={{ ...labelMono, color: theme.accentPrimary }}>
          {hud.track_badge || "STUDY // CONCEPT"}
        </div>
        <div
          style={{
            marginTop: 16,
            fontFamily: theme.fontMono,
            fontSize: 34,
            lineHeight: 1.15,
            fontWeight: 700,
            color: theme.textPrimary,
            background: paper ? "#FFFFFF" : "rgba(56,189,248,0.06)",
            border: `1px solid ${paper ? theme.ink : theme.ink}`,
            borderRadius: paper ? 3 : 8,
            padding: "14px 16px",
            wordBreak: "break-word",
          }}
        >
          {hud.core_formula_or_law || "—"}
        </div>
        <div
          style={{
            marginTop: 14,
            fontFamily: theme.fontHeading,
            fontSize: 20,
            fontWeight: 600,
            color: theme.accentSecondary,
          }}
        >
          {hud.real_world_scale}
        </div>
      </div>

      {/* Panel 2 — Live simulation parameter watches */}
      <div style={{ ...panelStyle, flex: 1, overflow: "hidden" }}>
        <div style={labelMono}>Live Simulation</div>
        <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 10 }}>
          {hud.state_watches.map((w, i) => {
            // When a watch changed this scene, flash a highlight that fades as
            // the scene settles (spring 0->1, flash = 1->0).
            const s = spring({
              frame: localFrame,
              fps,
              config: { damping: 14, stiffness: 110 },
            });
            const flash = w.changed ? 1 - s : 0;
            const accent = theme.accentPrimary;
            return (
              <div
                key={`${w.label}-${i}`}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: paper ? 3 : 8,
                  border: `1px solid ${
                    w.changed ? accent : paper ? "#DAD4C7" : "#1C2840"
                  }`,
                  background: w.changed
                    ? `${accent}${paper ? "22" : "26"}`
                    : paper
                      ? "#FFFFFF"
                      : "rgba(255,255,255,0.02)",
                  boxShadow: flash > 0 ? `0 0 ${18 * flash}px ${accent}` : "none",
                  transform: `scale(${1 + 0.03 * flash})`,
                }}
              >
                <span
                  style={{
                    fontFamily: theme.fontHeading,
                    fontSize: 18,
                    fontWeight: 600,
                    color: theme.textMuted,
                  }}
                >
                  {w.label}
                </span>
                <span
                  style={{
                    fontFamily: theme.fontMono,
                    fontSize: 20,
                    fontWeight: 700,
                    color: w.changed ? accent : theme.textPrimary,
                    textAlign: "right",
                  }}
                >
                  {w.value}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Panel 3 — Governing rule callout */}
      <div
        style={{
          ...panelStyle,
          borderLeft: `6px solid ${theme.accentPrimary}`,
        }}
      >
        <div style={{ ...labelMono, color: theme.accentPrimary }}>Governing Rule</div>
        <div
          style={{
            marginTop: 12,
            fontFamily: theme.fontHeading,
            fontSize: 21,
            lineHeight: 1.4,
            fontWeight: 600,
            color: theme.textPrimary,
          }}
        >
          {hud.governing_rule}
        </div>
      </div>
    </div>
  );
};
