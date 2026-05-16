from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Literal, Optional

ActionType = Literal["shell", "open", "script", "manual", "prompt"]


@dataclass
class Action:
    id: str
    label: str
    type: ActionType
    command: Optional[str] = None
    path: Optional[str] = None
    prompt_label: Optional[str] = None


@dataclass
class Stage:
    id: str
    label: str
    description: str
    actions: List[Action] = field(default_factory=list)


@dataclass
class PipelineConfig:
    stages: List[Stage]
