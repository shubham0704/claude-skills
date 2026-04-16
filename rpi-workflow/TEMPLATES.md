# RPI Templates

## Research Doc Template

```markdown
---
date: YYYY-MM-DDTHH:MM:SSZ
researcher: claude
topic: "short description"
tags: [research, component-a]
status: draft
---

## Research Question
What you are trying to learn/confirm.

## Context & Sources
- `path/to/file.py:line` — description
- Related docs/tickets

## Summary (max 8 bullets)
- `path:line` — key behavior/fact

## Detailed Findings
### Component/Area 1
- `path:line` — what exists and how it works

## Patterns & Conventions
- `path:line` — pattern to follow

## Open Questions
- Items needing further confirmation
```

## Plan Template

```markdown
# PLAN:<repo>:<task>

**Status:** AWAITING_FEEDBACK
**Created:** YYYY-MM-DDTHH:MM:SSZ
**Author:** Claude

## Goal
1-2 sentences.

## Key Files
- `path/to/file.py:line` — description

## Problem
What's broken or missing.

## Proposed Solution
### Phase 1: [name]
- `path/to/file.ext` — summary of edit
- Success criteria

### Phase 2: [name]
- ...

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Risks
1. Risk + mitigation

## Questions for Review
1. Question for Codex
```

## Implementation Report Template

```markdown
# IMPL:<repo>:<task>

**Status:** COMPLETE
**Completed:** YYYY-MM-DDTHH:MM:SSZ

## Changes Made
### Phase 1: [name]
- `path/to/file.ext:line` — what changed
- Deviations from plan: [none / description]

## Test Results
- [x] Criterion 1 — passed
- [ ] Criterion 2 — status

## Remaining Work
- Items deferred or discovered during implementation
```
