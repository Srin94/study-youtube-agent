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

// Physical/logical layers with an animated signal wave passing vertically
// through the stack (noise-canceling, EUV, OSI/TCP, OLED/E-Ink). (req 5.2.3)
export const LayeredHardwareStack: React.FC<Props> = ({ scene, theme, localFrame, fps }) => {
  const layers = scene.stack_layers;
  const paper = theme.mode === "light";
  if (!layers || layers.length === 0) return null;

  const count = layers.length;
  // A signal travels top -> bottom on a ~2.4s cycle; the fractional position
  // picks which layer is "hot" right now.
  const cycleFrames = fps * 2.4;
  const travel = (localFrame % cycleFrames) / cycleFrames; // 0..1
  const hotIndex = Math.min(count - 1, Math.floor(travel * count));

  return (
    <div style={{ width: "100%", height: "100%", display: "flex", gap: 22 }}>
      {/* Left signal spine */}
      <div style={{ position: "relative", width: 70, flexShrink: 0 }}>
        <svg width="70" height="100%" viewBox="0 0 70 1000" preserveAspectRatio="none">
          <line x1={35} y1={0} x2={35} y2={1000} stroke={paper ? theme.ink : "#223049"} strokeWidth={2} />
          {/* Traveling pulse */}
          {(() => {
            const y = travel * 1000;
            return (
              <g>
                <circle cx={35} cy={y} r={22} fill={theme.accentPrimary} opacity={0.18} />
                <circle cx={35} cy={y} r={9} fill={theme.accentPrimary} />
              </g>
            );
          })()}
          {/* Static sine hint */}
          <path
            d={Array.from({ length: 50 }, (_, k) => {
              const yy = (k / 49) * 1000;
              const xx = 35 + 18 * Math.sin(k * 0.6 + localFrame * 0.1);
              return `${k === 0 ? "M" : "L"} ${xx} ${yy}`;
            }).join(" ")}
            fill="none"
            stroke={theme.accentSecondary}
            strokeWidth={2}
            opacity={0.35}
          />
        </svg>
      </div>

      {/* Layer stack */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 14, justifyContent: "center" }}>
        {layers.map((layer, i) => {
          const enter = spring({ frame: localFrame - i * 4, fps, config: { damping: 16, stiffness: 150 } });
          const color = theme.stackStatusColors[layer.status];
          const hot = i === hotIndex;
          const glow = hot ? 1 : 0;
          return (
            <div
              key={`${layer.layer_label}-${i}`}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 18,
                padding: "16px 20px",
                background: paper ? (hot ? `${color}14` : "#FFFFFF") : hot ? `${color}1E` : "rgba(255,255,255,0.03)",
                border: `${paper ? 2 : 1.5}px solid ${hot ? color : paper ? theme.ink : "#223049"}`,
                borderLeft: `7px solid ${color}`,
                borderRadius: paper ? 4 : 12,
                boxShadow: hot
                  ? `0 0 ${24 * glow}px ${color}66` + (paper ? `, ${theme.hardShadow}` : "")
                  : paper
                    ? theme.hardShadow
                    : "none",
                opacity: Math.min(1, enter * 1.2),
                transform: `translateX(${(1 - enter) * -24}px) scale(${hot ? 1.012 : 1})`,
              }}
            >
              <div style={{ minWidth: 220, flexShrink: 0 }}>
                <div style={{ fontFamily: theme.fontMono, fontSize: 19, fontWeight: 700, color: theme.textPrimary }}>
                  {layer.layer_label}
                </div>
              </div>
              <div style={{ flex: 1, fontFamily: theme.fontHeading, fontSize: 19, color: theme.textMuted, lineHeight: 1.3 }}>
                {layer.detail_text}
              </div>
              <div
                style={{
                  flexShrink: 0,
                  fontFamily: theme.fontMono,
                  fontSize: 22,
                  fontWeight: 800,
                  color: theme.textOnAccent,
                  background: color,
                  padding: "6px 14px",
                  borderRadius: paper ? 3 : 8,
                  minWidth: 92,
                  textAlign: "center",
                }}
              >
                {layer.metric_badge}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
