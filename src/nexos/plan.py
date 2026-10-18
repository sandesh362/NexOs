from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Step:
    step_id: str
    tool: str
    dependencies: tuple[str, ...] = ()


TOOLS = frozenset({"manifest.inspect", "report.create", "report.verify"})


def diagnosis_plan() -> tuple[Step, ...]:
    return (
        Step("inspect", "manifest.inspect"),
        Step("report", "report.create", ("inspect",)),
        Step("verify", "report.verify", ("report",)),
    )


def validate_plan(steps: tuple[Step, ...]) -> list[dict]:
    if not steps or len(steps) > 12:
        raise ValueError("A plan must contain between one and twelve steps")
    by_id = {step.step_id: step for step in steps}
    if len(by_id) != len(steps):
        raise ValueError("Step identifiers must be unique")
    for step in steps:
        if step.tool not in TOOLS:
            raise ValueError("Plan requested an unregistered tool")
        if any(dep not in by_id for dep in step.dependencies):
            raise ValueError("Plan contains an unknown dependency")
    completed: set[str] = set()
    while len(completed) < len(steps):
        ready = {step.step_id for step in steps if step.step_id not in completed and set(step.dependencies) <= completed}
        if not ready:
            raise ValueError("Plan contains a dependency cycle")
        completed.update(ready)
    return [asdict(step) for step in steps]
