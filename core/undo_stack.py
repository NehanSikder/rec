from __future__ import annotations
from typing import Dict, List, Literal

from core.session import Session
from core.state_machine import revert_stage

EntryType = Literal["action_done", "stage_advanced", "stage_skipped"]


def _push(session: Session, entry: Dict) -> None:
    session.history.append(entry)
    session.save()


def record_action_done(session: Session, stage_id: str, action_id: str) -> None:
    _push(session, {
        "type": "action_done",
        "stage_id": stage_id,
        "action_id": action_id,
    })


def record_stage_advanced(session: Session, from_stage_id: str, to_stage_id: str) -> None:
    _push(session, {
        "type": "stage_advanced",
        "from_stage_id": from_stage_id,
        "to_stage_id": to_stage_id,
    })


def record_stage_skipped(session: Session, stage_id: str) -> None:
    _push(session, {
        "type": "stage_skipped",
        "stage_id": stage_id,
    })


def can_undo(session: Session) -> bool:
    return len(session.history) > 0


def undo(session: Session, pipeline) -> bool:
    """Undo the last recorded operation. Returns False if nothing to undo."""
    if not session.history:
        return False

    entry = session.history.pop()
    entry_type = entry["type"]

    if entry_type == "action_done":
        stage = session.get_stage(entry["stage_id"])
        if stage:
            action = next((a for a in stage.actions if a.action_id == entry["action_id"]), None)
            if action:
                action.status = "pending"
                action.output = None

    elif entry_type in ("stage_advanced", "stage_skipped"):
        revert_stage(session, pipeline)
        if session.history and session.history[-1].get("type") == "stage_advanced":
            pass

    session.save()
    return True
