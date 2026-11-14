# Desktop player

Install the player dependencies and launch from the repository root:

```console
python -m pip install -e ".[player]"
python -m player.player
```

Choose **File > Open Video**. The player loads cached segment JSON when available,
otherwise it analyzes the video in a background worker. This path adds optional
OCR and semantic scoring, with speech and OCR run concurrently. Precomputing with
`python -m scripts.run_pipeline` makes subsequent opens faster.

## Controls

- **Play/Pause**, volume, and playback speed.
- **Prev Segment** and **Next Segment** for segment navigation.
- Double-click a timeline segment or segment-list row to seek to it.
- **Play Content Only** skips segments whose `kind` is `non-content`.
- **F** toggles fullscreen; **Esc** exits fullscreen; **Space** toggles playback.

## Segment loading

`player_fusion.py` checks `data/output/<video_stem>_segments.json` first, then the
video's directory. A legacy `_visual_track` filename suffix is also supported.
If loading fails, it tries live analysis. If that fails, it probes the duration
and returns one Core Content segment. Diagnostics are printed to the terminal.

## Segment format

`build_segment_from_payload()` in `segments.py` converts each JSON interval to
the player's `Segment` dataclass. Start and end times are seconds, and `end` must
be greater than `start`. Supply segments in chronological order, without overlap,
and preferably covering the entire video.

The player taxonomy accepts Core Content, Intro, Outro, Advertisement,
Self-Promotion, Recap, Transition, Inactivity, and Filler. Only Core Content is
classified as `content` by default. The fusion engine currently produces the
first four labels. See the [JSON example](../README.md#output).

## Inference devices

The existing player defaults to CUDA for OCR and semantic models; speech uses
CPU `int8` with VAD. Set `CS576_TEXT_MODEL_DEVICE=cpu` before launching to run
OCR and semantic inference on CPU. See the [README](../README.md#analyze-and-play)
for the PowerShell command. Missing dependencies or local models are skipped
with terminal diagnostics.
