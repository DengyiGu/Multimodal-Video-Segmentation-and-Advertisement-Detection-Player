# Installation and usage

## Environment

Use Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -e ".[player,speech]"
```

On macOS and Linux, activate with `source .venv/bin/activate`.
For command-line analysis without the desktop player or speech recognition,
install with `python -m pip install -e .` instead.

The dependency files are also available for source-based use:

```console
python -m pip install -r requirements.txt
python -m pip install -r requirements-player.txt
python -m pip install -r Automatic_speech_recognition/requirements.txt
```

## FFmpeg

Install FFmpeg with both `ffmpeg` and `ffprobe` available on PATH. On Windows:

```powershell
winget install --id Gyan.FFmpeg
```

Open a new terminal after installation, reactivate the environment, and check:

```console
ffmpeg -version
ffprobe -version
```

The audio analyzer uses FFmpeg to extract audio. Duration probing may use
ffprobe. Video playback also depends on the codecs supported by Qt's backend.

## Speech model

Download the model once before running the full pipeline:

```console
python -m Automatic_speech_recognition.segment_text_analyzer --download-model --model small
```

Models remain in `Automatic_speech_recognition/models/` and are excluded from
Git. Transcription uses CPU `int8` compute. See the
[speech setup guide](Automatic_speech_recognition/SETUP.md) for model options.

## Analyze and play

```console
python -m scripts.run_pipeline data/input/example.mp4
python -m player.player
```

Use `--skip-speech` if no model is installed, or `--skip-audio` for visual-only
analysis. The command-line runner requires the requested dependencies and model;
it does not silently skip missing speech support.

In **File > Open Video**, select the analyzed file. The player first checks
`data/output/<stem>_segments.json`, then a matching file beside the video. Run
from the repository root to use the standard output directory. Existing cached
segments take priority; rerun the pipeline to refresh them after changing a
source video or analysis settings.

## Troubleshooting

- **Module not found:** activate this project's environment and run commands
  from the repository root. Use `python -m ...` as shown above.
- **Local speech model not found:** download the same model selected with
  `--model`, or use `--skip-speech`.
- **FFmpeg or ffprobe not found:** check PATH in a new terminal.
- **Player has no detected labels:** check terminal messages. If live analysis
  fails, the fallback is one full-length content segment.
- **Custom outputs are not loaded:** place `<stem>_segments.json` beside the
  video, or use the default `data/output/` directory.

## Optional OCR and semantic models

See the [README](README.md#optional-ocr-and-semantic-scoring) for optional
installation and model preparation. The simple runner uses visual/audio/speech
analysis. The fusion CLI and player also support OCR and semantic scoring.

The player defaults to CUDA for OCR and semantic inference. To choose CPU:

```powershell
$env:CS576_TEXT_MODEL_DEVICE = "cpu"
python -m player.player
```

The fusion CLI uses CPU unless `--cuda-text-models` is selected. ASR device
selection is separate. See the [README](README.md) for the full usage details.
