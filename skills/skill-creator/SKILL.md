---
name: skill-creator
description: Create high-quality SKILL.md files for agents. Triggers on /SKILL-CREATOR, create skill, write skill, new skill, skill scaffold.
metadata:
  version: "1.0"
  type: meta
---
# Skill Creator

## SKILL.md format (canonical)

```yaml
---
name: kebab-case-id
description: >
  One paragraph: what it does + WHEN to trigger (verbs, tools, user phrases).
  Frontmatter is the only thing routers read — make triggers explicit.
metadata:
  version: "1.0"
---
```

## Structure template

1. **Frontmatter** — name + description with trigger phrases
2. **Principle** — 3–7 hard rules (correctness, not taste)
3. **When to use / When not**
4. **Prerequisites**
5. **Workflow** — numbered, ask→confirm→execute→iterate when irreversible
6. **Helpers / tools / commands**
7. **Worked examples** (taste) separate from **Hard rules** (correctness)
8. **Common mistakes**
9. **Related skills**

## Quality bar

- Description must list real trigger phrases users say
- Hard rules only for silent failures / broken output
- Everything else is "worked example — invent freely"
- Prefer tools available in the runtime (HyperFrames, Remotion, ffmpeg, Grok Imagine, HeyGen MCP)
- Cap self-eval loops (e.g. 3 passes) to avoid infinite polish

## Output

Write `skills/<name>/SKILL.md` + optional `references/` and `helpers/`.
