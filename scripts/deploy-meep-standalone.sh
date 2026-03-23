#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_ENV="${REPO_ROOT}/.meep-env"
LEGACY_ENV="/home/naie/.local/share/mamba/envs/meep"

echo "[meep] repo root: ${REPO_ROOT}"
echo "[meep] target env: ${TARGET_ENV}"

if [[ -x "${TARGET_ENV}/bin/python" ]]; then
  echo "[meep] target env already exists, skip deployment"
  exit 0
fi

if command -v micromamba >/dev/null 2>&1; then
  echo "[meep] deploying with micromamba"
  micromamba create -y -p "${TARGET_ENV}" -c conda-forge python=3.10 meep numpy scipy matplotlib h5py
elif command -v mamba >/dev/null 2>&1; then
  echo "[meep] deploying with mamba"
  mamba create -y -p "${TARGET_ENV}" -c conda-forge python=3.10 meep numpy scipy matplotlib h5py
elif command -v conda >/dev/null 2>&1; then
  echo "[meep] deploying with conda"
  conda create -y -p "${TARGET_ENV}" -c conda-forge python=3.10 meep numpy scipy matplotlib h5py
elif [[ -d "${LEGACY_ENV}" ]]; then
  echo "[meep] no conda family tool detected, cloning legacy env into repo-local target"
  cp -a "${LEGACY_ENV}" "${TARGET_ENV}"
else
  echo "[meep] error: no deploy tool found and no legacy env to clone"
  exit 1
fi

"${TARGET_ENV}/bin/python" - <<'PY'
import meep
print("[meep] import ok:", meep.__version__ if hasattr(meep, "__version__") else "unknown")
PY

echo "[meep] standalone deployment completed"
