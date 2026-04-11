---
name: _template
description: "One-line WHAT this skill does + two to three sentences on WHEN to trigger it. Be specific about contexts and use a pushy tone — skills undertrigger by default. Mention related phrases the user might say even when they don't name the skill explicitly. Replace this with your own description."
version: 0.1.0
---

# _template

Replace this with a 1–3 sentence summary of what this skill helps
Claude do. Keep it tight — the full reasoning belongs below, not
here.

## 1. Workflow

Start with the end-to-end workflow. Imperative style. Short
sections. Give the reader (Claude) enough structure that they can
scan for the step they need.

### 1.1 Setup (if any)

### 1.2 Main loop

### 1.3 Hand-off / completion criteria

## 2. Core content

The bulk of the skill. For review-style skills, this is typically a
numbered list of failure modes and canonical fixes. For building-
style skills, it's usually a sequence of phases with decision
criteria. For writing-style skills, it's sections + patterns.

Use sub-sections freely. Keep any single section short enough to
scan.

## 3. Checklist / decision points

If this skill has a checklist, rubric, or review order, put it here
so it's findable. Otherwise delete this section.

## 4. Bundled resources

- `references/` — docs loaded on-demand when the body points at them
- `scripts/` — executable utilities (if any)
- `assets/` — templates/fixtures used in output

If a section of this skill is long, move it to `references/` and
point here with a sentence like "See `references/snippets.md` for
copy-paste patterns."

## 5. Pitfalls

List of things to watch out for. One bullet each, imperative mood.

---

## Notes for skill authors

When creating a skill from this template:

1. Pick a kebab-case directory name. Rename the directory, not just
   the frontmatter.
2. Fill in `name:` and `description:` in the frontmatter. Make the
   description pushy — mention specific trigger contexts beyond the
   obvious ones, including related phrases the user might say.
3. Start at `version: 0.1.0` (initial draft) or `1.0.0` (first
   stable release you're willing to recommend to others).
4. Keep this file under ~500 lines. Push overflow into
   `references/`, `scripts/`, or `assets/`.
5. Create a `CHANGELOG.md` alongside this file (see `_template/`)
   and log your first entry.
6. Delete this "Notes for skill authors" section from your final
   skill.
