"""MEEP handoff logging for OptiAi.

This module records a minimal simulation handoff configuration so the UI can
show what would be passed to the local MEEP execution pipeline.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from PhotonicsAI.config import PATH


def _log_path() -> Path:
    PATH.build.mkdir(parents=True, exist_ok=True)
    return PATH.build / "meep.log"


def _append_log(lines: list[str]) -> None:
    p = _log_path()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] MEEP integration\n")
        for ln in lines:
            f.write(ln.rstrip("\n") + "\n")


def _build_config_from_session(session: Any) -> dict[str, Any]:
    default_meep_python = PATH.repo / ".meep-env" / "bin" / "python"
    default_meep_script = PATH.repo / "meep_sim" / "mmi_4x4.py"
    default_meep_output = PATH.build / "meep_output_modal"

    meep_python = str(Path(os.getenv("OPTIAI_MEEP_PYTHON", str(default_meep_python))))
    meep_script = str(Path(os.getenv("OPTIAI_MEEP_SCRIPT", str(default_meep_script))))
    meep_output_dir = str(
        Path(os.getenv("OPTIAI_MEEP_OUTPUT_DIR", str(default_meep_output)))
    )

    component_names = []
    try:
        nodes = session.get("p300_circuit_dsl", {}).get("nodes", {})
        component_names = [details.get("component", "") for details in nodes.values()]
    except Exception:
        component_names = []

    return {
        "backend": "meep",
        "meep_python": meep_python,
        "meep_script": meep_script,
        "meep_output_dir": meep_output_dir,
        "component_names": component_names,
    }


def try_log_meep(session: Any) -> None:
    """Write best-effort MEEP handoff metadata for UI inspection."""
    cfg = _build_config_from_session(session)

    lines = [
        "Captured MEEP handoff configuration.",
        f"meep_python={cfg['meep_python']}",
        f"meep_script={cfg['meep_script']}",
        f"meep_output_dir={cfg['meep_output_dir']}",
        f"component_count={len(cfg.get('component_names', []))}",
    ]
    _append_log(lines)

    config_path = PATH.build / "meep_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
