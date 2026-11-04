import React from "react";
import type { SceneSpec } from "../types/schema";
import type { Theme } from "../styles/themes";
import { SequenceGridDryRun } from "./scenes/SequenceGridDryRun";
import { SystemAndFlowGraph } from "./scenes/SystemAndFlowGraph";
import { LayeredHardwareStack } from "./scenes/LayeredHardwareStack";
import { FormulaAndCodeProof } from "./scenes/FormulaAndCodeProof";
import { ComparisonMatrix } from "./scenes/ComparisonMatrix";

interface Props {
  scene: SceneSpec;
  theme: Theme;
  localFrame: number;
  fps: number;
}

// Full-bleed Zone-A renderer: dispatches to one of the five universal visual
// archetypes by `visual_type`.
export const ZoneAStage: React.FC<Props> = ({ scene, theme, localFrame, fps }) => {
  const render = () => {
    switch (scene.visual_type) {
      case "SequenceGridDryRun":
        return <SequenceGridDryRun scene={scene} theme={theme} localFrame={localFrame} fps={fps} />;
      case "SystemAndFlowGraph":
        return <SystemAndFlowGraph scene={scene} theme={theme} localFrame={localFrame} fps={fps} />;
      case "LayeredHardwareStack":
        return <LayeredHardwareStack scene={scene} theme={theme} localFrame={localFrame} fps={fps} />;
      case "FormulaAndCodeProof":
        return <FormulaAndCodeProof scene={scene} theme={theme} localFrame={localFrame} fps={fps} />;
      case "ComparisonMatrix":
        return <ComparisonMatrix scene={scene} theme={theme} localFrame={localFrame} fps={fps} />;
      default:
        return null;
    }
  };
  return <div style={{ position: "relative", width: "100%", height: "100%" }}>{render()}</div>;
};
