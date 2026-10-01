# Learning flow and recall

Use when planning a new explanation or repairing a conceptual jump. Apply the
parts that diagnose the actual difficulty, not an obligatory checklist per slide.

## Track what the audience can use

Keep a small authoring ledger for consequential concepts, not every index:

| Concept or symbol | Prerequisites | First concrete explanation | First use | Recall needed |
| --- | --- | --- | --- | --- |
| Object, law, operation, or decision | What must already make sense | Example or interpretation | Where reasoning relies on it | Where it returns after an absence or role change |

Distinguish mentioned, defined, demonstrated, and usable. A legend defines a name;
a worked example establishes how to use it. Do not count future slides, hidden
speaker notes, or the author's expertise as knowledge the audience already has.
For a live talk, essential spoken bridges may carry explanation; record them in
the narration. A standalone deck needs those bridges visible.

Test the ledger locally: at the first use, can the intended reader explain why
the quantity is needed, where it comes from, and what it lets us compute?
Abbreviations and domain terms need an ordinary-language anchor when unfamiliar.
Do not require a miniature textbook for an expert audience.

## Build dependency-led sections

Use a sequence such as need -> concrete case -> operation -> notation -> use.
Adapt it rather than reproducing those five labels on screen. For example, teach
the actual scalar conditions before naming the vector of their residuals. When
the reader reaches the compact map, its inputs, outputs, and role are familiar.

Separate three orders explicitly in authoring notes when they differ:

- Physical/dependency order: what determines or constrains what.
- Execution order: what the program actually computes, stores, repeats, or solves together.
- Teaching order: what this audience must understand first.

An algorithm is a navigation aid, not sufficient pedagogy. A function call can
hide the hardest idea in the section. Teach that operation and link back to its
stable step ID; do not re-explain a standard optimizer while its loss is opaque.
For coupled equations, a sequence of explanations need not imply a sequence of
independent assignments. State what is held fixed and what is solved jointly.

## Repair adjacent transitions

Write the final thought of slide A and the first thought of slide B consecutively.
Ask whether B uses a new object, changes the goal, changes abstraction level, or
changes what is known. Find the first missing dependency, not just the busiest page.

| Symptom | Likely missing bridge | Smallest useful repair |
| --- | --- | --- |
| "Why do we need this variable now?" | Its downstream use | Name the quantity needed next, then derive the new variable's role |
| "What does this function do?" | Concrete meaning behind shorthand | Show one explicit input-output calculation, then give it the compact name |
| "Did we measure or learn this?" | Information provenance or phase change | State what is available here and what is computed from it |
| "Why solve again after training?" | Fitting versus execution | Hold parameters fixed and trace a new input through the trained model |
| "I forgot the circuit/example/question" | Retrieval after an absence | Reuse the same small example, question, or geometry at the point of need |
| "Does this property prove the result?" | Boundary between properties and evidence | State precisely what follows and what still needs testing |

The examples diagnose patterns; they are not required domain-specific slides.
If explanation order is wrong, reorder. If a prerequisite is genuinely new, add
space for it. Do not append another summary to avoid fixing the first gap.

## Retrieve without restarting

Teach foundations carefully once. At a later dependency, recall the smallest
anchor that restores their use: a labeled thumbnail, one familiar equation,
an unchanged question, or a short example. Keep symbols and semantic colors stable.
Let the audience recover what matters before introducing the next abstraction.

Trigger recall by dependency, absence, or changed role, not a fixed page interval.
Do not put the entire circuit, algorithm, glossary, and formulation on every slide.
Each repeat must earn its space by making the next operation easier to understand.

## Revisit a formulation without re-teaching it

For a control walkthrough, the opening may establish the decision and objective;
after sensing, explain initialization and available information; after dynamics,
explain how a choice produces a trajectory; after coupling, explain admissibility;
after rollout, show how that trajectory is scored. Close with the complete problem.
These are possible milestones, not a required block taxonomy or number of slides.

Do not start with an unreadable full formulation merely to satisfy "overview
first." Start with the question and readable contract; reveal the formal parts
when their roles can be understood. Preserve conditions in the source and make
the material ones available before claiming the full formulation is explained.

## Compress by removing unnecessary work for the reader

Before expanding the deck, decide whether the repair is a reorder, replacement,
brief recall, deletion, or genuine new teaching step. Combine slides that repeat
the same reasoning; separate slides that require multiple unfamiliar dependencies.
Move secondary derivations to backup, not assumptions needed for the main claim.
Do not compress by shrinking text or replacing an explanation with more notation.

Read the narration continuously, ignoring page breaks and step labels. Every
paragraph should consume established understanding and leave something useful for
the next. Then rehearse against the available time. A coherent long walkthrough
does not automatically become a coherent short research talk by speaking faster.
