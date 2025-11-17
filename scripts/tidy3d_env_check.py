#!/usr/bin/env python3
"""
Tidy3D / xarray 环境兼容性检查脚本
- 打印 Python 与关键包版本
- 检查 xarray 是否包含 core.alignment （用于识别兼容性）
- 尝试导入 tidy3d 并输出结果/错误

用法：
  /home/shite/myvenv/bin/python scripts/tidy3d_env_check.py
"""
from __future__ import annotations

import importlib
import json
import os
import platform
import sys
from typing import Any


def safe_import_version(pkg: str) -> str:
    try:
        m = importlib.import_module(pkg)
        v = getattr(m, "__version__", "unknown")
        return str(v)
    except Exception as e:  # noqa: BLE001
        return f"not-installed ({type(e).__name__})"


def has_xarray_alignment() -> bool | str:
    try:
        import xarray as xr  # type: ignore
        from xarray.core import alignment as _alignment  # type: ignore
        _ = _alignment  # silence linter
        return True
    except Exception as e:  # noqa: BLE001
        return f"missing: {type(e).__name__}: {e}"


def try_import_tidy3d() -> dict[str, Any]:
    res: dict[str, Any] = {}
    try:
        import tidy3d as td  # type: ignore
        res["ok"] = True
        res["tidy3d_version"] = getattr(td, "__version__", "unknown")
    except Exception as e:  # noqa: BLE001
        res["ok"] = False
        res["error_type"] = type(e).__name__
        res["error"] = str(e)
    return res


def main() -> None:
    info = {
        "python": sys.version.replace("\n", " "),
        "python_exe": sys.executable,
        "platform": platform.platform(),
        "packages": {
            "tidy3d": safe_import_version("tidy3d"),
            "xarray": safe_import_version("xarray"),
            "numpy": safe_import_version("numpy"),
            "scipy": safe_import_version("scipy"),
            "pydantic": safe_import_version("pydantic"),
        },
        "xarray_core_alignment": has_xarray_alignment(),
        "tidy3d_import": try_import_tidy3d(),
    }
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
