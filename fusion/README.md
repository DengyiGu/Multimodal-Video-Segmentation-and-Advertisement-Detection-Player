# Fusion

`fuse.py` combines visual windows, audio features, and speech spans from an
`AnalysisBundle` into labeled intervals. The current engine emits Core Content,
Intro, Outro, and Advertisement. Detection parameters and rules live in this
module; sponsorship and brand phrases are stored in `ad_signals.json`.

## From an existing bundle

Run from the repository root:

```console
python -m fusion --bundle sample_data/sample_analysis_bundle.json --skip-speech --out data/output/sample_segments.json
```

When a bundle names an existing video, the CLI tries to fill missing audio and
speech features. `--skip-speech` disables transcription. Missing optional
modalities are reported in the terminal.

## From a video

For the standard visual, audio, and speech workflow, use the pipeline runner:

```console
python -m scripts.run_pipeline data/input/example.mp4 --skip-speech
```

The standalone fusion CLI also supports `--video`, `--bundle-out`, and `--out`:

```console
python -m fusion --video data/input/example.mp4 --skip-speech --sample-fps 1 --window-sec 2 --out data/output/example_segments.json
```

The standalone CLI has different sampling defaults from the pipeline runner.
Use explicit values when comparing their output. `--min-segment-sec` is retained
for compatibility but is unused by the current engine.

## Python interface

```python
from pathlib import Path
from fusion.fuse import fuse_bundle_to_segments, load_bundle, write_segments_json

bundle = load_bundle(Path("data/output/example_analysis_bundle.json"))
segments = fuse_bundle_to_segments(bundle)
write_segments_json(segments, Path("data/output/example_segments.json"))
```

The segment file contains `schema_version`, `source`, and `segments`. Each segment
has `start`, `end`, `label`, and `kind`; timestamps are in seconds. See the
[root README](../README.md#output) for an example and detection limitations.
