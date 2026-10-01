# Appendix Evidence Passes

Use this reference when auditing appendices, supplements, benchmark
details, result tables, figure placement, or reproduction-oriented
sections. The goal is to make appendix evidence easy to enter, easy to
trust, and easy to connect back to the main paper.

## Core Principle

An appendix is not a storage area. It should answer a local reader
question planted by the main text or by the appendix roadmap.

For each appendix block, write:

```text
Reader enters with:
This block answers:
Evidence provided:
Reproduction value:
Main-text claim linked:
Smallest fix:
```

## Passes

### Reader-Entry Pass

Check whether the first paragraph gives enough plain-language context
before protocol details, acronyms, symbols, or tables appear.

Flag when:
- a benchmark begins with apparatus details before saying what the
  system is;
- domain shorthand appears before a reader can visualize the setting;
- a result table appears before the protocol and metric are locally
  explained.

### Appendix Roadmap Pass

Check whether the appendix opening tells the reader what each appendix
block is for and where to look for proofs, protocols, diagnostics,
ablations, and extra results.

### Co-Location Pass

Keep protocol, schematic, companion result, and diagnostics near one
another when they answer the same reader question.

Good local cluster:

```text
benchmark context -> protocol -> figure/table -> interpretation ->
reproduction details
```

Flag a figure or table as **stray evidence** when it is far from the
text that explains it, not cross-referenced, or not interpreted after
appearing.

### Cold-Start Context Pass

Assume the reader opens the appendix directly from a main-text
reference. Check whether the section explains enough local context to
parse its first table, figure, or equation.

Typical debts:
- unexplained protocol names such as matched/full, q-only/full-state,
  nominal/reconfigured, teacher-forced/rollout;
- unexplained domain terms or acronyms;
- a setting name appears before the data source, task, or metric.

### Formal-Block Reproduction Pass

For equations, algorithms, and notation in appendices, require both
local scope and reproduction value.

Ask:
- What indices range over: time, subsystem, joint, cell, line, edge,
  seed, rollout horizon, or candidate?
- Is this equation needed to reproduce the experiment, interpret a
  metric, or support a claim?
- Does prose before the block create the need for it?
- Does prose after the block say how it is used?

### Table-Interpretability Pass

For every table, check:
- what is being compared;
- what protocol generated the rows;
- what units and scaling are used;
- whether lower or higher is better;
- whether the best values are highlighted consistently;
- what the reader should conclude.

Negative results may stay when they teach a diagnostic lesson. Remove,
move, or compress results that are neither claim-bearing nor
reproduction-bearing.

### Caption-Parse Pass

A caption should let a reader understand the object without re-reading
the whole section.

Check:
- Does it state the punchline, not only the contents?
- Does it define non-obvious protocol labels and units?
- Does it avoid jargon-first wording?
- Does it avoid claiming more than the figure/table shows?

### Main-Text Linkage Pass

Appendix evidence should be reachable from the main paper.

Flag:
- a main-text claim supported only by appendix material without a
  short main-text summary;
- appendix-only terminology that becomes necessary for understanding
  main results;
- a figure/table that is referenced by number but not framed by a
  reader question.

### Benchmark-Role Pass

Each benchmark or appendix experiment should have a declared role:
clean scaling, real-world validation, partial sensing, topology
change, typed heterogeneous blocks, ablation, diagnostic, or
reproduction detail.

If the role is missing, write one sentence before details:

```text
This benchmark isolates ...
```

Then make later tables and captions reuse that role.

### Claim-Boundary Pass

Scope experimental evidence positively. Avoid defensive standalone
disclaimers. Prefer a claim sentence that says exactly what was
validated and what remains outside that validation.

Example shape:

```text
The logged experiment validates consequence prediction and
objective-conditioned ranking on real telemetry; closed-loop command
execution is studied separately.
```

## Output Labels

Use these manual labels alongside the CLI risk labels:

- **ENTRY DEBT**: the section starts before the reader can visualize
  the setting.
- **CO-LOCATION DEBT**: figure, table, protocol, and interpretation
  are split apart.
- **REPRODUCTION GAP**: a detail is interesting but not sufficient for
  reproduction, or a reproducing reader still lacks a required fact.
- **CAPTION DEBT**: caption names the object but not the takeaway.
- **STRAY EVIDENCE**: evidence is unreferenced, uninterpreted, or not
  claim-bearing.
- **APPENDIX CLAIM LEAK**: appendix evidence is carrying a main-text
  claim without a main-text summary.
- **ROLE DRIFT**: benchmark details no longer serve the declared
  benchmark role.

## Edit Discipline

- Prefer moving evidence near the explanatory text over adding more
  cross-references.
- Add one reader-entry sentence before adding more notation.
- Do not keep a section only because work was done; keep it because it
  supports a claim, a diagnostic lesson, or reproduction.
- Do not overcompress away setup that prevents reader confusion.
- After moving appendix material, compile and scan for undefined refs,
  duplicate labels, and stale roadmap text.
