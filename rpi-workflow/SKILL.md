---
name: rpi-workflow
description: "Research-Plan-Implement workflow with Codex peer review. Use when the user says /rpi, asks to start a research-plan-implement cycle, wants Codex review on a plan, or needs to create research docs, plans, or implementation reports following the RPI protocol."
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, Task, TaskCreate, TaskUpdate, TaskList, EnterPlanMode, ExitPlanMode, AskUserQuestion
---

# RPI Workflow: Research -> Plan -> Implement

A structured workflow for complex engineering tasks with Codex architectural review.

## When to Invoke

- User says `/rpi` or "start RPI"
- User wants structured research before implementation
- User wants Codex to review a plan
- User needs to create research docs or implementation plans

## File Structure

All artifacts go in `docs/` at the project root:

```
docs/
├── research/
│   └── YYYY-MM-DD-topic.md        # Research findings
└── plans/
    ├── PLAN-<repo>-<task>.md      # Claude creates
    ├── FEEDBACK-<repo>-<task>.md  # Codex creates
    ├── IMPL-<repo>-<task>.md      # Claude creates after implementation
    └── VALIDATION-<repo>-<task>.md # Codex creates (optional)
```

## Workflow Steps

### Step 1: Research Phase

Launch parallel Explore agents to gather codebase understanding:

```
Task(subagent_type="Explore", prompt="Research how X works...")
Task(subagent_type="Explore", prompt="Research how Y connects to Z...")
```

Save findings to `docs/research/YYYY-MM-DD-topic.md` using the research template. For the template structure, see [TEMPLATES.md](TEMPLATES.md).

### Step 2: Plan Phase

Create `docs/plans/PLAN-<repo>-<task>.md` with:
- Goal (1-2 sentences)
- Key Files (`path:line` references)
- Problem (what's broken/missing)
- Proposed Solution (phased, with file-level changes)
- Success Criteria (checkboxes)
- Risks (numbered)
- Questions for Review (for Codex)

### Step 3: Codex Review

Run from the **project root**:

```bash
codex exec --skip-git-repo-check "Read docs/plans/PLAN-<repo>-<task>.md and provide architectural feedback. Review the proposed solution, identify risks, suggest improvements. Write your feedback to docs/plans/FEEDBACK-<repo>-<task>.md"
```

**Notes:**
- Always use `--skip-git-repo-check` for non-git repos
- No `--quiet` flag exists
- Codex writes feedback autonomously to the FEEDBACK file

### Step 4: Read & Incorporate Feedback

Read `docs/plans/FEEDBACK-<repo>-<task>.md` and present key findings to the user:
- Executive assessment
- Missing edge cases
- Better abstractions suggested
- Risks not identified
- Phase reordering suggestions
- Actionable recommendations

### Step 5: Implement

Make the changes. Create `docs/plans/IMPL-<repo>-<task>.md` documenting:
- What was actually changed (with `path:line` refs)
- Deviations from plan and why
- Test results
- Remaining work

### Step 6: Validate (Optional)

```bash
codex exec --skip-git-repo-check "Read docs/plans/IMPL-<repo>-<task>.md and validate the implementation. Check if success criteria are met, identify any issues. Write your validation to docs/plans/VALIDATION-<repo>-<task>.md"
```

## Guidelines

- **Research first**: Never plan without understanding the codebase
- **Parallel agents**: Use multiple Explore agents simultaneously
- **Compact findings**: Use `file:line` references, not full code dumps
- **Questions for Codex**: Always include 3-5 specific architectural questions
- **Parity checks**: Before deleting old code, run side-by-side comparisons
- **Phase boundaries**: Each phase should be independently mergeable
