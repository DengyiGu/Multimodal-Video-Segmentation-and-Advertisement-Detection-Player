# Multimodal Video Segmentation and Advertisement Detection Player

A local video analyzer and desktop player that identifies advertisements, intros,
outros, and main content. Visual features, audio changes, and speech transcripts
are combined into a labeled timeline, so you can inspect segment boundaries and
watch the main content with non-content sections skipped.

## Features

- Analyze a single video or a folder of videos.
- Combine visual appearance, scene changes, audio features, and optional local
  speech recognition with faster-whisper.
- Save analysis features and segment timestamps as JSON for reuse.
- Browse segments in a colored timeline and segment list.
- Jump between segments, adjust playback speed and volume, and use fullscreen.
- Enable **Play Content Only** to skip advertisements, intros, and outros.

The pipeline produces timestamps and labels. It does not cut or re-encode the
source video into separate files.

## Quick start

Requires **Python 3.10+** and **FFmpeg**, including `ffprobe`, on your PATH.
Run the commands below from the repository root.

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -e ".[player]"
ffmpeg -version
ffprobe -version
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`.
See [SETUP.md](SETUP.md) for installation details and troubleshooting.

Place a video in `data/input/`, then analyze it without speech recognition:

```console
python -m scripts.run_pipeline data/input/example.mp4 --skip-speech
python -m player.player
```

In the player, choose **File > Open Video** and select the same video. The player
loads `data/output/example_segments.json` automatically. Select **Play Content
Only** to skip non-content segments, or double-click a segment to seek to it.

### Enable speech recognition

```console
python -m pip install -e ".[speech]"
python -m Automatic_speech_recognition.segment_text_analyzer --download-model --model small
python -m scripts.run_pipeline data/input/example.mp4
```

The selected model is downloaded once to
`Automatic_speech_recognition/models/faster-whisper-small/`. Transcription then
runs locally on the CPU with `int8` compute. No GPU is required. The default
language is English; use `--language zh` for Chinese, for example.

## Pipeline options

```console
python -m scripts.run_pipeline --help
python -m scripts.run_pipeline --input-dir data/input --skip-speech
python -m scripts.run_pipeline data/input/example.mp4 --skip-audio
```

| Option | Purpose |
| --- | --- |
| `--input-dir DIR` | Analyze `.mp4`, `.mov`, `.mkv`, and `.avi` files directly in a folder. |
| `--out-dir DIR` | Save outputs to a different directory; default: `data/output`. |
| `--skip-speech` | Use visual and audio features without transcription. |
| `--skip-audio` | Use visual features only; also skips speech. |
| `--skip-analysis` | Reuse the existing visual bundle in the output directory. Audio and speech still run unless skipped. |
| `--model NAME` | Speech model: `tiny`, `base`, `small`, `medium`, or `large-v3`. |
| `--language CODE` | Transcription language; default: `en`. |
| `--vad` | Enable voice activity detection for transcription. |
| `--sample-fps N` | Visual sampling rate; default: `1.0`. |
| `--window-sec N` | Visual window duration; default: `2.0` seconds. |
| `--audio-window-sec N` | Audio window duration; default: `1.0` second. |

`--min-segment-sec` remains accepted for compatibility, but the current fusion
engine does not use this value. Its internal detection constraints still apply.

For custom output directories, copy `<video_stem>_segments.json` beside the video
so the player can find it. Videos with the same stem share an output filename;
use separate output directories for them.

## Output

For `example.mp4`, the pipeline writes:

- `data/output/example_analysis_bundle.json`: visual windows, audio features,
  and speech spans when enabled.
- `data/output/example_segments.json`: labeled intervals consumed by the player.

Example segment file (timestamps in seconds):

```json
{
  "schema_version": "1.0",
  "source": "fusion",
  "segments": [
    {"start": 0.0, "end": 10.0, "label": "Intro", "kind": "non-content"},
    {"start": 10.0, "end": 120.0, "label": "Core Content", "kind": "content"},
    {"start": 120.0, "end": 150.0, "label": "Advertisement", "kind": "non-content"},
    {"start": 150.0, "end": 180.0, "label": "Outro", "kind": "non-content"}
  ]
}
```

You can run fusion on the bundled example without a video or speech model:

```console
python -m fusion --bundle sample_data/sample_analysis_bundle.json --skip-speech --out data/output/sample_segments.json
```

## Project layout

| Path | Role |
| --- | --- |
| `scripts/run_pipeline.py` | Single-video and batch pipeline runner. |
| `visual/`, `visual_analyze/` | Visual feature extraction and CLI. |
| `audio/`, `audio_analyze/` | Audio feature extraction and CLI. |
| `Automatic_speech_recognition/` | Local model download and transcription. |
| `fusion/` | Detection rules, boundary selection, and segment JSON output. |
| `schemas/` | Shared analysis and dataset metadata models. |
| `player/` | PySide6 player, timeline, and playback controls. |
| `player_fusion.py` | Cached segment loading and live analysis for the player. |
| `sample_data/` | Small analysis bundle example. |
| `video_info/` | Optional stitched-video metadata example. |

Module details: [fusion](fusion/README.md), [player](player/README.md),
[speech recognition](Automatic_speech_recognition/SETUP.md), and
[dataset metadata](video_info/README.md).

## Detection limits

Detection uses heuristics tuned for vlog-style videos, including assumptions
about advertisement duration and spacing. Short ads, closely spaced ads, and
other video styles may be missed or receive inaccurate boundaries. The current
fusion engine emits **Core Content**, **Intro**, **Outro**, and **Advertisement**;
the player also accepts additional labels supplied in custom segment files.
Intro and outro labeling currently runs when ad intervals are found; otherwise
fusion returns a single content segment. Review the timeline before relying on
content-only playback.

If no cached segments exist, opening a video in the player starts live analysis
in a background worker. Missing audio or speech dependencies are skipped there.
If analysis fails, the player attempts to treat the entire video as content;
check the terminal messages when expected labels are missing.

Source videos, downloaded models, and generated analysis files are kept local
and excluded from Git. No video dataset is included.
