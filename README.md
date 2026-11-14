# Multimodal Video Segmentation and Advertisement Detection Player

A local video analyzer and desktop player that identifies advertisements, intros,
outros, and main content. Visual features, audio changes, speech transcripts,
on-screen text, and optional semantic scores are combined into a labeled
timeline for browsing and content-only playback.

## Features

- Detect advertisements and opening/closing sections with multimodal signals.
- Read speech with faster-whisper and on-screen text with optional EasyOCR.
- Add optional sentence-transformer scores for advertisements, intros, and outros.
- Reuse JSON segment files without analyzing a video again.
- Browse a colored timeline and segment list, jump between segments, and adjust
  playback speed, volume, and fullscreen controls.
- Enable **Play Content Only** to skip non-content segments.

The output is a timeline of timestamps and labels. The program does not cut or
re-encode the source video into separate files.

## Installation

Requires **Python 3.10+** and **FFmpeg**, including `ffprobe`, on PATH. Run all
commands from the repository root.

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -e ".[player,speech]"
ffmpeg -version
ffprobe -version
```

On macOS or Linux, activate with `source .venv/bin/activate`.
See [SETUP.md](SETUP.md) for FFmpeg installation and troubleshooting.

Download the selected speech model once:

```console
python -m Automatic_speech_recognition.segment_text_analyzer --download-model --model small
```

Models are stored in `Automatic_speech_recognition/models/`. The default speech
model is `small`; transcription uses CPU `int8` compute unless another device is
selected. English is the default language.

## Analyze and play

For visual, audio, and speech analysis:

```console
python -m scripts.run_pipeline data/input/example.mp4
python -m player.player
```

Use `--skip-speech` without a local speech model, or `--skip-audio` for visual-only
analysis. This runner analyzes one video at a time and does not invoke OCR or
semantic scoring. Use the fusion CLI or player for those optional passes.

In the player, choose **File > Open Video** and select the analyzed video.
The player first loads `data/output/<video_stem>_segments.json`, then checks for
the same filename beside the video. Without cached segments, it runs live
analysis in a background worker. Speech and OCR run concurrently in that path,
followed by semantic scoring and fusion. Missing optional dependencies or local
models are reported in the terminal and skipped.

The player preserves the existing default of CUDA for OCR and semantic models.
To run those passes on CPU instead, set the environment variable before launch:

```powershell
$env:CS576_TEXT_MODEL_DEVICE = "cpu"
python -m player.player
```

This setting controls OCR and semantic inference; the player's speech pass uses
CPU `int8` with voice activity detection enabled.

## Optional OCR and semantic scoring

Install the optional dependencies:

```console
python -m pip install -e ".[ocr,semantic]"
```

Prepare local models once while online:

```console
python -c "import easyocr; easyocr.Reader(['en'], gpu=False, model_storage_directory='ocr/models', download_enabled=True)"
python -m semantic.analyze --download-model --model mini
```

OCR models remain in `ocr/models/`; semantic models remain in `semantic/models/`.
The semantic choices are `mini` (all-MiniLM-L6-v2) and `mpnet`
(all-mpnet-base-v2); automatic integration uses `mini`. Analysis expects local
models and does not download them automatically.

Run the integrated CLI with CPU inference:

```console
python -m fusion --video data/input/example.mp4 --sample-fps 1 --window-sec 2 --asr-device cpu --out data/output/example_segments.json --bundle-out data/output/example_analysis_bundle.json
```

The fusion CLI uses CPU for OCR and semantic scoring by default. Its optional
`--cuda-text-models` switch enables CUDA for those passes; ASR has separate
`--asr-device` and `--asr-compute-type` options. The player environment variable
and CLI flags apply to their respective entry points.

## Runner options

```console
python -m scripts.run_pipeline --help
```

| Option | Purpose |
| --- | --- |
| `--out-dir DIR` | Output directory; default: `data/output`. |
| `--skip-speech` | Skip speech transcription. |
| `--skip-audio` | Skip audio analysis and speech transcription. |
| `--model NAME` | Speech model: `tiny`, `base`, `small`, `medium`, or `large-v3`. |
| `--language CODE` | Transcription language; default: `en`. |
| `--vad` | Enable speech voice activity detection in the runner; off by default there. |
| `--sample-fps N` | Visual sample rate; default: `1.0`. |
| `--window-sec N` | Visual window length; default: `2.0` seconds. |
| `--audio-window-sec N` | Audio window length; default: `1.0` second. |

`--min-segment-sec` is accepted for compatibility but unused by the current
fusion engine. Its internal detection constraints still apply.

For a custom output directory, copy `<video_stem>_segments.json` beside the
video so the player can find it. Videos with the same stem share an output
filename; use separate output directories for them.

## Output

For `example.mp4`, the runner writes:

- `data/output/example_analysis_bundle.json`: visual windows, audio features,
  and speech spans when enabled. The fusion CLI can also include OCR and semantic
  spans in its bundle output.
- `data/output/example_segments.json`: the labeled intervals used by the player.

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

The bundled example illustrates the schema and can be fused without a video or
speech model; it is not a detection benchmark:

```console
python -m fusion --bundle sample_data/sample_analysis_bundle.json --skip-speech --out data/output/sample_segments.json
```

## Project layout

| Path | Role |
| --- | --- |
| `scripts/run_pipeline.py` | Single-video visual/audio/speech runner. |
| `visual/`, `visual_analyze/` | Visual feature extraction and CLI. |
| `audio/`, `audio_analyze/` | Audio feature extraction and CLI. |
| `Automatic_speech_recognition/` | Local speech model download and transcription. |
| `ocr/` | On-screen text extraction from sampled frames. |
| `semantic/` | Semantic advertisement and video-structure scores. |
| `fusion/` | Advertisement fusion, intro/outro detectors, and text dictionaries. |
| `schemas/` | Shared analysis and dataset metadata models. |
| `player/`, `player_fusion.py` | Desktop player, cache loading, and live analysis. |
| `sample_data/`, `video_info/` | Small schema and stitched-video metadata examples. |

Module details: [fusion](fusion/README.md), [player](player/README.md),
[speech recognition](Automatic_speech_recognition/SETUP.md), and
[dataset metadata](video_info/README.md).

## Detection limits and data

Detection combines heuristic boundaries and text evidence, with assumptions about
advertisement duration and video structure. Short advertisements, unusual video
styles, or missing text evidence may produce inaccurate labels or boundaries.
The engine emits Core Content, Intro, Outro, and Advertisement; the player accepts
additional labels from custom JSON files. Review the timeline before relying on
content-only playback. If live analysis fails, the player attempts to use one
full-length content segment.

Source videos, downloaded models, and generated outputs are excluded from Git.
No video dataset is included. The optional extended brand dictionary retains its
Simple Icons source and CC0 attribution in `fusion/extra_brand_names.txt`;
brand names and trademarks belong to their respective owners. It is enabled by
default in the current code; set `FUSION_USE_EXTRA_BRANDS=0` to disable it.
