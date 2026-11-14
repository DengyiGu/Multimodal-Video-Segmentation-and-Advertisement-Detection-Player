# Local video data

Place source videos in `data/input/`. The pipeline writes feature bundles and
segment files to `data/output/`. Both directories are excluded from Git.

```console
python -m scripts.run_pipeline data/input/example.mp4 --skip-speech
```

See the [README](../README.md) for batch processing and output details.
