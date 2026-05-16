from __future__ import annotations
from typing import List, Optional
from config.models import PipelineConfig
from core.session import Session, StageStatus


def _stage_index(session: Session, stage_id: str) -> int:
    for i, s in enumerate(session.stages):
        if s.stage_id == stage_id:
            return i
    raise ValueError(f"Stage {stage_id!r} not found in session")


def current_stage_index(session: Session) -> int:
    return _stage_index(session, session.current_stage_id)


def advance_stage(session: Session, pipeline: PipelineConfig) -> bool:
    """Mark current stage done and activate the next one. Returns False if already on last stage."""
    idx = current_stage_index(session)
    session.stages[idx].status = "done"

    next_idx = idx + 1
    if next_idx >= len(session.stages):
        session.save()
        return False

    session.stages[next_idx].status = "active"
    session.current_stage_id = session.stages[next_idx].stage_id
    session.save()
    return True


def revert_stage(session: Session, pipeline: PipelineConfig) -> bool:
    """Mark current stage pending and reactivate the previous one. Returns False if already on first stage."""
    idx = current_stage_index(session)
    if idx == 0:
        return False

    session.stages[idx].status = "pending"
    for action in session.stages[idx].actions:
        action.status = "pending"
        action.output = None

    prev_idx = idx - 1
    session.stages[prev_idx].status = "active"
    session.current_stage_id = session.stages[prev_idx].stage_id

    for action in session.stages[prev_idx].actions:
        action.status = "pending"
        action.output = None

    session.save()
    return True


def skip_stage(session: Session, pipeline: PipelineConfig) -> bool:
    """Mark current stage skipped and activate the next one. Returns False if already on last stage."""
    idx = current_stage_index(session)
    session.stages[idx].status = "skipped"
    for action in session.stages[idx].actions:
        action.status = "skipped"

    next_idx = idx + 1
    if next_idx >= len(session.stages):
        session.save()
        return False

    session.stages[next_idx].status = "active"
    session.current_stage_id = session.stages[next_idx].stage_id
    session.save()
    return True


def stage_is_complete(session: Session) -> bool:
    """True if all actions in the current stage are done or skipped."""
    stage = session.get_stage(session.current_stage_id)
    if stage is None:
        return False
    return all(a.status in ("done", "skipped") for a in stage.actions)


def pipeline_is_complete(session: Session) -> bool:
    return all(s.status in ("done", "skipped") for s in session.stages)
