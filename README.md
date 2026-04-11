# S-Tier Staff Researcher

> Skills that make Claude Code and OpenAI Codex operate at
> **staff-researcher level** — structured research, rigorous LaTeX
> authoring, pitiless review, and the edit loop to keep all of it
> tight.

A personal, opinionated collection of distilled academic research
workflows: the kind of patterns a senior collaborator brings to the
table — pattern-matching failure modes, enforcing structural rigor,
catching the thing you would have missed on your third read. Each
skill in here is a workflow I've hit twice, captured once, and now
reuse across papers, lectures, and projects.

Every skill is format-compatible with **both Claude Code and Codex**.
Clone once, symlink to the other tool's path, and both see the same
source of truth.

![license](https://img.shields.io/badge/license-MIT-blue)
![tools](https://img.shields.io/badge/works_with-Claude_Code_%7C_Codex-purple)
![format](https://img.shields.io/badge/format-SKILL.md-green)

---

## ⚡ Quick start

```bash
# 1. Clone the repo into Claude Code's skill root
git clone https://github.com/shubham0704/claude-skills ~/.claude/skills

# 2. Symlink for Codex (one source of truth, both tools see it)
mkdir -p ~/.agents && ln -s ~/.claude/skills ~/.agents/skills
```

That's it. Start a new Claude Code or Codex session and the skills are
live. Trigger them by asking for what they do — the model reads each
skill's `description` field and picks up the right one automatically.

```
you: "run an RPI cycle on this codebase"            → /rpi-workflow
you: "review this figure for label collisions"      → /tikz-figure-review
you: "plan the structure for our new paper"         → /rigorous-paper-author
you: "address these reviewer comments on our paper" → /refining-ml-papers
```

---

## 🌟 Flagship: the RPI framework

[`rpi-workflow`](rpi-workflow/) is the crown jewel. **Research →
Plan → Implement** is a structured protocol for complex engineering
and research tasks, with **Codex architectural peer review baked in**.
Instead of jumping straight from a vague ask into a half-formed
implementation, RPI forces the model to:

1. **Research** — build a shared understanding of the problem,
   surface the unknowns, identify the constraints.
2. **Plan** — write the plan down as a concrete doc, then hand it to
   Codex (or another model) for an adversarial architectural review.
3. **Implement** — execute the approved plan with checkpoints, with
   implementation reports committed back to `docs/`.

All artifacts land under `docs/` in the project root as tracked
Markdown, so future sessions (and humans) can pick up exactly where
you left off. Trigger with `/rpi` or by asking for a research-plan-
implement cycle.

---

## 📚 All skills in this repo

| Skill | Purpose |
|-------|---------|
| ⭐ [`rpi-workflow`](rpi-workflow/) | **Research → Plan → Implement** workflow with Codex architectural peer review. Forces structured thinking before code and creates committed research/plan/report artifacts in `docs/`. |
| [`rigorous-paper-author`](rigorous-paper-author/) | Draft mathematically rigorous LaTeX papers with claim graphs, notation ledgers, theorem discipline, and numerical-analysis rigor. |
| [`rigorous-paper-reviewer`](rigorous-paper-reviewer/) | Deep 7-pass technical review of LaTeX papers (structure, notation, theorem/proof, numerics, complexity, figures, coherence) with a static Python verifier for automated triage. |
| [`refining-ml-papers`](refining-ml-papers/) | Revise ML/scientific LaTeX papers based on reviewer or advisor feedback — structural reorganization, table instantiation, cross-file deduplication. |
| [`tikz-figure-review`](tikz-figure-review/) | Review and fix alignment, label collision, clipping, legend-over-data issues in TikZ/pgfplots figures. 11 failure modes + copy-paste snippet catalog. |
| [`enhancing-latex-lectures`](enhancing-latex-lectures/) | Enhance LaTeX lecture notes with visualizations, concrete examples, and pedagogical patterns from reference material. |

## 🤝 External skills I use (installed separately)

Skills I rely on but didn't write — clone or install them directly
from their authors. Listed here so my setup is reproducible and the
original authors get visible credit.

| Skill | Author | Install | Purpose |
|-------|--------|---------|---------|
| `poster` ([posterskill](https://github.com/ethanweber/posterskill)) | [Ethan Weber](https://github.com/ethanweber) | `git clone git@github.com:ethanweber/posterskill.git ~/.claude/skills/poster` | Generate print-ready conference posters from your paper source + project website, with a live in-browser layout editor. |
| `research-companion` ([repo](https://github.com/andrehuang/research-companion)) | [Andre Huang](https://github.com/andrehuang) | Claude Code plugin — install via marketplace | Strategic research thinking agents — idea critic, research strategist, enhanced brainstormer, structured brainstorming skill for research ideation (inspired by Carlini's research methodology). |

The same symlink above (`~/.agents/skills → ~/.claude/skills`) makes
all of these visible to both Claude Code and Codex if you install
them alongside.

---

## 🛠 Why both Claude Code and Codex?

Both tools converged on the same skill format: a `SKILL.md` file with
YAML frontmatter (`name` + `description`) and optional `references/`,
`scripts/`, `assets/` subdirectories. The only difference is the
discovery path:

- **Claude Code** scans `~/.claude/skills/`
- **Codex** scans `~/.agents/skills/` (user-level) or
  `$CWD/.agents/skills` (project-local)

One clone + one symlink = both tools see the same source of truth
with zero drift. See the
[Anthropic skill docs](https://code.claude.com/docs/en/skills) and
[Codex skill docs](https://developers.openai.com/codex/skills) for
each tool's discovery rules.

## 🧠 How skills work (progressive disclosure)

Skills are **model-invoked**: the model reads the `description` field
in each skill's frontmatter and triggers the right one automatically
based on your request. You can also invoke explicitly with
`/<skill-name>`.

Each skill loads in three layers so your context window doesn't
bloat:

1. **Metadata** (name + description, ~100 words) — always in context
2. **SKILL.md body** — loads only when the skill triggers (aim for
   <500 lines)
3. **Bundled resources** (`references/`, `scripts/`, `assets/`) —
   load on-demand when the body points at them

For the canonical reference and the full iterate-and-eval loop (test
prompts, benchmarks, description optimization), see Anthropic's
[skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).

---

## 🔄 Maintenance playbook — how I keep skills from rotting

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
