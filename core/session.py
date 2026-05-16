from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

SESSIONS_DIR = Path.home() / ".rec" / "sessions"

ActionStatus = Literal["pending", "running", "done", "failed", "skipped"]
StageStatus = Literal["pending", "active", "done", "skipped"]


@dataclass
class ActionState:
    action_id: str
    status: ActionStatus = "pending"
    output: Optional[str] = None


@dataclass
class StageState:
    stage_id: str
    status: StageStatus = "pending"
    actions: List[ActionState] = field(default_factory=list)


@dataclass
class Session:
    id: str
    title: str
    created_at: str
    current_stage_id: str
    stages: List[StageState]
    history: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "current_stage_id": self.current_stage_id,
            "stages": [
                {
                    "stage_id": s.stage_id,
                    "status": s.status,
                    "actions": [
                        {"action_id": a.action_id, "status": a.status, "output": a.output}
                        for a in s.actions
                    ],
                }
                for s in self.stages
            ],
            "history": self.history,
        }

    @staticmethod
    def from_dict(data: Dict) -> Session:
        stages = [
            StageState(
                stage_id=s["stage_id"],
                status=s["status"],
                actions=[
                    ActionState(
                        action_id=a["action_id"],
                        status=a["status"],
                        output=a.get("output"),
                    )
                    for a in s["actions"]
                ],
            )
            for s in data["stages"]
        ]
        return Session(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            current_stage_id=data["current_stage_id"],
            stages=stages,
            history=data.get("history", []),
        )

    def save(self) -> None:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        path = SESSIONS_DIR / f"{self.id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2))

    def get_stage(self, stage_id: str) -> Optional[StageState]:
        return next((s for s in self.stages if s.stage_id == stage_id), None)

    def get_action(self, stage_id: str, action_id: str) -> Optional[ActionState]:
        stage = self.get_stage(stage_id)
        if stage is None:
            return None
        return next((a for a in stage.actions if a.action_id == action_id), None)


def create_session(title: str, pipeline_stage_ids: List[str], pipeline_action_ids: Dict[str, List[str]]) -> Session:
    first_stage = pipeline_stage_ids[0]
    stages = []
    for stage_id in pipeline_stage_ids:
        status: StageStatus = "active" if stage_id == first_stage else "pending"
        actions = [ActionState(action_id=a) for a in pipeline_action_ids[stage_id]]
        stages.append(StageState(stage_id=stage_id, status=status, actions=actions))

    session = Session(
        id=str(uuid.uuid4()),
        title=title,
        created_at=datetime.now().isoformat(),
        current_stage_id=first_stage,
        stages=stages,
    )
    session.save()
    return session


def load_session(session_id: str) -> Session:
    path = SESSIONS_DIR / f"{session_id}.json"
    data = json.loads(path.read_text())
    return Session.from_dict(data)


def delete_session(session_id: str) -> None:
    path = SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        path.unlink()


def list_sessions() -> List[Dict]:
    if not SESSIONS_DIR.exists():
        return []
    sessions = []
    for path in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = json.loads(path.read_text())
        sessions.append({"id": data["id"], "title": data["title"], "created_at": data["created_at"]})
    return sessions
