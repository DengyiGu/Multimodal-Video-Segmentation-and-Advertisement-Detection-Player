"""Analyze one video with visual, audio, speech, and fusion passes.

Run from the repository root with ``python -m scripts.run_pipeline --help``.
Outputs are written to ``data/output`` for the desktop player.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def _print_step(idx: int, total: int, msg: str) -> None:
    print(f"\n[{idx}/{total}] {msg}", flush=True)


def _run_visual(video: Path, bundle_out: Path, sample_fps: float, window_sec: float) -> None:
    from visual.analyze import (
        analyze_visual,
        build_analysis_bundle,
        write_analysis_bundle_json,
    )

    track = analyze_visual(video, sample_fps=sample_fps, window_sec=window_sec)
    bundle = build_analysis_bundle(video, track=track)
    write_analysis_bundle_json(bundle, bundle_out)
    print(f"     Wrote bundle -> {bundle_out}")


def _run_audio(
    video: Path,
    bundle_path: Path,
    *,
    window_sec: float,
    with_speech: bool,
    model_name: str,
    vad: bool,
    language: str,
) -> None:
    from audio.analyze import analyze_audio
    from schemas.modality import AnalysisBundle

    bundle = AnalysisBundle.model_validate_json(bundle_path.read_text(encoding="utf-8"))
    windows, _duration = analyze_audio(video_path=video, window_sec=window_sec)
    bundle.audio_windows = list(windows)
    print(f"     Audio: {len(windows)} windows")

    if with_speech:
        from Automatic_speech_recognition.segment_text_analyzer import build_speech_spans

        bundle.speech_spans = build_speech_spans(
            video,
            model_name=model_name,
            language=language,
            vad=vad,
        )
        print(f"     Speech: {len(bundle.speech_spans)} spans")
    else:
        print("     Speech: skipped")

    bundle_path.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
    print(f"     Updated bundle -> {bundle_path}")


def _run_fusion(bundle_path: Path, segments_out: Path, min_segment_sec: float) -> None:
    from fusion.fuse import fuse_bundle_to_segments, load_bundle, write_segments_json

    bundle = load_bundle(bundle_path)
    segments = fuse_bundle_to_segments(bundle, min_segment_seconds=min_segment_sec)
    write_segments_json(segments, segments_out)
    print(f"     Wrote {len(segments)} segments -> {segments_out}")
    if segments:
        for seg in segments:
            dur = seg["end"] - seg["start"]
            print(
                f"       {seg['start']:>8.1f}s - {seg['end']:>8.1f}s "
                f"({dur:>6.1f}s)  {seg['label']}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.run_pipeline",
        description="Run visual + audio + speech + fusion end-to-end on a video.",
    )
    parser.add_argument("video", type=Path, help="Input video file (.mp4 / .mov / ...).")
    parser.add_argument("--out-dir", type=Path, default=Path("data/output"))
    parser.add_argument("--skip-speech", action="store_true")
    parser.add_argument("--skip-audio", action="store_true")
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="en")
    parser.add_argument("--vad", action="store_true")
    parser.add_argument("--sample-fps", type=float, default=1.0)
    parser.add_argument("--window-sec", type=float, default=2.0)
    parser.add_argument("--audio-window-sec", type=float, default=1.0)
    parser.add_argument("--min-segment-sec", type=float, default=20.0)
    args = parser.parse_args(argv)

    video = args.video.expanduser().resolve(strict=False)
    if not video.is_file():
        print(f"Error: video not found: {video}", file=sys.stderr)
        return 2

    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / f"{video.stem}_analysis_bundle.json"
    segments_path = out_dir / f"{video.stem}_segments.json"

    print(f"Pipeline: {video.name}")
    print(f"  Bundle  -> {bundle_path}")
    print(f"  Segments-> {segments_path}")

    total_steps = 1 + (0 if args.skip_audio else 1) + 1
    step = 0

    step += 1
    t0 = time.monotonic()
    _print_step(step, total_steps, "Visual analysis")
    _run_visual(video, bundle_path, args.sample_fps, args.window_sec)
    print(f"     Took {time.monotonic() - t0:.1f}s")

    if not args.skip_audio:
        step += 1
        t0 = time.monotonic()
        _print_step(
            step,
            total_steps,
            "Audio analysis" + ("" if args.skip_speech else " + speech"),
        )
        _run_audio(
            video,
            bundle_path,
            window_sec=args.audio_window_sec,
            with_speech=not args.skip_speech,
            model_name=args.model,
            vad=args.vad,
            language=args.language,
        )
        print(f"     Took {time.monotonic() - t0:.1f}s")

    step += 1
    t0 = time.monotonic()
    _print_step(step, total_steps, "Fusion")
    _run_fusion(bundle_path, segments_path, args.min_segment_sec)
    print(f"     Took {time.monotonic() - t0:.1f}s")

    print()
    print(f"Done. Launch the player with:")
    print(f"  python -m player.player")
    print(f"  (open '{video}' in the file dialog; segments load from {segments_path.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
