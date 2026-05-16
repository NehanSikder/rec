from __future__ import annotations
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional
from config.models import Action
from core.session import ActionState, Session


def _resolve_template(template: str, session: Session) -> str:
    session_dir = Path.home() / ".rec" / "sessions" / session.id
    replacements = {
        "{session.id}": session.id,
        "{session.title}": session.title,
        "{session.dir}": str(session_dir),
    }
    result = template
    for key, value in replacements.items():
        result = result.replace(key, value)
    return result


def run_action(
    action: Action,
    action_state: ActionState,
    session: Session,
    on_output: Optional[Callable[[str], None]] = None,
) -> bool:
    """Execute an action. Returns True on success, False on failure."""
    action_state.status = "running"
    session.save()

    try:
        if action.type == "manual":
            action_state.status = "done"
            session.save()
            return True

        if action.type == "shell":
            if not action.command:
                raise ValueError(f"Action {action.id!r} has no command")
            cmd = _resolve_template(action.command, session)
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            )
            output = result.stdout + result.stderr
            action_state.output = output.strip() or None
            if on_output and output:
                on_output(output)
            if result.returncode != 0:
                action_state.status = "failed"
                session.save()
                return False

        elif action.type == "open":
            if not action.path:
                raise ValueError(f"Action {action.id!r} has no path")
            path = _resolve_template(action.path, session)
            subprocess.run(["open", path], check=True)

        elif action.type == "script":
            if not action.path:
                raise ValueError(f"Action {action.id!r} has no path")
            path = _resolve_template(action.path, session)
            result = subprocess.run(
                [sys.executable, path], capture_output=True, text=True
            )
            output = result.stdout + result.stderr
            action_state.output = output.strip() or None
            if on_output and output:
                on_output(output)
            if result.returncode != 0:
                action_state.status = "failed"
                session.save()
                return False

        elif action.type == "prompt":
            # Prompt type is handled by the UI layer — runner treats it as done
            action_state.status = "done"
            session.save()
            return True

        action_state.status = "done"
        session.save()
        return True

    except Exception as e:
        action_state.status = "failed"
        action_state.output = str(e)
        session.save()
        return False
