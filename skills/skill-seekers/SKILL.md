---
name: skill-seekers
description: Discover, fetch, and inventory agent skills from GitHub, skills.md registries, and Drive. Triggers on /SKILL-SEEKERS, find skills, skill search, video skills list.
metadata:
  version: "1.0"
---
# Skill Seekers

## Sources

| Source | How |
|--------|-----|
| GitHub raw SKILL.md | `raw.githubusercontent.com/.../SKILL.md` or gh get_file_contents |
| skills.md | Directory / registry of skills |
| marketingskills | coreyhaines31/marketingskills |
| browser-use/video-use | Conversational video edit skill |
| EveryInc/product-launch-video | Remotion launch workflow |
| mdskills.ai / skillgild / nanoskill | Web catalogs |
| Local | `/root/.grok/server-skills/*/SKILL.md` |

## Process

1. Parse user intent → keywords (video, remotion, hyperframes, clone…)
2. Search GitHub + web for SKILL.md
3. Fetch full text; extract name, description, hard rules
4. Write inventory JSON: `{name, source, triggers, tools, quality}`
5. Rank by fitness to current runtime (what tools exist here)

## Output schema

```json
{"skills":[{"name":"","source_url":"","triggers":[],"tools":[],"summary":"","install_path":""}]}
```
