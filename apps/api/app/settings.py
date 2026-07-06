from __future__ import annotations

from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = API_ROOT.parents[1]
DATA_DIR = REPO_ROOT / "data"
MODEL_DIR = DATA_DIR / "models"
OUTPUT_DIR = DATA_DIR / "outputs"
REGISTRY_PATH = DATA_DIR / "models.json"
