"""
Typed workflow schema shared by the orchestrator and callers.

The orchestrator can still accept legacy list-based plans, but normalizing them
into these dataclasses gives us a stricter contract between the planner and the
executor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_int_list(values: Any) -> List[int]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return []

    result: List[int] = []
    for value in values:
        try:
            item = int(value)
        except (TypeError, ValueError):
            continue
        if item not in result:
            result.append(item)
    return result


def _coerce_str_list(values: Any) -> List[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return []
    return [str(value) for value in values]


@dataclass
class WorkflowStep:
    """A single executable step in a workflow plan."""

    step_id: int
    name: str
    type: str = "task"
    agent: str = "task"
    depends_on: List[int] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_outputs: List[str] = field(default_factory=list)
    error_handling: str = "retry"
    timeout_seconds: int = 30
    parallel_group: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], fallback_step_id: int) -> "WorkflowStep":
        payload_dict = dict(payload)
        step_id = _coerce_int(payload_dict.get("step_id"), fallback_step_id)
        name = str(payload_dict.get("name", f"Step {step_id}"))
        inputs = payload_dict.get("inputs")
        metadata = payload_dict.get("metadata")
        parallel_group_value = payload_dict.get("parallel_group")
        parallel_group = None
        if parallel_group_value is not None:
            group_id = _coerce_int(parallel_group_value, -1)
            if group_id >= 0:
                parallel_group = group_id
        return cls(
            step_id=step_id,
            name=name,
            type=str(payload_dict.get("type", "task")),
            agent=str(payload_dict.get("agent", "task")),
            depends_on=_coerce_int_list(payload_dict.get("depends_on", [])),
            inputs=dict(inputs) if isinstance(inputs, Mapping) else {},
            expected_outputs=_coerce_str_list(payload_dict.get("expected_outputs", [])),
            error_handling=str(payload_dict.get("error_handling", "retry")),
            timeout_seconds=max(1, _coerce_int(payload_dict.get("timeout_seconds"), 30)),
            parallel_group=parallel_group,
            metadata=dict(metadata) if isinstance(metadata, Mapping) else {},
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "step_id": self.step_id,
            "name": self.name,
            "type": self.type,
            "agent": self.agent,
            "depends_on": list(self.depends_on),
            "inputs": dict(self.inputs),
            "expected_outputs": list(self.expected_outputs),
            "error_handling": self.error_handling,
            "timeout_seconds": self.timeout_seconds,
        }
        if self.parallel_group is not None:
            payload["parallel_group"] = self.parallel_group
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


@dataclass
class WorkflowPlan:
    """Normalized workflow plan returned by the LLM planner."""

    goal: str
    total_steps: int
    steps: List[WorkflowStep] = field(default_factory=list)
    parallel_groups: List[List[int]] = field(default_factory=list)
    estimated_duration_seconds: int = 0
    schema_version: str = "workflow-plan/v1"
    metadata: Dict[str, Any] = field(default_factory=dict)
    normalization_warnings: List[str] = field(default_factory=list)

    @classmethod
    def from_payload(
        cls,
        payload: Any,
        default_goal: str = "",
    ) -> "WorkflowPlan":
        if isinstance(payload, WorkflowPlan):
            return payload
        if isinstance(payload, list):
            payload = {"steps": payload}
        if not isinstance(payload, Mapping):
            raise TypeError("Workflow plan payload must be a mapping, list, or WorkflowPlan")

        payload_dict = dict(payload)
        warnings: List[str] = []
        raw_steps = payload_dict.get("steps", [])
        steps: List[WorkflowStep] = []
        seen_ids = set()

        if not isinstance(raw_steps, Sequence) or isinstance(raw_steps, (str, bytes)):
            raw_steps = []

        for fallback_step_id, raw_step in enumerate(raw_steps):
            if not isinstance(raw_step, Mapping):
                warnings.append(f"Skipped non-mapping step at position {fallback_step_id}")
                continue

            step = WorkflowStep.from_payload(raw_step, fallback_step_id=fallback_step_id)
            if step.step_id in seen_ids:
                warnings.append(
                    f"Duplicate step_id {step.step_id} detected; reassigned to {fallback_step_id}"
                )
                step.step_id = fallback_step_id
            seen_ids.add(step.step_id)
            steps.append(step)

        valid_step_ids = {step.step_id for step in steps}
        parallel_groups: List[List[int]] = []
        raw_groups = payload_dict.get("parallel_groups", [])
        if isinstance(raw_groups, Sequence) and not isinstance(raw_groups, (str, bytes)):
            for raw_group in raw_groups:
                group_ids = _coerce_int_list(raw_group)
                normalized_group = [step_id for step_id in group_ids if step_id in valid_step_ids]
                if len(normalized_group) > 1:
                    parallel_groups.append(normalized_group)

        total_steps = _coerce_int(payload_dict.get("total_steps"), len(steps))
        if total_steps != len(steps):
            warnings.append(
                f"total_steps ({total_steps}) did not match actual steps ({len(steps)}); normalised"
            )
            total_steps = len(steps)

        metadata = payload_dict.get("metadata")

        return cls(
            goal=str(payload_dict.get("goal", default_goal)),
            total_steps=total_steps,
            steps=steps,
            parallel_groups=parallel_groups,
            estimated_duration_seconds=max(
                0, _coerce_int(payload_dict.get("estimated_duration_seconds"), 0)
            ),
            schema_version=str(payload_dict.get("schema_version", "workflow-plan/v1")),
            metadata=dict(metadata) if isinstance(metadata, Mapping) else {},
            normalization_warnings=warnings,
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "goal": self.goal,
            "total_steps": self.total_steps,
            "steps": [step.to_dict() for step in self.steps],
            "parallel_groups": [list(group) for group in self.parallel_groups],
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "schema_version": self.schema_version,
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        if self.normalization_warnings:
            payload["normalization_warnings"] = list(self.normalization_warnings)
        return payload

    def to_legacy_steps(self) -> List[Dict[str, Any]]:
        return [step.to_dict() for step in self.steps]

    def step_map(self) -> Dict[int, WorkflowStep]:
        return {step.step_id: step for step in self.steps}

    def ready_batches(
        self,
        completed_step_ids: Sequence[int],
        pending_step_ids: Optional[Sequence[int]] = None,
    ) -> List[List[WorkflowStep]]:
        """Group ready steps into explicit parallel batches when possible."""
        completed = set(completed_step_ids)
        pending_ids = set(pending_step_ids) if pending_step_ids is not None else None
        if pending_step_ids is None:
            pending = self.step_map()
        else:
            pending = {
                step.step_id: step
                for step in self.steps
                if pending_ids is not None and step.step_id in pending_ids
            }
        ready = [
            step
            for step in pending.values()
            if all(dep in completed for dep in step.depends_on)
        ]
        if not ready:
            return []

        ready_ids = {step.step_id for step in ready}
        grouped_ids = set()
        batches: List[List[WorkflowStep]] = []

        for group in self.parallel_groups:
            batch = [pending[step_id] for step_id in group if step_id in ready_ids]
            if len(batch) > 1:
                batches.append(batch)
                grouped_ids.update(step.step_id for step in batch)

        remaining = [step for step in ready if step.step_id not in grouped_ids]
        if remaining:
            batches.append(remaining)

        return batches
