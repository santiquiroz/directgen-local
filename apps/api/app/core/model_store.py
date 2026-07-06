from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import uuid5, NAMESPACE_URL


@dataclass(frozen=True)
class InstalledModel:
    id: str
    repo_id: str
    local_path: str
    task: str
    runtime: str
    installed_at: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class ModelStore:
    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path
        self._lock = Lock()

    def list(self) -> list[InstalledModel]:
        return list(self._read().values())

    def get(self, model_id: str) -> InstalledModel:
        models = self._read()
        if model_id not in models:
            raise KeyError(model_id)
        return models[model_id]

    def register(self, *, repo_id: str, local_path: Path, task: str, runtime: str) -> InstalledModel:
        model_id = uuid5(NAMESPACE_URL, f"{repo_id}:{runtime}:{task}").hex
        model = InstalledModel(
            id=model_id,
            repo_id=repo_id,
            local_path=str(local_path),
            task=task,
            runtime=runtime,
            installed_at=datetime.now(UTC).isoformat(),
        )
        with self._lock:
            models = self._read_unlocked()
            models[model.id] = model
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            self.registry_path.write_text(
                json.dumps([item.to_dict() for item in models.values()], indent=2),
                encoding="utf-8",
            )
        return model

    def _read(self) -> dict[str, InstalledModel]:
        with self._lock:
            return self._read_unlocked()

    def _read_unlocked(self) -> dict[str, InstalledModel]:
        if not self.registry_path.exists():
            return {}
        raw = json.loads(self.registry_path.read_text(encoding="utf-8"))
        return {item["id"]: InstalledModel(**item) for item in raw}
