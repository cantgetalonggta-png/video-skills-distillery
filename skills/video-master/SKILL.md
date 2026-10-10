---
name: video-master
description: >
  Master video skill distilled from video-use, product-launch-video, and marketing video skills.
  Triggers on make a video, edit video, product launch video, HyperFrames, Remotion, AI video,
  captions, storyboard, B-roll, avatar video, distill video skills.
metadata:
  version: "1.0"
  distilled_from: [video-use, product-launch-video, marketing-video]
---
# Video Master (Distilled)

## Hard rules (non-negotiable)

1. Subtitles **last** in filter chain (after overlays).
2. Per-segment extract → lossless concat (no double-encode).
3. **30ms** audio fades at every segment boundary.
4. Overlays: `setpts=PTS-STARTPTS+T/TB`.
5. Master SRT uses **output-timeline** offsets.
6. Never cut inside a word; pad 30–200ms.
7. Word-level verbatim ASR only; cache transcripts.
8. Strategy confirmation before execution.
9. Never invent product UI labels — mirror real app.
10. Burn captions for social (85% muted).
11. Self-eval ≤3 passes; then ship or flag.
12. Product visible within ~3s on launch clips.

## Choose stack

| Need | Stack |
|------|--------|
| Edit existing takes | video-use + ffmpeg + ASR |
| 15–30s launch | Remotion product-launch-video + 4 critics |
| Agent HTML motion | HyperFrames (MCP compose / local CLI) |
| Short gen B-roll | Grok Imagine / Veo / Kling |
| Talking head no film | HeyGen avatar / HyperFrames |
| Long branded | HyperFrames MCP (minutes) |

## Grok runtime map

- **Imagine:** 6/10/15s, 480p–1080p
- **HyperFrames connector:** prompt duration, ~1080p MP4, paid render
- **Voice:** 28 catalog voices (no MP3 clone ingest)
- **ffmpeg:** stitch, fades, captions, grade

## Workflow skeleton

1. Inventory assets + platform aspect
2. Storyboard / strategy (confirm)
3. Produce (edit | code | gen | avatar)
4. Critic pass (design, text, narrative, brand)
5. Export platform packs + captions
