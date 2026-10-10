---
name: free-render
description: >
  Prefer free open-source video render paths (ffmpeg, HyperFrames CLI Apache-2.0, Motion Canvas,
  fframes, html-video) before paid HeyGen MCP render_video. Triggers on free render, open source
  video render, no paid credits, local MP4, HyperFrames CLI, ffmpeg render.
metadata:
  version: "1.0"
---
# Free Render

## Rule
Never require paid render_video when a free path exists.

## Priority
1. ffmpeg-local
2. HyperFrames CLI (Apache-2.0, Node>=22)
3. Motion Canvas / fframes / html-video
4. Grok Imagine short clips
5. Remotion (free <=4 devs)
6. HeyGen MCP paid last

## Proof
python3 scripts/free_render_demo.py --out renders/free-demo.mp4
