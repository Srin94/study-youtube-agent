import React, { useMemo, useState, useEffect } from "react";
import { continueRender, delayRender, interpolate } from "remotion";
import { codeToHtml } from "shiki";
import type { SceneSpec } from "../../types/schema";
import type { Theme } from "../../styles/themes";

interface Props {
  scene: SceneSpec;
  theme: Theme;
  localFrame: number;
  fps: number;
}

interface Rendered {
  before: string;
  after: string;
}

// Naive intuition vs mathematical/engineering reality, rendered with shiki +
// large clean typography. (requirement 5.2.4)
export const FormulaAndCodeProof: React.FC<Props> = ({ scene, theme, localFrame }) => {
  const proof = scene.formula_proof;
  const paper = theme.mode === "light";
  const [html, setHtml] = useState<Rendered | null>(null);
  const [handle] = useState(() => delayRender("shiki-formula"));
  const shikiTheme = theme.shikiTheme;

  // shiki has no grammar for 'math'/'text' — render those as plain escaped text.
  const codeLang = proof && !["math", "text", ""].includes(proof.language)
    ? proof.language
    : null;

  useEffect(() => {
    let cancelled = false;
    const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    const plain = (s: string) => `<pre><code>${esc(s)}</code></pre>`;
    const run = async () => {
      if (!proof) {
        setHtml({ before: "", after: "" });
        continueRender(handle);
        return;
      }
      if (!codeLang) {
        if (!cancelled) setHtml({ before: plain(proof.naive_or_before), after: plain(proof.optimal_or_after) });
        continueRender(handle);
        return;
      }
      try {
        const opts = { lang: codeLang, theme: shikiTheme } as const;
        const [before, after] = await Promise.all([
          codeToHtml(proof.naive_or_before || "", opts),
          codeToHtml(proof.optimal_or_after || "", opts),
        ]);
        if (!cancelled) setHtml({ before, after });
      } catch {
        if (!cancelled) setHtml({ before: plain(proof.naive_or_before), after: plain(proof.optimal_or_after) });
      } finally {
        continueRender(handle);
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, [proof, codeLang, shikiTheme, handle]);

  const reveal = interpolate(localFrame, [8, 44], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const longest = proof
    ? (proof.naive_or_before + "\n" + proof.optimal_or_after)
        .split("\n")
        .reduce((m, l) => Math.max(m, l.length), 1)
    : 1;
  const codeFont = Math.max(15, Math.min(26, Math.floor(620 / (longest * 0.6))));

  const panel = useMemo<React.CSSProperties>(
    () => ({
      flex: 1,
      minWidth: 0,
      background: paper ? "#FFFFFF" : "#0C1322",
      border: theme.borderStyle,
      borderRadius: paper ? 4 : 12,
      boxShadow: paper ? theme.hardShadow : theme.hardShadow,
      overflow: "hidden",
      position: "relative",
      display: "flex",
      flexDirection: "column",
    }),
    [theme, paper],
  );

  const tag: React.CSSProperties = {
    fontFamily: theme.fontMono,
    fontSize: 15,
    letterSpacing: 1.5,
    padding: "10px 16px",
    textTransform: "uppercase",
    fontWeight: 700,
    borderBottom: theme.borderStyle,
  };

  if (!proof) return null;

  return (
    <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ fontFamily: theme.fontHeading, fontSize: 30, fontWeight: 800, color: theme.textPrimary }}>
        {proof.title}
      </div>

      <style>{`
        .ffit pre, .ffit code { white-space: pre-wrap !important; overflow-wrap: anywhere;
          word-break: break-word; font-size: ${codeFont}px !important; line-height: 1.55 !important;
          background: transparent !important; margin: 0; font-family: ${theme.fontMono}; }
      `}</style>

      <div style={{ display: "flex", gap: 20, flex: 1, minHeight: 0, alignItems: "stretch" }}>
        <div style={panel}>
          <div style={{ ...tag, color: theme.accentCritical }}>✕ Naïve Intuition</div>
          <div className="ffit" style={{ padding: 20, flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", color: theme.textPrimary }} dangerouslySetInnerHTML={{ __html: html?.before ?? "" }} />
        </div>
        <div style={panel}>
          <div style={{ ...tag, color: theme.accentPositive }}>✓ The Real Rule</div>
          <div style={{ position: "relative", flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <div className="ffit" style={{ padding: 20, color: theme.textPrimary }} dangerouslySetInnerHTML={{ __html: html?.after ?? "" }} />
            <div style={{ position: "absolute", top: 0, left: `${reveal}%`, right: 0, bottom: 0, background: paper ? "#FFFFFF" : "#0C1322" }} />
            <div style={{ position: "absolute", top: 0, bottom: 0, left: `calc(${reveal}% - 2px)`, width: 3, background: theme.accentPositive, opacity: reveal > 0 && reveal < 100 ? 1 : 0 }} />
          </div>
        </div>
      </div>

      <div style={{ fontFamily: theme.fontHeading, fontSize: 21, fontWeight: 600, color: theme.accentSecondary, textAlign: "center" }}>
        {proof.takeaway_caption}
      </div>
    </div>
  );
};
