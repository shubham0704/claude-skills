#!/usr/bin/env python3
"""Validate a plan-dag.v1 JSON artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_TASK_TYPES = {"research", "design", "code", "test", "docs", "migration", "ops", "review"}
ALLOWED_OWNERS = {"local", "worker", "explorer", "human", "external"}
ALLOWED_RISKS = {"low", "medium", "high"}


def fail(message: str) -> None:
    print(f"invalid DAG: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def validate(path: Path) -> None:
    data = require_mapping(json.loads(path.read_text(encoding="utf-8")), "root")
    if data.get("schema_version") != "plan-dag.v1":
        fail("schema_version must be plan-dag.v1")

    tasks = require_list(data.get("tasks"), "tasks")
    waves = require_list(data.get("waves"), "waves")
    if not tasks:
        fail("tasks must not be empty")
    if not waves:
        fail("waves must not be empty")

    task_by_id: dict[str, dict[str, Any]] = {}
    for raw_task in tasks:
        task = require_mapping(raw_task, "task")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            fail("each task requires a non-empty string id")
        if task_id in task_by_id:
            fail(f"duplicate task id {task_id!r}")
        task_by_id[task_id] = task

        if task.get("type") not in ALLOWED_TASK_TYPES:
            fail(f"task {task_id}: invalid type {task.get('type')!r}")
        if task.get("owner") not in ALLOWED_OWNERS:
            fail(f"task {task_id}: invalid owner {task.get('owner')!r}")
        if task.get("risk") not in ALLOWED_RISKS:
            fail(f"task {task_id}: invalid risk {task.get('risk')!r}")
        for field in ("write_scope", "depends_on", "validation", "done_when"):
            require_list(task.get(field), f"task {task_id}.{field}")

    for task_id, task in task_by_id.items():
        for dep in task["depends_on"]:
            if dep not in task_by_id:
                fail(f"task {task_id}: unknown dependency {dep!r}")
            if dep == task_id:
                fail(f"task {task_id}: self dependency")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            fail(f"cycle detected at {task_id}")
        visiting.add(task_id)
        for dep in task_by_id[task_id]["depends_on"]:
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in task_by_id:
        visit(task_id)

    assigned: set[str] = set()
    completed: set[str] = set()
    for raw_wave in waves:
        wave = require_mapping(raw_wave, "wave")
        wave_id = wave.get("id")
        if not isinstance(wave_id, str) or not wave_id:
            fail("each wave requires a non-empty string id")
        wave_tasks = require_list(wave.get("tasks"), f"wave {wave_id}.tasks")
        require_list(wave.get("validation_gate"), f"wave {wave_id}.validation_gate")
        wave_set = set()
        for task_id in wave_tasks:
            if task_id not in task_by_id:
                fail(f"wave {wave_id}: unknown task {task_id!r}")
            if task_id in assigned:
                fail(f"task {task_id} appears in multiple waves")
            deps = set(task_by_id[task_id]["depends_on"])
            same_wave_deps = deps & set(wave_tasks)
            if same_wave_deps:
                fail(f"wave {wave_id}: task {task_id} depends on same-wave task(s) {sorted(same_wave_deps)}")
            missing = deps - completed
            if missing:
                fail(f"wave {wave_id}: task {task_id} missing prior dependency/dependencies {sorted(missing)}")
            assigned.add(task_id)
            wave_set.add(task_id)
        completed.update(wave_set)

    missing_from_waves = set(task_by_id) - assigned
    if missing_from_waves:
        fail(f"tasks not assigned to waves: {sorted(missing_from_waves)}")

    print(f"valid DAG: {len(task_by_id)} task(s), {len(waves)} wave(s)")


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: validate_dag.py path/to/dag.json", file=sys.stderr)
        raise SystemExit(2)
    validate(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
