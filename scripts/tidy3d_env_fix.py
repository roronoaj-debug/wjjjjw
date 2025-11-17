#!/usr/bin/env python3
"""
Tidy3D / xarray 环境修复脚本（安全默认：仅建议，不直接安装）

- 默认打印建议的安装组合与命令。
- 传入 --apply/-y 才会执行 pip 安装。
- 执行后自动调用 tidy3d_env_check 进行验证。

用法：
  建议模式：/home/shite/myvenv/bin/python scripts/tidy3d_env_fix.py
  应用模式：/home/shite/myvenv/bin/python scripts/tidy3d_env_fix.py --apply
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import List

PY = sys.executable

# 候选策略（从上到下尝试）
# 说明：无法联网或无授权时会失败；脚本会捕获并继续后续策略。
STRATEGIES = [
    {
        "name": "Upgrade tidy3d to latest",
        "commands": [
            [PY, "-m", "pip", "install", "-U", "pip"],
            [PY, "-m", "pip", "install", "-U", "tidy3d"],
        ],
    },
    {
        "name": "Pin xarray to 2023.1.0 (compat for legacy imports)",
        "commands": [
            [PY, "-m", "pip", "install", "xarray==2023.1.0"],
        ],
    },
    {
        "name": "Pin tidy3d==2.6.1 + xarray==2023.1.0",
        "commands": [
            [PY, "-m", "pip", "install", "tidy3d==2.6.1"],
            [PY, "-m", "pip", "install", "xarray==2023.1.0"],
        ],
    },
]


def run_cmd(cmd: List[str], apply: bool) -> dict:
    if not apply:
        return {"cmd": cmd, "skipped": True}
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "cmd": cmd,
            "returncode": out.returncode,
            "stdout": out.stdout[-1000:],
            "stderr": out.stderr[-2000:],
        }
    except Exception as e:  # noqa: BLE001
        return {"cmd": cmd, "error": f"{type(e).__name__}: {e}"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", "-y", action="store_true", help="执行安装而非仅打印建议")
    args = ap.parse_args()

    print("=== Tidy3D/xarray 修复建议 ===")
    for strat in STRATEGIES:
        print(f"- {strat['name']}")
        for cmd in strat["commands"]:
            print("  $", " ".join(cmd))
    print("============================\n")

    if args.apply:
        results = []
        for strat in STRATEGIES:
            print(f"\n>>> 执行策略: {strat['name']}")
            for cmd in strat["commands"]:
                r = run_cmd(cmd, apply=True)
                results.append(r)
                print(json.dumps(r, indent=2, ensure_ascii=False))
            # 执行每个策略后做一次检查
            print("\n>>> 执行检查: tidy3d_env_check")
            chk = subprocess.run([PY, "scripts/tidy3d_env_check.py"], capture_output=True, text=True)
            print(chk.stdout)
            # 如果导入已成功，则结束
            try:
                info = json.loads(chk.stdout or "{}")
                if info.get("tidy3d_import", {}).get("ok"):
                    print("\n✅ 已成功导入 tidy3d，停止后续修复。")
                    return
            except Exception:
                pass
        print("\n⚠️  所有策略已尝试，请检查网络、授权或联系维护者进一步处理。")
    else:
        print("当前为建议模式。加入 --apply 或 -y 参数以实际执行安装。")


if __name__ == "__main__":
    main()
