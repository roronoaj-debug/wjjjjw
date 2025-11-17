"""Tidy3D integration scaffold.

This module provides a soft-dependency wrapper so the app can:
- Log the intended Tidy3D calls for the current run
- Optionally build a minimal Simulation JSON (if tidy3d is available)

Note: We do NOT assume Tidy3D license/runtime is available. If import fails,
we write a clear log and continue without crashing the UI.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Any, Dict

from PhotonicsAI.config import PATH


def _log_path() -> Path:
    PATH.build.mkdir(parents=True, exist_ok=True)
    return PATH.build / "tidy3d.log"


def _append_log(lines: list[str]) -> None:
    p = _log_path()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] Tidy3D integration\n")
        for ln in lines:
            f.write(ln.rstrip("\n") + "\n")


def _build_minimal_config(session: Any) -> Dict[str, Any]:
    """Extract a minimal, generic config from session for demonstration.

    If DSL is present, use its doc(title/description) and create a generic
    single-source single-monitor setup around 1550nm.
    """
    dsl = session.get("p300_circuit_dsl", {}) if isinstance(session, dict) else {}
    title = (
        dsl.get("doc", {}).get("title")
        or dsl.get("doc", {}).get("name")
        or "PhIDO-Tidy3D-Run"
    )

    cfg: Dict[str, Any] = {
        "design_task": f"Auto-generated Tidy3D run for: {title}",
        "wavelengths": {"central_nm": 1550.0, "span_nm": 50.0, "samples": 11},
        "simulation": {
            "domain_um": [20.0, 10.0, 2.0],
            "boundary": "pml",
            "pml": [1.0, 1.0, 1.0],
        },
        "sources": {
            "input_port": "auto_src",
            "polarization": "TE",
            "mode_index": 0,
            "angle_deg": 0.0,
        },
        "monitors": [
            {
                "name": "auto_power",
                "type": "port_power",
                "location": "auto_out",
            }
        ],
        "postprocess": {
            "exports": ["json_config"],
            "save_best_only": False,
        },
    }
    return cfg


def run_tidy3d_from_config(config: Dict[str, Any]) -> None:
    """Attempt to import tidy3d and build a minimal Simulation.

    We record which high-level classes are used. If tidy3d is unavailable, we log
    a clear message and return gracefully.
    """
    lines: list[str] = []
    try:
        import tidy3d as td  # type: ignore

        lines.append("import tidy3d as td  # OK")

        # Minimal domain from config
        dom = config.get("simulation", {}).get("domain_um", [20.0, 10.0, 2.0])
        Lx, Ly, Lz = (float(dom[0]), float(dom[1]), float(dom[2]))

        # Build a minimal simulation with explicit grid spec to avoid validation errors
        # Use central wavelength from config (nm -> um)
        wl_cfg = config.get("wavelengths", {}).get("central_nm", 1550.0)
        wl_um = float(wl_cfg) / 1000.0
        grid = td.GridSpec.auto(wavelength=wl_um, min_steps_per_wvl=10)

        # Try to add a minimal plane wave source
        src_obj = None
        try:
            try:
                pulse = td.GaussianPulse(wavelength=wl_um, fwidth=wl_um / 10.0)
            except Exception:
                # Fallback to frequency definition if wavelength signature unsupported
                freq0 = td.C_0 / (wl_um * 1e-6)
                pulse = td.GaussianPulse(freq0=freq0, fwidth=freq0 / 10.0)

            src_obj = td.PlaneWave(
                source_time=pulse,
                center=(-Lx/2 + 0.05, 0.0, 0.0),
                size=(0.0, Ly, Lz),
                direction="+",
                pol_angle=0.0,
            )
            lines.append("td.PlaneWave(...)  # created")
        except Exception as se:  # noqa: BLE001
            lines.append(f"source setup failed: {type(se).__name__}: {se}")

        # Optional: simple flux monitor at the right boundary
        monitors = []
        try:
            freqs = (td.C_0 / (wl_um * 1e-6),)
            mon = td.FluxMonitor(
                name="flux_out",
                center=(Lx/2 - 0.05, 0.0, 0.0),
                size=(0.0, Ly, Lz),
                freqs=freqs,
                normal_dir="+",
            )
            monitors.append(mon)
            lines.append("td.FluxMonitor(...)  # created")
        except Exception as me:  # noqa: BLE001
            lines.append(f"monitor setup failed: {type(me).__name__}: {me}")

        sim = td.Simulation(
            size=(Lx, Ly, Lz),
            run_time=1e-12,
            boundary_spec=td.BoundarySpec.all_sides(td.PML()),
            medium=td.Medium(permittivity=1.0),
            grid_spec=grid,
            sources=tuple([src_obj] if src_obj is not None else []),
            monitors=tuple(monitors),
        )
        lines.append("td.Simulation(...)  # created")

        # Try to plot basic geometry slices for Streamlit
        try:
            # z=0 slice (xy-plane)
            ax = sim.plot(z=0)
            fig = ax.figure
            out_png = PATH.build / "tidy3d_sim_z0.png"
            fig.savefig(out_png, dpi=150, bbox_inches="tight")
            plt.close(fig)
            lines.append(f"write {out_png}")
        except Exception as pe:
            lines.append(f"plot z=0 failed: {type(pe).__name__}: {pe}")

        for axis_key, fname in (("x", "tidy3d_sim_x0.png"), ("y", "tidy3d_sim_y0.png")):
            try:
                kwargs = {axis_key: 0}
                ax = sim.plot(**kwargs)
                fig = ax.figure
                out_png = PATH.build / fname
                fig.savefig(out_png, dpi=150, bbox_inches="tight")
                plt.close(fig)
                lines.append(f"write {out_png}")
            except Exception as pe2:
                lines.append(f"plot {axis_key}=0 failed: {type(pe2).__name__}: {pe2}")

        # Write JSON snapshot for reference
        out_json = PATH.build / "tidy3d_sim.json"
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump({"size": [Lx, Ly, Lz], "note": "minimal demo"}, fh, indent=2)
        lines.append(f"write {out_json}")

        # Optional: run actual FDTD if user explicitly opts in
        if os.getenv("TIDY3D_RUN", "0") == "1":
            try:
                # Prefer cloud run via tidy3d.web if available and API key provided
                api_key = os.getenv("TIDY3D_API_KEY")
                if api_key:
                    try:
                        from tidy3d import web  # type: ignore

                        # Configure API key programmatically for this session
                        try:
                            web.configure(apikey=api_key)
                            lines.append("web.configure(apikey=***)  # set")
                        except Exception as conf_e:  # noqa: BLE001
                            lines.append(f"web.configure failed: {type(conf_e).__name__}: {conf_e}")

                        task_name = f"PhIDO-Run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                        lines.append(f"web.run(sim, task_name={task_name})")
                        results = web.run(
                            simulation=sim,
                            task_name=task_name,
                            path=str(PATH.build / "tidy3d_simulation_data.hdf5"),
                        )
                        res_txt = PATH.build / "tidy3d_results.txt"
                        with open(res_txt, "w", encoding="utf-8") as fh:
                            fh.write("Tidy3D cloud run completed.\n")
                            fh.write(str(results)[:2000])
                        lines.append(f"write {res_txt}")
                    except Exception as cloud_e:  # noqa: BLE001
                        lines.append(f"web.run failed: {type(cloud_e).__name__}: {cloud_e}")
                else:
                    lines.append("TIDY3D_RUN=1 but no TIDY3D_API_KEY found; cloud run skipped.")
                    lines.append("Note: tidy3d>=2.x does not support local sim.run(); use cloud API.")
            except Exception as run_e:  # noqa: BLE001
                lines.append(f"run setup failed: {type(run_e).__name__}: {run_e}")

        _append_log(lines)
    except Exception as e:  # noqa: BLE001
        lines.append(f"tidy3d import or setup failed: {type(e).__name__}: {e}")
        lines.append("No Tidy3D calls executed. This is a soft dependency.")
        lines.append("Install tidy3d and ensure license to enable actual runs.")
        # Also emit a stub snapshot to keep UI links alive
        try:
            out_json = PATH.build / "tidy3d_sim.json"
            with open(out_json, "w", encoding="utf-8") as fh:
                json.dump({"note": "tidy3d unavailable", "size": [20.0, 10.0, 2.0]}, fh, indent=2)
            lines.append(f"write {out_json}")
        except Exception:
            pass
        _append_log(lines)


def try_log_tidy3d(session: Any) -> None:
    """Build a minimal config from session and attempt a Tidy3D demo run/log."""
    cfg = _build_minimal_config(session)
    # Always dump the config used
    PATH.build.mkdir(parents=True, exist_ok=True)
    cfg_path = PATH.build / "tidy3d_config.json"
    with open(cfg_path, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
    _append_log([f"write {cfg_path}"])
    # Try calling tidy3d
    run_tidy3d_from_config(cfg)
