import React, { useMemo } from "react";
import { spring } from "remotion";
import type { SceneSpec, GraphNodeStatus } from "../../types/schema";
import type { Theme } from "../../styles/themes";
import { computeLayeredLayout, NODE_WIDTH, NODE_HEIGHT } from "../../utils/elkLayout";

interface Props {
  scene: SceneSpec;
  theme: Theme;
  localFrame: number;
  fps: number;
}

// Analytic cubic bezier point (matches cubicPath control points in elkLayout).
const bezier = (
  t: number,
  p0: [number, number],
  c1: [number, number],
  c2: [number, number],
  p3: [number, number],
): [number, number] => {
  const u = 1 - t;
  return [
    u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p3[0],
    u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p3[1],
  ];
};

const PACKET_OFFSETS = [0, 0.25, 0.5, 0.75];

// elkjs auto-layout graph (payoff trees, road networks, clearing hops, B+ trees)
// with animated SVG packets and camera-focus emphasis. (requirement 5.2.2)
export const SystemAndFlowGraph: React.FC<Props> = ({ scene, theme, localFrame, fps }) => {
  const layout = useMemo(
    () => computeLayeredLayout(scene.nodes, scene.edges),
    [scene.nodes, scene.edges],
  );

  const focus = scene.camera_focus_node_id ? layout.byId[scene.camera_focus_node_id] : null;
  const adjacent = useMemo(() => {
    const set = new Set<string>();
    if (focus) {
      set.add(focus.id);
      scene.edges.forEach((e) => {
        if (e.source === focus.id) set.add(e.target);
        if (e.target === focus.id) set.add(e.source);
      });
    }
    return set;
  }, [focus, scene.edges]);

  const statusColor = (s: GraphNodeStatus) => theme.nodeStatusColors[s];
  const M = 48;
  const vb = { x: -M, y: -M, w: layout.width + M * 2, h: layout.height + M * 2 };
  const pulse = 0.5 + 0.5 * Math.sin(localFrame * 0.12);

  return (
    <div style={{ width: "100%", height: "100%", padding: 6 }}>
      <svg
        width="100%"
        height="100%"
        viewBox={`${vb.x} ${vb.y} ${vb.w} ${vb.h}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Edges: dim track + bright line + glowing packet stream */}
        {layout.edges.map((e) => {
          const dx = Math.max(40, (e.tx - e.sx) * 0.5);
          const c1: [number, number] = [e.sx + dx, e.sy];
          const c2: [number, number] = [e.tx - dx, e.ty];
          const color = theme.packetColors[e.packet_color] ?? theme.accentPrimary;
          const dim = focus && !(adjacent.has(e.source) && adjacent.has(e.target));
          const mid = bezier(0.5, [e.sx, e.sy], c1, c2, [e.tx, e.ty]);
          return (
            <g key={e.id} style={{ opacity: dim ? 0.2 : 1 }}>
              <path d={e.path} fill="none" stroke={color} strokeWidth={6} strokeOpacity={0.16} strokeLinecap="round" />
              <path d={e.path} fill="none" stroke={color} strokeWidth={2} strokeOpacity={0.55} strokeLinecap="round" />
              {e.animate_packets &&
                PACKET_OFFSETS.map((off) => {
                  const t = (((localFrame * 0.0095 + off) % 1) + 1) % 1;
                  const [px, py] = bezier(t, [e.sx, e.sy], c1, c2, [e.tx, e.ty]);
                  const edgeFade = Math.min(1, Math.min(t, 1 - t) * 8);
                  return (
                    <g key={off} style={{ opacity: edgeFade }}>
                      <circle cx={px} cy={py} r={10} fill={color} opacity={0.2} />
                      <circle cx={px} cy={py} r={4.5} fill={color} />
                    </g>
                  );
                })}
              {/* Edge label */}
              {e.label ? (
                <g>
                  <rect
                    x={mid[0] - e.label.length * 4.6 - 8}
                    y={mid[1] - 15}
                    width={e.label.length * 9.2 + 16}
                    height={26}
                    rx={6}
                    fill={theme.panelBg}
                    stroke={color}
                    strokeWidth={1}
                  />
                  <text
                    x={mid[0]}
                    y={mid[1] + 3}
                    textAnchor="middle"
                    fontFamily={theme.fontMono}
                    fontSize={15}
                    fontWeight={700}
                    fill={color}
                  >
                    {e.label}
                  </text>
                </g>
              ) : null}
            </g>
          );
        })}

        {/* Nodes */}
        {layout.nodes.map((n, i) => {
          const enter = spring({ frame: localFrame - i * 5, fps, config: { damping: 16, stiffness: 150 } });
          const dim = focus && !adjacent.has(n.id);
          const isFocus = !!focus && n.id === focus.id;
          const color = statusColor(n.status);
          const accented = n.status !== "neutral";
          const eliminated = n.status === "eliminated";
          const s = (0.92 + enter * 0.08) * (isFocus ? 1.04 : 1);
          const rise = (1 - enter) * 20;
          const labelStr = n.label.slice(0, 18);
          const subStr = n.sublabel.slice(0, 26);
          return (
            <g
              key={n.id}
              transform={`translate(${n.x}, ${n.y - rise})`}
              style={{ opacity: (dim ? 0.3 : eliminated ? 0.55 : 1) * Math.min(1, enter * 1.2) }}
            >
              <g transform={`translate(${NODE_WIDTH / 2}, ${NODE_HEIGHT / 2}) scale(${s}) translate(${-NODE_WIDTH / 2}, ${-NODE_HEIGHT / 2})`}>
                {isFocus ? (
                  <rect x={-9} y={-9} width={NODE_WIDTH + 18} height={NODE_HEIGHT + 18} rx={16} fill="none" stroke={theme.accentPrimary} strokeWidth={3} strokeOpacity={0.5 + 0.4 * pulse} />
                ) : null}
                {accented ? (
                  <rect x={-5} y={-5} width={NODE_WIDTH + 10} height={NODE_HEIGHT + 10} rx={14} fill="none" stroke={color} strokeWidth={10} strokeOpacity={0.14} />
                ) : null}
                {theme.mode === "light" ? (
                  <rect x={5} y={7} width={NODE_WIDTH} height={NODE_HEIGHT} rx={10} fill={theme.ink} opacity={0.9} />
                ) : (
                  <rect x={0} y={8} width={NODE_WIDTH} height={NODE_HEIGHT} rx={12} fill="#000000" opacity={0.38} />
                )}
                <rect
                  width={NODE_WIDTH}
                  height={NODE_HEIGHT}
                  rx={theme.mode === "light" ? 8 : 12}
                  fill={theme.panelBg}
                  stroke={accented ? color : theme.ink}
                  strokeWidth={accented ? 2.5 : theme.mode === "light" ? 2 : 1.5}
                />
                {/* status dot */}
                <circle cx={22} cy={NODE_HEIGHT / 2} r={8} fill={color} />
                <text x={42} y={NODE_HEIGHT / 2 - 6} fontFamily={theme.fontHeading} fontSize={21} fontWeight={800} fill={theme.textPrimary}>
                  {labelStr}
                </text>
                <text x={42} y={NODE_HEIGHT / 2 + 20} fontFamily={theme.fontMono} fontSize={15} fill={theme.textMuted}>
                  {subStr}
                </text>
              </g>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
