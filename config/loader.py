from __future__ import annotations
from pathlib import Path
import yaml
from config.models import Action, PipelineConfig, Stage

DEFAULT_CONFIG = Path(__file__).parent.parent / "stages.yaml"
USER_CONFIG = Path.home() / ".rec" / "stages.yaml"


def load_pipeline() -> PipelineConfig:
    path = USER_CONFIG if USER_CONFIG.exists() else DEFAULT_CONFIG
    with open(path) as f:
        raw = yaml.safe_load(f)

    stages = [
        Stage(
            id=s["id"],
            label=s["label"],
            description=s["description"],
            actions=[
                Action(
                    id=a["id"],
                    label=a["label"],
                    type=a["type"],
                    command=a.get("command"),
                    path=a.get("path"),
                    prompt_label=a.get("prompt_label"),
                )
                for a in s.get("actions", [])
            ],
        )
        for s in raw["stages"]
    ]
    return PipelineConfig(stages=stages)
