# S-Tier Staff Researcher

> Skills + workflows that help **you** operate at staff-researcher
> level. The agent does the grunt work; you stay in the driver's seat.

A personal, opinionated collection of skills that give Claude Code and
OpenAI Codex a **proper workflow — not vibes** — for research work.

Research isn't a linear pipeline. It's a **loop**: you polish raw
ideas, express them (to yourself in a paper, to others in a lecture,
to code in an experiment), and the act of expressing reveals whether
you actually understand. Gaps feed back into polishing. Implementation
feeds back into the paper. Teaching feeds back into the research plan.
**S-Tier researchers run this loop fast and rigorously.**

```
      ┌─────────── Polish ───────────┐
      │  raw ideas → worth writing   │
      │   down. brainstorm, triage,  │
      │   research-the-problem.      │
      └──────┬───────────────┬───────┘
             │               │
             ↓               ↑        ↖
       ┌─────────┐   gaps found during
       │ Express │   expressing/teaching
       │  it.    │   kick you back here.
       └────┬────┘
            │
            ↓
    ┌───────────────┐
    │   Implement   │ ← RPI + Codex adversarial review
    │ (experiments, │
    │  infra, code) │
    └───────────────┘
```

Every skill in this repo is a workflow I've hit twice, captured once,
and now reuse across papers, lectures, and projects. Format-compatible
with **both Claude Code and Codex** — clone once, symlink to the other
tool's path, both see the same source of truth.

![license](https://img.shields.io/badge/license-MIT-blue)
![tools](https://img.shields.io/badge/works_with-Claude_Code_%7C_Codex-purple)
![format](https://img.shields.io/badge/format-SKILL.md-green)

---

## 🎯 Who this is for

- **Academic researchers** who want agents to act like senior
  collaborators — pattern-matching failure modes, enforcing rigor,
  catching the thing you'd miss on your third read.
- **PhD students** drafting theory-heavy papers where claim graphs,
  notation discipline, and proof obligations are load-bearing.
- **ML engineers** running research infrastructure who need
  structured engineering (plan → adversarial review → implement)
  instead of brainstorm-and-hope.
- **Educators** who want lectures to serve as a *Feynman test* on
  their own understanding, not just an output artifact.

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

---

## 🧭 Start here

Not sure where to begin? Match your situation to the first skill:

| If you're... | Start with | Because |
|---|---|---|
| **Sitting with a raw, half-formed research idea** | `research-companion` *(external)* | Adversarial sparring partner on the idea itself before you invest any drafting effort. |
| **Trying to prove you actually understand a concept** | [`enhancing-latex-lectures`](enhancing-latex-lectures/) | **Feynman test.** If you can't teach it with a stunning visualization, you haven't earned the right to claim it in a paper yet. |
| **Drafting a theory-heavy paper from scratch** | [`rigorous-paper-author`](rigorous-paper-author/) | Enforces claim graphs, notation ledgers, and theorem discipline before you write a single sentence. |
| **Hardening a draft before submission** | [`rigorous-paper-reviewer`](rigorous-paper-reviewer/) | 7-pass adversarial read finds the cracks a sympathetic eye misses. |
| **Reviewer comments just came back** | [`refining-ml-papers`](refining-ml-papers/) | Addresses comments without breaking the claim graph; surgical revisions. |
| **Starting a complex engineering task** | [`rpi-workflow`](rpi-workflow/) | Research the codebase, plan the change, adversarially review the plan, *then* implement. No vibe-coding. |
| **One figure looks wrong** | [`tikz-figure-review`](tikz-figure-review/) | 11 documented failure modes + standalone iteration loop. |
| **Paper accepted, conference coming up** | `poster` *(external)* | Turns paper source + website into shippable print-ready poster with a live in-browser editor. |

---

## 🔁 The research loop: Polish ↔ Express ↔ Implement

The skills group into three phases, but treat them as a **loop, not a
pipeline**. Every time you try to *express* something — in a draft,
in a review, in a lecture, in code — you find out whether your
understanding is real. Gaps you discover go back into polishing.
Implementations that don't match the paper go back into expressing.

### 1. Polish 🧠 — raw ideas → worth writing down

Brainstorming, strategic triage, research-the-problem.

| Skill | Your specialist | What they do |
|---|---|---|
| `research-companion` *(external — [Andre Huang](https://github.com/andrehuang/research-companion))* | **Research Strategist / Devil's Advocate** | Idea critic, research strategist, structured brainstorming. When you want an adversarial sparring partner on a half-formed idea (inspired by Carlini's research methodology). |

### 2. Express 📝 — worth writing down → defensibly correct *and teachable*

Authoring, review, revision, teaching, visualization. This is also
where the **Feynman test** lives: if you can't teach it simply, you
don't understand it, and you go back to Polish.

| Skill | Your specialist | What they do |
|---|---|---|
| [`rigorous-paper-author`](rigorous-paper-author/) | **Theory-Paper Ghostwriter** | Draft mathematically rigorous LaTeX papers with claim graphs, notation ledgers, theorem discipline, and numerical-analysis rigor. |
| [`rigorous-paper-reviewer`](rigorous-paper-reviewer/) | **PhD-Committee Reviewer** | 7-pass adversarial technical review (structure, notation, theorem/proof, numerics, complexity, figures, coherence) with a static Python verifier for automated triage. |
| [`refining-ml-papers`](refining-ml-papers/) | **Revision Surgeon** | Revise ML/scientific LaTeX papers based on reviewer or advisor feedback — structural reorganization, table instantiation, cross-file deduplication. |
| [`enhancing-latex-lectures`](enhancing-latex-lectures/) | **Feynman-Test Partner** | Pattern-matches against exemplary pedagogical material (e.g. Todorov's PDFs) and adds stunning visualizations, concrete-to-abstract progressions, insight boxes. **Making a concept teachable is how you discover whether you understand it well enough to write the paper.** |
| [`tikz-figure-review`](tikz-figure-review/) | **Figure Layout Engineer** | Review and fix alignment, label collision, clipping, legend-over-data issues in TikZ/pgfplots figures. 11 failure modes + copy-paste snippet catalog. |
| `poster` *(external — [Ethan Weber](https://github.com/ethanweber/posterskill))* | **Conference Poster Designer** | Generate print-ready conference posters from your paper source and project website, with a live in-browser layout editor. |

### 3. Implement ⚙️ — teachable → working code

Research the codebase, plan the change, adversarially review the plan,
*then* implement. No vibe-coding.

| Skill | Your specialist | What they do |
|---|---|---|
| ⭐ [`rpi-workflow`](rpi-workflow/) | **Research Engineer / Tech Lead** *(with Codex on speed-dial)* | **Research → Plan → Implement** with Codex architectural peer review baked in. Never plans without understanding the codebase; always gets a second opinion before coding. Commits research/plan/feedback/impl/validation artifacts to `docs/`. This is the flagship — see the deep dive below. |

---

## 🔗 How skills chain together

Phases aren't silos. Each skill produces artifacts that downstream
skills consume, so a full cycle threads through multiple skills:

- **Polish → Express (idea to draft).** `research-companion` produces
  a validated research direction. Hand it to `rigorous-paper-author`
  (papers) or `rpi-workflow`'s research phase (code).
- **Express → Express (draft ↔ review loop).**
  `rigorous-paper-author` emits a draft with a claim graph.
  `rigorous-paper-reviewer` reads the draft and writes a 7-pass review
  report. `refining-ml-papers` reads the review (or external reviewer
  comments) and produces a revised version. `tikz-figure-review`
  fixes any figures flagged in the review. The whole loop converges
  on a camera-ready PDF.
- **Express → Polish (Feynman kickback).**
  `enhancing-latex-lectures` forces you to explain a concept simply
  with beautiful visualizations. If you stumble, you have a gap — go
  back to `research-companion` and polish your understanding before
  continuing.
- **Express → Implement (paper to code).** Once the claim graph and
  proofs hold, `rpi-workflow` takes the experimental plan and turns
  it into a concrete engineering task: research the codebase in
  parallel with Explore agents, write a `PLAN-<repo>-<task>.md`, run
  `codex exec` to get adversarial architectural feedback, iterate,
  implement, commit an `IMPL-<repo>-<task>.md` report.
- **Implement → Express (experiments back to paper).** When the RPI
  implementation produces results, feed them back through
  `refining-ml-papers` (to update Table 1 with concrete
  instantiations) or `tikz-figure-review` (to render new convergence
  plots cleanly).
- **Express → Ship (paper to conference).** When the paper is
  accepted, `poster` generates a print-ready conference poster from
  the same source material.

The common thread: **every skill writes its artifact to disk** (into
`docs/` for RPI, into your LaTeX source tree for the paper skills, into
a standalone figure scratch directory for `tikz-figure-review`), so
the next skill in the chain — or a future session, or a human
collaborator — can pick up exactly where the last one left off.

---

## 🌟 Flagship deep-dive: the RPI framework

[`rpi-workflow`](rpi-workflow/) is the crown jewel and the engineering
backbone of everything in this repo. **Research → Plan → Implement**,
with **Codex architectural peer review baked in** so a second model
adversarially reviews the plan before you spend any implementation
effort.

It's not "senior researcher" in the abstract — it's a concrete
engineering discipline for people who refuse to vibe-code. The skill
walks you through six steps, all artifacts landing under `docs/`:

```
docs/
├── research/YYYY-MM-DD-topic.md    # parallel Explore agents dump findings here
└── plans/
    ├── PLAN-<repo>-<task>.md        # Claude writes: goal, key files,
    │                                 # problem, solution, success criteria,
    │                                 # risks, 3–5 questions for Codex
    ├── FEEDBACK-<repo>-<task>.md    # Codex writes: adversarial review
    │                                 # (missing edge cases, better abstractions,
    │                                 # risks Claude missed, phase reordering)
    ├── IMPL-<repo>-<task>.md        # Claude writes after coding:
    │                                 # what actually changed (path:line refs),
    │                                 # deviations from plan and why, test results
    └── VALIDATION-<repo>-<task>.md  # Codex writes (optional): success criteria met?
```

The non-negotiables RPI enforces:

- **Research first.** Never plan without understanding the codebase.
  Parallel Explore subagents gather context before a single line of
  plan gets written.
- **Compact findings.** `path:line` references, not code dumps.
- **3–5 architectural questions for Codex.** Every plan explicitly
  asks Codex to adversarially attack specific concerns.
- **Parity checks before deletion.** Side-by-side comparison before
  any old code gets removed.
- **Independently mergeable phases.** Each plan phase must ship
  on its own.

The point isn't that RPI makes the model smarter. It's that the
structure forces *you* and the agent into a disciplined loop a senior
tech lead would use, instead of brainstorm-and-hope. Trigger with
`/rpi` or "start RPI".

---

## 🎬 See it work — a realistic paper-hardening cycle

Here's what a full cycle looks like through four of these skills on
an actual use case: you have a draft, reviewers meet next week, you
need to harden it.

```
you: "my ICML draft is done, reviewers meet next week, help me harden it"

Claude: invoking /rigorous-paper-reviewer
  [7-pass review: finds notation drift between §3 and §5, a missing
   proof obligation on Theorem 2, a claim in the abstract that doesn't
   survive §4.2. Writes a review report in the standard format.]

you: "OK let's fix the proof first"

Claude: invoking /rigorous-paper-author
  [rewrites §2's notation ledger so §3 and §5 can agree, discharges
   the missing proof obligation on Theorem 2, patches the abstract
   claim to match what §4.2 actually shows. Updates the claim graph.]

you: "figure 3 looks weird in the PDF"

Claude: invoking /tikz-figure-review
  [extracts figure 3 as a standalone, identifies a legend-over-data
   collision (§2.1 of the figure-review skill) and a label-on-marker
   collision on two equilibria (§2.2b — the #1 phase-portrait footgun).
   Fixes both in the standalone, syncs the tikzpicture body back to
   the main paper, re-renders, verifies the PNG is clean.]

[reviewer comments come back Monday]

you: "address these 14 comments"

Claude: invoking /refining-ml-papers
  [structural reorganization across 3 sections, concrete instantiation
   of the abstract table from §4 with real results from your
   experiment logs, cross-file deduplication between §2.1 and §B.1,
   compilation verification after every change.]

→ camera-ready
```

Notice the cycle: reviewer finds a gap → author fixes the gap → review
finds the ripple → figure review catches collateral damage → refining
threads the reviewer comments through everything. Each skill consumes
the artifacts from the previous one. That's the chain.

---

## 🤝 Installing the external skills

Two of the skills above are maintained by their authors, not in this
repo. Clone / install them directly so authors get the stars and you
get updates from source:

```bash
# research-companion — install as a Claude Code plugin (phase 1: polish)
# see https://github.com/andrehuang/research-companion for plugin install

# posterskill — clone into ~/.claude/skills/poster (phase 2: express)
git clone git@github.com:ethanweber/posterskill.git ~/.claude/skills/poster
```

The same symlink above (`~/.agents/skills → ~/.claude/skills`) makes
both visible to Claude Code and Codex with no extra setup.

---

## 🛠 Works with Claude Code *and* Codex

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

---

## 🧠 How skills work (progressive disclosure)

Skills are **model-invoked**: the model reads the `description` field
in each skill's frontmatter and triggers the right one automatically
based on your request. You can also invoke explicitly with
`/<skill-name>`.

Each skill loads in three layers so your context window doesn't bloat:

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
