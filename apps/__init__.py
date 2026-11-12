"""Dynamic loader shims for hyphenated Skeleton Crew app directories (`apps/repo-necromancer` & `apps/med-evidence-checker`)."""

from __future__ import annotations

import importlib.util
import pathlib
from types import ModuleType


_APPS_DIR = pathlib.Path(__file__).resolve().parent


def _load_module(module_name: str, file_path: pathlib.Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


repo_necromancer_adapter = _load_module(
    "repo_necromancer_adapter", _APPS_DIR / "repo-necromancer" / "adapter.py"
)
repo_necromancer_presets = _load_module(
    "repo_necromancer_presets", _APPS_DIR / "repo-necromancer" / "presets.py"
)

med_evidence_adapter = _load_module(
    "med_evidence_adapter", _APPS_DIR / "med-evidence-checker" / "adapter.py"
)
med_evidence_presets = _load_module(
    "med_evidence_presets", _APPS_DIR / "med-evidence-checker" / "presets.py"
)
