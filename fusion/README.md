# Fusion

The fusion module combines visual windows, audio features, and speech/OCR text
into Core Content, Intro, Outro, and Advertisement intervals. `intro_detector.py`
and `outro_detector.py` handle the opening and closing boundaries. Advertisement
rules and boundary refinement are in `fuse.py`.

## Integrated analysis

```console
python -m fusion --video data/input/example.mp4 --sample-fps 1 --window-sec 2 --asr-device cpu --out data/output/example_segments.json --bundle-out data/output/example_analysis_bundle.json
```

Audio, speech, OCR, and semantic passes are attempted before fusion. Missing
optional dependencies or local models are reported and skipped. Speech uses CPU
`int8` and VAD by default. `--no-asr-vad` disables VAD. OCR and semantic inference
use CPU unless `--cuda-text-models` is selected. `--skip-speech` skips ASR while
other available modalities can still run.

The standalone CLI has different sampling defaults from `scripts.run_pipeline`;
use explicit sampling values when comparing outputs. `--min-segment-sec` is
accepted but unused by the current engine.

## Existing bundle

```console
python -m fusion --bundle sample_data/sample_analysis_bundle.json --skip-speech --out data/output/sample_segments.json
```

When a bundle names an existing video, the CLI can fill missing modalities.

## Python interface

```python
from pathlib import Path
from fusion.fuse import fuse_bundle_to_segments, load_bundle, write_segments_json

bundle = load_bundle(Path("data/output/example_analysis_bundle.json"))
segments = fuse_bundle_to_segments(bundle)
write_segments_json(segments, Path("data/output/example_segments.json"))
```

The segment file contains `schema_version`, `source`, and `segments`. Each
interval has `start`, `end`, `label`, and `kind`; timestamps are in seconds.
See the [root README](../README.md#output) for an example.

`ad_signals.json` contains curated brand and phrase signals.
`extra_brand_names.txt` retains its Simple Icons source and CC0 attribution.
The extended dictionary is enabled by default in the current implementation;
set `FUSION_USE_EXTRA_BRANDS=0` before startup to disable it.
