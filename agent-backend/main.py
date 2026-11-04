"""Master end-to-end orchestrator for the First Principles study-video agent.

Stages:
    1. Topic selection                curriculum_manager.pick_topic
    2. Factual reference gathering     reference_gatherer.gather (Jina/Wikipedia)
    3. Structured script generation    script_generator.generate_script (Gemini)
    4. Voiceover + word alignment      audio_engine
    5. Thumbnail render                thumbnail_generator
    6. Programmatic video compile      Remotion CLI (StudyMasterVideo)
    7. Telegram HITL approval gate     telegram_gate
    8. YouTube upload + community      youtube_publisher

Flags:
    --topic "..."     targeted topic (classified into the closest track)
    --dry-run         do everything but skip the YouTube upload
    --skip-video      skip the Remotion render (fast backend-only iteration)
    --skip-approval   skip the Telegram approval gate entirely (local testing:
                      ALWAYS pair with --dry-run so nothing is ever published)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import config  # type: ignore  # noqa: E402
import db  # type: ignore  # noqa: E402
import curriculum_manager  # type: ignore  # noqa: E402
import reference_gatherer  # type: ignore  # noqa: E402
import script_generator  # type: ignore  # noqa: E402
import audio_engine  # type: ignore  # noqa: E402
import thumbnail_generator  # type: ignore  # noqa: E402
import telegram_gate  # type: ignore  # noqa: E402
import youtube_publisher  # type: ignore  # noqa: E402


def _banner(stage: str) -> None:
    print("\n" + "=" * 68)
    print(f"  {stage}")
    print("=" * 68)


def build_payload(topic):
    _banner("STAGE 1-3: Reference gathering & structured script generation")
    reference = reference_gatherer.gather(topic)
    print(f"[main] Reference: method={reference.method} chars={len(reference.markdown)}")
    payload = script_generator.generate_script(
        topic_title=topic.title,
        source_url=topic.source_url,
        reference_markdown=reference.markdown,
        track_category=topic.track,
    )
    print(
        f"[main] Script: track={payload.track_category} theme={payload.theme_id} "
        f"scenes={len(payload.scenes)}"
    )
    script_generator.save_payload(payload)
    return payload


def build_audio(payload):
    _banner("STAGE 4: Voiceover synthesis & word-level alignment")
    audio_engine.build_audio(payload, save=True)
    return payload


def build_thumbnail(payload):
    _banner("STAGE 5: Thumbnail rendering")
    try:
        thumbnail_generator.render_thumbnail(payload)
    except Exception as exc:  # noqa: BLE001
        print(f"[main] Thumbnail render failed (continuing): {exc}")


def render_video(payload) -> bool:
    _banner("STAGE 6: Programmatic video compilation (Remotion)")
    config.VIDEO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if config.NARRATION_PATH.exists():
        shutil.copy(config.NARRATION_PATH, config.VIDEO_ASSETS_DIR / "narration.wav")
    shutil.copy(config.RENDER_PAYLOAD_PATH, config.VIDEO_ASSETS_DIR / "render_payload.json")

    npx = shutil.which("npx") or "npx"
    cmd = [
        npx, "remotion", "render", "src/index.ts",
        config.REMOTION_COMPOSITION_ID,
        str(config.FINAL_VIDEO_PATH),
        "--codec=h264",
    ]
    print(f"[main] Running: {' '.join(cmd)} (cwd={config.VIDEO_ENGINE_DIR})")
    try:
        subprocess.run(cmd, cwd=str(config.VIDEO_ENGINE_DIR), check=True, shell=(os.name == "nt"))
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"[main] Remotion render failed: {exc}")
        return False
    ok = config.FINAL_VIDEO_PATH.exists()
    print(f"[main] Video rendered: {ok} -> {config.FINAL_VIDEO_PATH}")
    return ok


def approve_and_publish(payload, dry_run: bool, skip_approval: bool) -> None:
    if skip_approval:
        _banner("STAGE 7: Approval gate SKIPPED (--skip-approval)")
        print("[main] Telegram gate bypassed for local testing.")
        if dry_run:
            print("[main] --dry-run: not publishing. Recording topic as seen.")
            db.mark_topic_published(payload.source_url, payload.youtube_title, None)
            return
    else:
        _banner("STAGE 7: Telegram human-in-the-loop approval")
        decision = telegram_gate.request_approval(payload)
        if not decision.approved:
            print(f"[main] Not publishing ({decision.reason}).")
            if decision.reject_permanently:
                db.mark_topic_published(payload.source_url, payload.youtube_title, None)
            else:
                print("[main] Topic left unseen; it can resurface on a later run.")
            return

    _banner("STAGE 8: YouTube upload & community seeding")
    if dry_run:
        print("[main] --dry-run: skipping upload. Recording topic as seen.")
        db.mark_topic_published(payload.source_url, payload.youtube_title, None)
        return
    youtube_publisher.publish(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="First Principles study-video agent")
    parser.add_argument("--topic", default=None, help="Targeted topic prompt")
    parser.add_argument("--dry-run", action="store_true", help="Skip YouTube upload")
    parser.add_argument("--skip-video", action="store_true", help="Skip the Remotion render")
    parser.add_argument(
        "--skip-approval",
        action="store_true",
        help="Skip the Telegram gate (pair with --dry-run for safe local tests)",
    )
    args = parser.parse_args()

    mode = "TARGETED" if args.topic else "CURRICULUM ROTATION"
    print(f"[main] Mode: {mode}  dry_run={args.dry_run}  skip_approval={args.skip_approval}")
    db.init_db()

    topic = curriculum_manager.pick_topic(args.topic)
    print(f"[main] TOPIC: {topic.title}\n        track={topic.track}  {topic.source_url}")
    payload = build_payload(topic)
    build_audio(payload)
    build_thumbnail(payload)

    if not args.skip_video:
        render_video(payload)
    else:
        print("[main] --skip-video: not rendering the MP4.")

    approve_and_publish(payload, dry_run=args.dry_run, skip_approval=args.skip_approval)
    _banner("DONE")


if __name__ == "__main__":
    main()
