# Claude Code Skills

A personal collection of Claude Code skills — distilled workflows,
review rubrics, and writing/building patterns I've accumulated across
projects. Each skill lives in its own directory with a `SKILL.md`
(required), optional `references/`, `scripts/`, and `assets/`, and a
`CHANGELOG.md` that records how the skill evolved.

This README is the top-level index and maintenance playbook. The
per-skill detail lives inside each skill directory.

---

## Skills in this repo

| Skill | One-line purpose |
|-------|------------------|
| [`enhancing-latex-lectures`](enhancing-latex-lectures/) | Enhance LaTeX lecture notes with visualizations, concrete examples, and pedagogical patterns from reference material. |
| [`refining-ml-papers`](refining-ml-papers/) | Revise ML/scientific LaTeX papers based on reviewer or advisor feedback — structural reorganization, table instantiation, cross-file deduplication. |
| [`rigorous-paper-author`](rigorous-paper-author/) | Draft mathematically rigorous LaTeX papers with claim graphs, notation ledgers, and theorem discipline. |
| [`rigorous-paper-reviewer`](rigorous-paper-reviewer/) | Deep technical review of LaTeX papers in 7 ordered passes, with a static Python verifier for automated triage. |
| [`rpi-workflow`](rpi-workflow/) | Research–Plan–Implement workflow with Codex peer review. |
| [`tikz-figure-review`](tikz-figure-review/) | Review and fix alignment, label collision, clipping, and legend-over-data issues in TikZ/pgfplots figures. |

## External skills I use (installed separately)

These are skills I rely on but didn't write — clone or install them
directly from their authors. They're listed here so my setup is
reproducible and the original authors get credit.

| Skill | Author | Install | Purpose |
|-------|--------|---------|---------|
| `poster` ([posterskill](https://github.com/ethanweber/posterskill)) | [Ethan Weber](https://github.com/ethanweber) | `git clone git@github.com:ethanweber/posterskill.git ~/.claude/skills/poster` | Generate print-ready conference posters from your paper source + project website, with a live in-browser layout editor. |
| `research-companion` ([repo](https://github.com/andrehuang/research-companion)) | [Andre Huang](https://github.com/andrehuang) | Claude Code plugin — install via marketplace | Strategic research thinking agents — idea critic, research strategist, enhanced brainstormer, structured brainstorming skill for research ideation (inspired by Carlini's research methodology). |

If you install these alongside the ones in this repo, the same
symlink (`~/.agents/skills → ~/.claude/skills`) makes everything
visible to both Claude Code and Codex.

---

## Installation

The skills in this repo use the shared `SKILL.md` + YAML-frontmatter
format that works for **both Claude Code and OpenAI Codex** (the
format is identical — only the discovery path differs). Clone once,
symlink from the other tool's expected path:

```bash
# Clone into the Claude Code skill root:
git clone https://github.com/<you>/claude-skills ~/.claude/skills

# Expose the same skills to Codex (symlink, no duplication):
mkdir -p ~/.agents
ln -s ~/.claude/skills ~/.agents/skills
```

Now `git pull` updates both tools at once. Claude Code scans
`~/.claude/skills/`; Codex scans `~/.agents/skills/` (user-level) or
`$CWD/.agents/skills` (project-local). See
[Anthropic skill docs](https://code.claude.com/docs/en/skills) and
[Codex skill docs](https://developers.openai.com/codex/skills) for
each tool's discovery rules.

If you'd rather install the other direction (primary in `~/.agents/`,
symlink to `~/.claude/skills`), either works — same result. Codex
has one optional extra, `agents/openai.yaml` per skill, which is
Codex-specific metadata (not in SKILL.md) — add it per-skill if you
need tighter Codex integration.

## How skills work

Skills are **model-invoked**: the model reads the `description` field
in each skill's YAML frontmatter and triggers the relevant skill
automatically based on your request. You don't need to name the skill
explicitly — though you can, via `/<skill-name>` or by referencing it
in prose.

Progressive disclosure: metadata (name + description, ~100 words) is
always in context. The full `SKILL.md` body loads only when the skill
triggers. Files under `references/`, `scripts/`, and `assets/` load
on-demand when the body points at them. Keep each `SKILL.md` under
~500 lines and push overflow into bundled resources.

For the canonical reference and the iterative improvement loop (eval
pipeline, benchmarks, description optimization), see the Anthropic
[skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).

---

## Updating skills — the maintenance playbook

Skills and sessions run at different tempos. A session produces raw
material — corrections, edge cases, workflow refinements. A skill is
distilled guidance — high-signal, coherent, not every fleeting
observation. Follow the pipeline below to keep skills evolving
without bloating them.

### 1. Two-layer storage

Each skill has both a `SKILL.md` (distilled rules) and a `CHANGELOG.md`
(raw learnings + version history). Raw observations land in the
changelog immediately; polished rules only enter the skill body after
they've proven themselves.

### 2. The hit-twice rule

Don't promote a new failure mode or rule to `SKILL.md` until it's
happened **twice**. First incident: log a candidate entry in
`CHANGELOG.md` with the incident, fix, and date. Second incident:
promote to the skill body with "seen twice" as the provenance marker.
This is a lightweight alternative to a full eval loop — use it for
small additions. For bigger rewrites, use the Anthropic skill-creator
eval pipeline instead.

### 3. End-of-session sweep

When a session ends that used a skill, take 2 minutes to ask: "what
did we hit that isn't in the skill?" A subagent can do the first
pass: *"read the session transcript and the current SKILL.md, propose
a diff of additions."* A human reviews and merges — agents are good
at spotting candidates, but a human greenlights promotions or you'll
accumulate both signal and noise.

### 4. Commit discipline

Conventional-commits-style messages. Your git history becomes a
readable log of what you learned when.

```
feat(tikz-figure-review): add §2.12 for dashed enclosure label strike-through
fix(refining-ml-papers): correct table instantiation example in §4
docs(rigorous-paper-reviewer/changelog): log candidate for reference overflow
refactor(tikz-figure-review): split snippets into references/
chore(skill): bump version to 1.1.0
```

### 5. Semantic versioning

Each skill carries a `version:` field in its frontmatter. Follow
semver semantics:

- **MAJOR** (x.0.0) — breaking changes: different trigger, different
  expected output shape, incompatible workflow.
- **MINOR** (1.x.0) — new failure modes, new sections, new features.
  Backward-compatible.
- **PATCH** (1.0.x) — wording tweaks, typos, clarifications, new
  examples. No behavioral change.

### 6. Quarterly compaction

Every ~3 months, re-read each skill with fresh eyes. Still coherent?
Still under 500 lines? Any sections outdated? Refactor, deprecate,
reorganize. Don't just append forever — skills decay silently. When
deprecating rules, mark them rather than deleting: `(deprecated Mar
2026 — see §2.Y)`.

### 7. Pre-push audit (public repos)

Before every push, run `scripts/pre-push-audit.sh` to grep for
accidental leaks: email addresses, API keys, client names, absolute
home paths, internal project names. The script exits non-zero if it
finds anything worth reviewing — you decide whether each hit is a
real problem or a false positive.

---

## Creating a new skill

Start from `docs/skill-template/` which has a skeletal SKILL.md and
CHANGELOG.md already wired up (it lives under `docs/` rather than at
the root so Claude Code doesn't auto-register it as a real skill).
Copy it to a new top-level directory, fill in the frontmatter, drop
in your content, bump the version to `0.1.0` (initial draft) or
`1.0.0` (first stable release):

```bash
cp -r docs/skill-template my-new-skill
# Then edit my-new-skill/SKILL.md and my-new-skill/CHANGELOG.md
```

For anything nontrivial, use the Anthropic skill-creator workflow:
draft → test prompts → eval → review → iterate. Don't skip evals
just because your skill "feels right" — the eval pipeline catches
things that intuition misses.

---

## Anti-patterns

- **Auto-commit every tweak** — bloats history, loses intent. Batch
  related edits.
- **Delete rules without a diff trail** — loses the "why this rule
  exists" context. Deprecate, don't delete.
- **Over-fit to one session** — skill becomes a catalog of weird
  one-offs instead of general patterns. Hit-twice protects against
  this.
- **Skip compaction** — you'll notice at 1500 lines when it's too
  late.
- **Fully autonomous promotion** — the human in the loop is a feature.
  Agents propose, humans merge.
- **Skip the pre-push audit** — a single leaked client name in a
  public repo is a painful rewrite-and-force-push later.
