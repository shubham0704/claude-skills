# Changelog — tikz-figure-review

All notable changes to this skill. Format follows
[Keep a Changelog](https://keepachangelog.com/) and the skill adheres
to [Semantic Versioning](https://semver.org/).

Each release section has two parts:

- **Promoted rules** — new content that landed in `SKILL.md`. Follow
  the hit-twice rule: promote only after a pattern has been observed
  twice (or bypass it for a big rewrite and run the Anthropic
  skill-creator eval pipeline instead).
- **Candidate observations** — raw learnings from recent sessions
  that haven't earned their way into `SKILL.md` yet.

---

## [Unreleased]

### Candidate observations

<!--
One bullet per raw observation. Keep context short. Example:

- **2026-05-03 — Tick labels clipping at long y-axis labels.** Seen
  once in a Rayleigh distribution plot. Fix: `ylabel style={yshift=
  -10pt}`. Waiting for a second incident.
-->

*(none yet — log first-time observations here, promote on the
second incident)*

### Promoted rules

*(none promoted this cycle)*

---

## [1.0.0] — 2026-04-11

First stable release. Skill covers 11 failure modes plus the
extract → standalone → PNG → review workflow learned from two rounds
of real figure review.

### Workflow

- Extract each tikzpicture to a `standalone`-class scratch file that
  shares a common preamble with the main document.
- Compile with `pdflatex`, render to PNG with `pdftoppm`, view via
  Read tool.
- Fix in the standalone, sync to the main file, re-render, iterate.
- For 20+ figure documents, dispatch an extraction subagent first,
  then batch review subagents (5–7 agents handling 5–6 figures
  each).

### Failure modes documented (§2.1–§2.11)

- §2.1 Legend on top of data — four fix tiers in preference order.
- §2.2a Text label on a dashed/solid enclosure border.
- §2.2b Label hidden by its marker — the #1 phase-portrait failure.
- §2.3 Bidirectional ports between two boxes colliding → split into
  parallel arrows with xshift.
- §2.4 Third arrow crossing a channel between two boxes.
- §2.5 Notes beside a stack of boxes clipping into the boxes
  (`anchor=center` footgun).
- §2.6 Dashed separator crossed by arrows or labels.
- §2.7 `minimum width` is a minimum, not a cap — use `text width`
  for consistent stacked-box sizing. (**Hit twice** — lecture-shape
  fig7 on 2026-04-10 and tutorial-metrip-examples fig13 on
  2026-04-10.)
- §2.8 pgfplots `\foreach \var in ... \addplot[\var, ...]` —
  compile-blocking macro expansion bug. Fix: unroll the loop.
- §2.9 3D axes and cross-product vectors projecting into the same
  screen direction (label fusion).
- §2.10 Labels inside dashed/shaded enclosure struck through by
  interior content.
- §2.11 Arrow paths crossing through other labels or boxes.

### Checklist

12-item review checklist in §3, scanned in order. Stop at first
"yes" and fix before moving on — fixes change what other issues
look like.

### Snippets

All copy-paste code patterns moved to `references/snippets.md` for
on-demand loading; the SKILL.md body points at it.

### Pitfalls (§5)

- Custom macros must be copied into the standalone preamble.
- pgfplots compat mismatch between standalone and main document.
- `\eqref` / `\ref` / `\cref` use placeholders in standalone only.
- Sync drift between standalone and main file — diff before
  declaring victory.
- Subagents may be sandbox-blocked from running `pdflatex`; driver
  must re-render after editing.
- `text width` vs `minimum width` for stacked boxes (from §2.7).
