import React from "react";
import {
  AbsoluteFill,
  Audio,
  staticFile,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { SceneSpec, VideoRenderPayload } from "./types/schema";
import { getTheme, gridBackground } from "./styles/themes";
import { ZoneAStage } from "./components/ZoneAStage";
import { ZoneBConceptHUD } from "./components/ZoneBConceptHUD";

export type MasterProps = {
  payload: VideoRenderPayload;
};

// On-screen channel brand (keep in sync with agent-backend config CHANNEL_NAME).
const CHANNEL_NAME = "First Principles";

interface ActiveScene {
  scene: SceneSpec;
  index: number;
  localFrame: number;
}

const useActiveScene = (payload: VideoRenderPayload, fps: number, frame: number): ActiveScene => {
  const timeSec = frame / fps;
  let index = 0;
  for (let i = 0; i < payload.scenes.length; i += 1) {
    if (timeSec >= payload.scenes[i].start_sec) index = i;
  }
  const scene = payload.scenes[index];
  const sceneStartFrame = Math.round(scene.start_sec * fps);
  return { scene, index, localFrame: frame - sceneStartFrame };
};

export const MasterComposition: React.FC<MasterProps> = ({ payload }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = getTheme(payload.theme_id);
  const paper = theme.mode === "light";
  const active = useActiveScene(payload, fps, frame);
  // Only mount Audio when real narration exists (the live pipeline fills
  // `words`); the bundled mock has none, so it must not try to fetch the wav.
  const hasAudio = payload.words.length > 0;

  // Per-scene header kicker + stage enter transition.
  const kicker = spring({ frame: active.localFrame, fps, config: { damping: 18, stiffness: 120 } });
  const enter = interpolate(active.localFrame, [0, 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const stageY = interpolate(enter, [0, 1], [24, 0]);

  // Slow grid drift so the canvas is never static.
  const gx = (frame * 0.2) % 100;
  const gy = (frame * 0.1) % 100;
  const progress = durationInFrames > 1 ? frame / (durationInFrames - 1) : 0;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.canvasBg,
        fontFamily: theme.fontHeading,
        color: theme.textPrimary,
        overflow: "hidden",
      }}
    >
      {hasAudio ? <Audio src={staticFile("assets/narration.wav")} /> : null}

      {/* Drifting grid layer */}
      <AbsoluteFill
        style={{
          ...gridBackground(theme),
          backgroundColor: "transparent",
          backgroundPosition: `${gx}px ${gy}px`,
          opacity: paper ? 0.9 : 0.8,
          pointerEvents: "none",
        }}
      />

      {/* Soft accent glow (dark theme only — paper stays flat/archival) */}
      {!paper ? (
        <AbsoluteFill style={{ pointerEvents: "none" }}>
          <div
            style={{
              position: "absolute",
              left: "30%",
              top: "28%",
              width: 820,
              height: 820,
              transform: "translate(-50%, -50%)",
              background: `radial-gradient(circle, ${theme.accentPrimary}12 0%, transparent 62%)`,
            }}
          />
        </AbsoluteFill>
      ) : null}

      {/* Header: wordmark + per-scene chapter title */}
      <div
        style={{
          position: "absolute",
          top: 48,
          left: 72,
          right: 56,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          zIndex: 5,
        }}
      >
        <div>
          <div style={{ fontFamily: theme.fontMono, fontSize: 20, letterSpacing: 7, fontWeight: 700, color: theme.accentPrimary }}>
            {CHANNEL_NAME.toUpperCase()}
          </div>
          <div
            style={{
              marginTop: 14,
              fontFamily: theme.fontHeading,
              fontSize: 44,
              fontWeight: 800,
              letterSpacing: -0.5,
              color: theme.textPrimary,
              opacity: kicker,
              transform: `translateY(${interpolate(kicker, [0, 1], [16, 0])}px)`,
            }}
          >
            {active.scene.chapter_title}
          </div>
        </div>
        <div
          style={{
            fontFamily: theme.fontMono,
            fontSize: 18,
            fontWeight: 700,
            color: theme.textMuted,
            marginTop: 6,
          }}
        >
          {String(active.index + 1).padStart(2, "0")} / {String(payload.scenes.length).padStart(2, "0")}
        </div>
      </div>

      {/* Zone A — the stage (left ~74%) */}
      <div
        style={{
          position: "absolute",
          top: 150,
          left: 72,
          right: 540,
          bottom: 72,
          zIndex: 2,
          opacity: enter,
          transform: `translateY(${stageY}px)`,
        }}
      >
        <ZoneAStage scene={active.scene} theme={theme} localFrame={active.localFrame} fps={fps} />
      </div>

      {/* Zone B — the live concept HUD (right 26%) */}
      <ZoneBConceptHUD theme={theme} hud={active.scene.hud} localFrame={active.localFrame} fps={fps} />

      {/* Progress bar */}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 5, background: paper ? "rgba(0,0,0,0.08)" : "rgba(255,255,255,0.08)", zIndex: 6 }}>
        <div style={{ width: `${progress * 100}%`, height: "100%", background: theme.accentPrimary, boxShadow: `0 0 12px ${theme.accentPrimary}` }} />
      </div>
    </AbsoluteFill>
  );
};
