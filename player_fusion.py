"""Load cached segments or analyze a video for the desktop player.

If analysis fails, preserve playback with a single full-length content segment.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


from player.segments import (
    Segment,
    build_full_content_segment,
    build_segment_from_payload,
    probe_video_duration_seconds,
)


# Candidate locations for a pre-computed segments file

def _find_segments_file(video_path: Path) -> Path | None:
    stem = video_path.stem
    candidates = [
        Path("data/output") / f"{stem}_segments.json",
        video_path.parent / f"{stem}_segments.json",
        Path("data/output") / f"{stem.replace('_visual_track', '')}_segments.json",
    ]
    for c in candidates:
        try:
            if c.is_file():
                return c.resolve()
        except OSError:
            continue
    return None


# Convert cached or freshly computed intervals to player segments

def _build_player_segments(payloads: list[dict[str, Any]]) -> list[Segment]:
    segments = []
    for index, payload in enumerate(payloads):
        segment = build_segment_from_payload(payload, index)
        if segment is not None:
            segments.append(segment)
    return segments


def _load_segments_from_json(path: Path) -> list[Segment]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return _build_player_segments(data.get("segments", []))


# Run visual, audio, and optional speech analysis before fusion

def _run_fusion_live(video_path: Path) -> list[Segment]:
    from visual.analyze import build_analysis_bundle
    from fusion.fuse import fuse_bundle_to_segments

    print(f"[fusion] Running visual analysis on {video_path.name} …", file=sys.stderr)
    bundle = build_analysis_bundle(video_path)

    # Wire in audio analysis
    try:
        from audio.analyze import analyze_audio
        print(f"[fusion] Running audio analysis on {video_path.name} …", file=sys.stderr)
        audio_windows, _ = analyze_audio(video_path=video_path)
        bundle.audio_windows = audio_windows
        print(f"[fusion] Got {len(audio_windows)} audio windows.", file=sys.stderr)
    except Exception as e:
        print(f"[fusion] Audio analysis unavailable, skipping: {e}", file=sys.stderr)

    # Wire in speech recognition if the module is available
    try:
        from Automatic_speech_recognition.segment_text_analyzer import build_speech_spans
        print(f"[fusion] Running speech recognition on {video_path.name} …", file=sys.stderr)
        bundle.speech_spans = build_speech_spans(video_path)
        print(f"[fusion] Got {len(bundle.speech_spans)} speech spans.", file=sys.stderr)
    except Exception as e:
        print(f"[fusion] Speech recognition unavailable, skipping: {e}", file=sys.stderr)

    print(f"[fusion] Fusing {len(bundle.visual.windows)} windows …", file=sys.stderr)
    raw_segments = fuse_bundle_to_segments(bundle)

    # Persist for next time
    out_dir = Path("data/output")
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{video_path.stem}_segments.json"
        from fusion.fuse import write_segments_json
        write_segments_json(raw_segments, out_path)
        print(f"[fusion] Saved segments → {out_path}", file=sys.stderr)
    except Exception as e:
        print(f"[fusion] Warning: could not save segments.json: {e}", file=sys.stderr)

    return _build_player_segments(raw_segments)


# Player entry point

def run_video_segmentation(video_path: Path) -> list[Segment]:
    """Prefer cached segments, then live analysis, then full-content playback."""
    # 1. Pre-computed file
    segments_file = _find_segments_file(video_path)
    if segments_file is not None:
        try:
            segments = _load_segments_from_json(segments_file)
            if segments:
                print(
                    f"[fusion] Loaded {len(segments)} segments from {segments_file.name}",
                    file=sys.stderr,
                )
                return segments
        except Exception as e:
            print(f"[fusion] Warning: could not load {segments_file}: {e}", file=sys.stderr)

    # 2. Live fusion
    try:
        return _run_fusion_live(video_path)
    except Exception as e:
        print(f"[fusion] Live fusion failed: {e}", file=sys.stderr)

    # 3. Preserve playback if analysis is unavailable
    print("[fusion] Falling back to a full-length content segment.", file=sys.stderr)
    duration = probe_video_duration_seconds(video_path)
    return build_full_content_segment(duration)
