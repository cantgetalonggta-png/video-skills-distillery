---
name: skill-distiller
description: Distill multiple SKILL.md and docs into one master skill + atomic knowledge atoms. Triggers on /SKILL-DISTILLER, distill skills, merge skills, video master skill.
metadata:
  version: "1.0"
---
# Skill Distiller

## Process

1. Load all source SKILL.md + related docs
2. Extract: hard rules, workflows, tool maps, platform specs, anti-patterns
3. Deduplicate; prefer more specific hard rules
4. Emit:
   - `video-master/SKILL.md` — unified agent skill
   - `atoms.json` — atomic knowledge units
   - `tool-matrix.json` — approach × tool × when
5. Verify with common sense: every hard rule prevents a real silent failure

## Distillation rules

- Keep production-correctness rules from video-use (subtitle last, 30ms fades, word-boundary cuts…)
- Keep product-launch storyboard-before-code + multi-critic review
- Keep marketing-video tool selection matrix (Hyperframes vs Remotion vs Veo vs HeyGen)
- Map to Grok runtime: Imagine (6–15s), HyperFrames MCP (minutes), Voice TTS, ffmpeg
