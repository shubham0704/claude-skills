# DAG JSON Shape

Use this reference when a user asks for a saved or machine-checkable DAG artifact.

## Required Top-Level Shape

```json
{
  "schema_version": "plan-dag.v1",
  "goal": "Short outcome statement",
  "constraints": ["Hard rule"],
  "tasks": [
    {
      "id": "T1",
      "title": "Add workflow schema",
      "type": "code",
      "owner": "local",
      "write_scope": ["api/schemas/ai-app/ai-app-manifest.v1.json"],
      "depends_on": [],
      "parallel_with": ["T2"],
      "risk": "medium",
      "validation": ["schema validation passes"],
      "done_when": ["manifest accepts workflow_surfaces"]
    }
  ],
  "waves": [
    {
      "id": "W1",
      "objective": "Establish contracts",
      "tasks": ["T1", "T2"],
      "validation_gate": ["contract tests pass"]
    }
  ]
}
```

## Allowed Task Types

- `research`
- `design`
- `code`
- `test`
- `docs`
- `migration`
- `ops`
- `review`

## Allowed Owners

- `local`
- `worker`
- `explorer`
- `human`
- `external`

## Allowed Risk Values

- `low`
- `medium`
- `high`

## ID Rules

- Task IDs should be stable and short: `T1`, `T2`, `API1`, `DB1`.
- Wave IDs should be stable and short: `W0`, `W1`, `W2`.
- Do not reuse IDs.
- Do not encode status in IDs.

## Dependency Rules

- `depends_on` can only reference existing task IDs.
- Dependencies must not create cycles.
- A wave can include a task only if all dependencies are in earlier waves or the same task has no dependencies.
- Tasks in the same wave must not depend on each other.
