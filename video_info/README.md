# Stitched-video metadata

`test_009.json` is an example descriptor for a video with inserted ads. Its
`timeline_segments` list records `video_content` and `ad` intervals in final-video
seconds. The corresponding video is not included.

Place the file named by `video_filename` in `data/input/` or `videos_with_ad/`.
The visual CLI can use the descriptor and export reference ad timestamps:

```console
python -m visual_analyze --video-info video_info/test_009.json --videos-root data/input --bundle-out data/output/test_009_analysis_bundle.json --reference-out data/output/test_009_reference_ads.json
```

For ordinary videos, use the [pipeline runner](../README.md#quick-start); metadata
is not required.
