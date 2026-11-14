# Automatic Speech Recognition Setup

Install Python dependencies:

```bash
python -m pip install -r Automatic_speech_recognition/requirements.txt
```

Download one local speech-to-text model:

```bash
python -m Automatic_speech_recognition.segment_text_analyzer --download-model --model small
```

The default model is `small`. Models are stored under the `models/` folder next to `segment_text_analyzer.py`:

```text
models/faster-whisper-small
```

Only the selected model is downloaded. Other models are not downloaded unless you explicitly choose them.

Available models:

```text
tiny      fastest, lowest accuracy, lowest compute
base      fast, lower compute
small     default balance between speed and accuracy
medium    slower, higher accuracy
large-v3  slowest, highest accuracy, highest compute
```

Command options:

```text
video path        Required for transcription. Path to the local video file.
--download-model  Downloads the selected faster-whisper model and exits.
--model           Model size to use or download. Default: small.
--device          Inference device: cpu (default) or cuda.
--compute-type    Compute type for faster-whisper. Default: int8.
                  Common choices: int8, int16, float32.
--language        Transcription language code. Default: en.
--vad             Enables voice activity detection (default on in this CLI).
--no-vad          Disables voice activity detection.
--model-dir       Optional custom directory for the selected local model. The default directory is: Automatic_speech_recognition/models/faster-whisper-<model>
```

For example, the default `small` model uses:

```text
Automatic_speech_recognition/models/faster-whisper-small
```

Examples:

Run transcription with default options (`--model small`, `--language en`, VAD on):

```bash
python -m Automatic_speech_recognition.segment_text_analyzer data/input/example.mp4
```

Run transcription with a different downloaded model:

```bash
python -m Automatic_speech_recognition.segment_text_analyzer data/input/example.mp4 --model tiny
```

Run transcription with a different language:

```bash
python -m Automatic_speech_recognition.segment_text_analyzer data/input/example.mp4 --language zh
```

Run transcription with VAD enabled:

```bash
python -m Automatic_speech_recognition.segment_text_analyzer data/input/example.mp4 --vad
```

Notes:

- `faster-whisper` is used for offline speech-to-text.
- `pydantic` is required because the shared fusion schema defines `SpeechSpan` with Pydantic.
- `huggingface_hub` is only needed to download the selected model during setup.
- `build_speech_spans(video_path)` returns `list[SpeechSpan]`, where each item has `t0`, `t1`, and `text`.


The simple pipeline runner passes its own `--vad` flag, which defaults to off.
The player and fusion CLI enable VAD by default.
