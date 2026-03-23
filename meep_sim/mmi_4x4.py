#!/usr/bin/env python3
"""2D Meep simulation for a 4x4 multimode interference coupler.

This script now supports a more trustworthy splitter characterization flow:
- eigenmode excitation of the selected input waveguide,
- eigenmode monitors for guided-mode power at the input/output ports,
- a straight-waveguide reference normalization run,
- optional coarse geometry sweep for MMI length/width optimization.

The model is still a 2D effective-index approximation of SOI-220 rather than a
full 3D silicon photonics simulation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
import meep as mp
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SOI_220_THICKNESS_UM = 0.22
SOI_220_SI_INDEX = 3.476
SOI_220_OXIDE_INDEX = 1.444


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def parse_float_list(values: str | None) -> list[float]:
    if not values:
        return []
    parsed = []
    for item in values.split(","):
        item = item.strip()
        if not item:
            continue
        parsed.append(float(item))
    return parsed


def parse_bounds(values: str | None) -> tuple[float, float] | None:
    if not values:
        return None
    parsed = parse_float_list(values)
    if len(parsed) != 2:
        raise ValueError("Bounds must contain exactly two comma-separated values.")
    lower, upper = parsed
    if lower > upper:
        lower, upper = upper, lower
    return lower, upper


def insertion_loss_db(transmission: float) -> float:
    if transmission <= 0:
        return float("inf")
    return float(-10.0 * math.log10(transmission))


def resolve_search_bounds(
    explicit_bounds: tuple[float, float] | None,
    sweep_values: str | None,
    default_value: float,
) -> tuple[float, float]:
    if explicit_bounds is not None:
        return explicit_bounds
    parsed = parse_float_list(sweep_values)
    if parsed:
        return min(parsed), max(parsed)
    return default_value, default_value


def build_candidate_output_dir(base_dir: Path, values: dict[str, float], prefix: str) -> Path:
    return base_dir / (
        f"{prefix}_L{values['mmi_length']:.2f}"
        f"_W{values['mmi_width']:.2f}"
        f"_TL{values['taper_length']:.2f}"
        f"_TW{values['taper_width']:.2f}"
        f"_P{values['port_pitch']:.2f}"
        f"_S{values['straight_length']:.2f}"
    )


def apply_candidate_parameters(base_args: argparse.Namespace, values: dict[str, float], output_dir: Path) -> argparse.Namespace:
    candidate = argparse.Namespace(**vars(base_args))
    candidate.mmi_length = values["mmi_length"]
    candidate.mmi_width = values["mmi_width"]
    candidate.taper_length = values["taper_length"]
    candidate.taper_width = values["taper_width"]
    candidate.port_pitch = values["port_pitch"]
    candidate.straight_length = values["straight_length"]
    candidate.optimize_mmi_lengths = None
    candidate.optimize_mmi_widths = None
    candidate.optimize_taper_lengths = None
    candidate.optimize_taper_widths = None
    candidate.optimize_port_pitches = None
    candidate.optimize_straight_lengths = None
    candidate.output_dir = str(output_dir)
    return candidate


def summarize_candidate(summary: dict[str, object], values: dict[str, float], summary_path: Path) -> dict[str, object]:
    return {
        "mmi_length": values["mmi_length"],
        "mmi_width": values["mmi_width"],
        "taper_length": values["taper_length"],
        "taper_width": values["taper_width"],
        "port_pitch": values["port_pitch"],
        "straight_length": values["straight_length"],
        "score": summary["optimization"]["score"],
        "guided_split_ratio": summary["guided_split_ratio"],
        "guided_total_transmission": summary["guided_total_transmission"],
        "guided_insertion_loss_db": summary["guided_insertion_loss_db"],
        "guided_reflection": summary["guided_reflection"],
        "guided_excess_loss": summary["guided_excess_loss"],
        "transmission_shortfall": summary["optimization"]["transmission_shortfall"],
        "summary_path": str(summary_path),
    }


def resolve_pso_bounds(args: argparse.Namespace) -> dict[str, tuple[float, float]]:
    return {
        "mmi_length": resolve_search_bounds(parse_bounds(args.pso_mmi_length_bounds), args.optimize_mmi_lengths, args.mmi_length),
        "mmi_width": resolve_search_bounds(parse_bounds(args.pso_mmi_width_bounds), args.optimize_mmi_widths, args.mmi_width),
        "taper_length": resolve_search_bounds(parse_bounds(args.pso_taper_length_bounds), args.optimize_taper_lengths, args.taper_length),
        "taper_width": resolve_search_bounds(parse_bounds(args.pso_taper_width_bounds), args.optimize_taper_widths, args.taper_width),
        "port_pitch": resolve_search_bounds(parse_bounds(args.pso_port_pitch_bounds), args.optimize_port_pitches, args.port_pitch),
        "straight_length": resolve_search_bounds(parse_bounds(args.pso_straight_length_bounds), args.optimize_straight_lengths, args.straight_length),
    }


def resolve_effective_indices(args: argparse.Namespace) -> dict[str, float | str]:
    avg_clad_index = 0.5 * (args.box_index + args.top_clad_index)

    if args.index_model == "material":
        return {
            "core_index": args.si_index,
            "clad_index": avg_clad_index,
            "vertical_method": "material-index-2d",
        }

    clad_index = args.effective_clad_index if args.effective_clad_index is not None else avg_clad_index
    if args.effective_core_index is not None:
        return {
            "core_index": args.effective_core_index,
            "clad_index": clad_index,
            "vertical_method": "user-effective-index",
        }

    reference_core_index = 2.85 if args.polarization == "te" else 2.05
    thickness_ratio = args.soi_thickness / SOI_220_THICKNESS_UM
    etch_ratio = clamp(args.etch_depth / max(args.soi_thickness, 1e-9), 0.0, 1.0)
    asymmetry_penalty = abs(args.top_clad_index - args.box_index) / SOI_220_OXIDE_INDEX

    confinement_scale = 1.0
    confinement_scale += 0.65 * (thickness_ratio - 1.0)
    confinement_scale += 0.08 * (etch_ratio - 1.0)
    confinement_scale -= 0.06 * asymmetry_penalty
    confinement_scale = clamp(confinement_scale, 0.75, 1.25)

    silicon_adjust = 0.35 * (args.si_index - SOI_220_SI_INDEX)
    delta_ref = reference_core_index - SOI_220_OXIDE_INDEX
    core_index = clad_index + delta_ref * confinement_scale + silicon_adjust
    core_index = clamp(core_index, clad_index + 0.05, args.si_index - 0.05)

    return {
        "core_index": core_index,
        "clad_index": clad_index,
        "vertical_method": "heuristic-effective-index",
    }


def field_settings(polarization: str) -> tuple[mp.Component, str, int]:
    if polarization == "tm":
        return mp.Ez, "Ez", mp.ODD_Z
    return mp.Hz, "Hz", mp.EVEN_Z


def port_centers(port_pitch: float) -> list[float]:
    return [(-1.5 + index) * port_pitch for index in range(4)]


def source_and_monitor_positions(args: argparse.Namespace) -> dict[str, float]:
    mmi_half = 0.5 * args.mmi_length
    left_straight_center = -mmi_half - args.taper_length - 0.5 * args.straight_length
    right_straight_center = mmi_half + args.taper_length + 0.5 * args.straight_length
    source_x = left_straight_center - 0.2 * args.straight_length
    input_monitor_x = left_straight_center + 0.2 * args.straight_length
    output_monitor_x = right_straight_center + 0.2 * args.straight_length
    flux_monitor_x = right_straight_center + 0.35 * args.straight_length
    return {
        "source_x": source_x,
        "input_monitor_x": input_monitor_x,
        "output_monitor_x": output_monitor_x,
        "flux_monitor_x": flux_monitor_x,
    }


def build_mmi_geometry(
    waveguide_width: float,
    taper_width: float,
    taper_length: float,
    mmi_width: float,
    mmi_length: float,
    straight_length: float,
    port_pitch: float,
    core_medium: mp.Medium,
) -> list[mp.GeometricObject]:
    geometry: list[mp.GeometricObject] = []
    y_ports = port_centers(port_pitch)
    mmi_half_length = 0.5 * mmi_length
    straight_center_offset = 0.5 * straight_length

    geometry.append(
        mp.Block(
            size=mp.Vector3(mmi_length, mmi_width, mp.inf),
            center=mp.Vector3(),
            material=core_medium,
        )
    )

    for y_pos in y_ports:
        geometry.append(
            mp.Prism(
                vertices=[
                    mp.Vector3(-mmi_half_length - taper_length, y_pos - 0.5 * waveguide_width),
                    mp.Vector3(-mmi_half_length - taper_length, y_pos + 0.5 * waveguide_width),
                    mp.Vector3(-mmi_half_length, y_pos + 0.5 * taper_width),
                    mp.Vector3(-mmi_half_length, y_pos - 0.5 * taper_width),
                ],
                height=mp.inf,
                material=core_medium,
            )
        )
        geometry.append(
            mp.Prism(
                vertices=[
                    mp.Vector3(mmi_half_length, y_pos - 0.5 * taper_width),
                    mp.Vector3(mmi_half_length, y_pos + 0.5 * taper_width),
                    mp.Vector3(mmi_half_length + taper_length, y_pos + 0.5 * waveguide_width),
                    mp.Vector3(mmi_half_length + taper_length, y_pos - 0.5 * waveguide_width),
                ],
                height=mp.inf,
                material=core_medium,
            )
        )
        geometry.append(
            mp.Block(
                size=mp.Vector3(straight_length, waveguide_width, mp.inf),
                center=mp.Vector3(-mmi_half_length - taper_length - straight_center_offset, y_pos),
                material=core_medium,
            )
        )
        geometry.append(
            mp.Block(
                size=mp.Vector3(straight_length, waveguide_width, mp.inf),
                center=mp.Vector3(mmi_half_length + taper_length + straight_center_offset, y_pos),
                material=core_medium,
            )
        )

    return geometry


def build_reference_geometry(cell_x: float, waveguide_width: float, y_pos: float, core_medium: mp.Medium) -> list[mp.GeometricObject]:
    return [
        mp.Block(
            size=mp.Vector3(cell_x, waveguide_width, mp.inf),
            center=mp.Vector3(0, y_pos),
            material=core_medium,
        )
    ]


def make_source(
    args: argparse.Namespace,
    source_x: float,
    source_y: float,
    monitored_field: mp.Component,
    mode_parity: int,
    core_index: float,
    clad_index: float,
) -> tuple[mp.Source | mp.EigenModeSource, float]:
    fcen = 1.0 / args.wavelength

    if args.source_type == "continuous":
        source_profile: mp.SourceTime = mp.ContinuousSource(frequency=fcen, width=args.source_width)
    else:
        source_profile = mp.GaussianSource(frequency=fcen, fwidth=args.fwidth, cutoff=args.gaussian_cutoff)

    if args.source_kind == "line":
        return (
            mp.Source(
                src=source_profile,
                component=monitored_field,
                center=mp.Vector3(source_x, source_y),
                size=mp.Vector3(0, args.source_span_y),
            ),
            fcen,
        )

    guess_neff = clamp(0.5 * (core_index + clad_index), clad_index + 0.05, core_index - 0.05)
    return (
        mp.EigenModeSource(
            src=source_profile,
            center=mp.Vector3(source_x, source_y),
            size=mp.Vector3(0, args.mode_span_y),
            direction=mp.X,
            eig_match_freq=True,
            eig_band=1,
            eig_parity=mode_parity,
            eig_kpoint=mp.Vector3(fcen * guess_neff, 0, 0),
            eig_resolution=2 * args.resolution,
            eig_tolerance=args.eig_tolerance,
        ),
        fcen,
    )


def run_engine(
    sim: mp.Simulation,
    args: argparse.Namespace,
    monitored_field: mp.Component,
    probe_point: mp.Vector3,
) -> tuple[str, float | None]:
    if args.run_method == "cw":
        sim.init_sim()
        sim.solve_cw(args.cw_tol, args.cw_max_iters, args.cw_L)
        return "cw-solver", None

    if args.until is not None:
        sim.run(until=args.until)
        return "fixed-time", args.until

    sim.run(
        until_after_sources=mp.stop_when_fields_decayed(
            args.decay_by,
            monitored_field,
            probe_point,
            args.field_decay,
        )
    )
    return "decay-stop", None


def get_mode_power(
    sim: mp.Simulation,
    monitor: object,
    mode_parity: int,
    resolution: int,
) -> dict[str, object]:
    result = sim.get_eigenmode_coefficients(
        monitor,
        [1],
        eig_parity=mode_parity,
        eig_resolution=2 * resolution,
    )
    forward = complex(result.alpha[0, 0, 0])
    backward = complex(result.alpha[0, 0, 1])
    return {
        "forward": forward,
        "backward": backward,
        "forward_power": float(abs(forward) ** 2),
        "backward_power": float(abs(backward) ** 2),
        "kpoint": [result.kpoints[0].x, result.kpoints[0].y, result.kpoints[0].z],
        "group_velocity": float(np.asarray(result.vgrp).reshape(-1)[0]),
    }


def plot_fields(
    eps_data: np.ndarray,
    field_data: np.ndarray,
    cell: mp.Vector3,
    y_ports: list[float],
    output_path: Path,
    title: str,
    field_name: str,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)
    extent = [-0.5 * cell.x, 0.5 * cell.x, -0.5 * cell.y, 0.5 * cell.y]

    eps_im = axes[0].imshow(
        eps_data.T,
        origin="lower",
        cmap="gray_r",
        extent=extent,
        aspect="auto",
    )
    axes[0].set_title("Dielectric map")
    axes[0].set_xlabel("x (um)")
    axes[0].set_ylabel("y (um)")
    for y_pos in y_ports:
        axes[0].axhline(y_pos, color="tab:blue", alpha=0.15, linewidth=0.8)
    plt.colorbar(eps_im, ax=axes[0], label="epsilon")

    field_lim = float(np.max(np.abs(field_data)))
    field_im = axes[1].imshow(
        field_data.T,
        origin="lower",
        cmap="RdBu",
        extent=extent,
        aspect="auto",
        vmin=-field_lim,
        vmax=field_lim,
    )
    axes[1].set_title(f"{field_name} field")
    axes[1].set_xlabel("x (um)")
    axes[1].set_ylabel("y (um)")
    for y_pos in y_ports:
        axes[1].axhline(y_pos, color="k", alpha=0.12, linewidth=0.8)
    plt.colorbar(field_im, ax=axes[1], label=field_name)

    fig.suptitle(title)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def simulate_structure(
    args: argparse.Namespace,
    geometry: list[mp.GeometricObject],
    cell: mp.Vector3,
    core_medium: mp.Medium,
    clad_medium: mp.Medium,
    positions: dict[str, float],
    source_y: float,
    monitored_field: mp.Component,
    field_name: str,
    mode_parity: int,
    output_monitor_ys: list[float],
    save_fields: bool,
) -> dict[str, object]:
    source, fcen = make_source(
        args=args,
        source_x=positions["source_x"],
        source_y=source_y,
        monitored_field=monitored_field,
        mode_parity=mode_parity,
        core_index=math.sqrt(core_medium.epsilon_diag.x),
        clad_index=math.sqrt(clad_medium.epsilon_diag.x),
    )

    sim = mp.Simulation(
        cell_size=cell,
        geometry=geometry,
        sources=[source],
        boundary_layers=[mp.PML(args.pml)],
        resolution=args.resolution,
        default_material=clad_medium,
        force_complex_fields=args.run_method == "cw",
    )

    input_mode_monitor = sim.add_mode_monitor(
        fcen,
        0,
        1,
        mp.ModeRegion(
            center=mp.Vector3(positions["input_monitor_x"], source_y),
            size=mp.Vector3(0, args.mode_span_y),
        ),
    )
    input_flux_monitor = sim.add_flux(
        fcen,
        0,
        1,
        mp.FluxRegion(
            center=mp.Vector3(positions["input_monitor_x"], source_y),
            size=mp.Vector3(0, args.monitor_span_y),
        ),
    )

    output_mode_monitors = [
        sim.add_mode_monitor(
            fcen,
            0,
            1,
            mp.ModeRegion(
                center=mp.Vector3(positions["output_monitor_x"], y_pos),
                size=mp.Vector3(0, args.mode_span_y),
            ),
        )
        for y_pos in output_monitor_ys
    ]
    output_flux_monitors = [
        sim.add_flux(
            fcen,
            0,
            1,
            mp.FluxRegion(
                center=mp.Vector3(positions["flux_monitor_x"], y_pos),
                size=mp.Vector3(0, args.monitor_span_y),
            ),
        )
        for y_pos in output_monitor_ys
    ]

    run_mode, run_until = run_engine(
        sim=sim,
        args=args,
        monitored_field=monitored_field,
        probe_point=mp.Vector3(positions["output_monitor_x"], output_monitor_ys[len(output_monitor_ys) // 2]),
    )

    input_mode = get_mode_power(sim, input_mode_monitor, mode_parity, args.resolution)
    output_modes = [get_mode_power(sim, monitor, mode_parity, args.resolution) for monitor in output_mode_monitors]
    input_flux = float(mp.get_fluxes(input_flux_monitor)[0])
    output_fluxes = [float(mp.get_fluxes(monitor)[0]) for monitor in output_flux_monitors]

    result: dict[str, object] = {
        "run_mode": run_mode,
        "run_until": run_until,
        "input_mode": input_mode,
        "output_modes": output_modes,
        "input_flux": input_flux,
        "output_fluxes": output_fluxes,
        "field_max_abs": None,
        "eps_data": None,
        "field_data": None,
        "field_name": field_name,
    }

    if save_fields:
        eps_data = sim.get_array(center=mp.Vector3(), size=cell, component=mp.Dielectric)
        field_data = sim.get_array(center=mp.Vector3(), size=cell, component=monitored_field, cmplx=args.run_method == "cw")
        result["eps_data"] = eps_data
        result["field_data"] = field_data
        result["field_max_abs"] = float(np.max(np.abs(field_data)))

    return result


def evaluate_design(args: argparse.Namespace, write_summary: bool = True, save_plot: bool = True) -> dict[str, object]:
    index_data = resolve_effective_indices(args)
    core_index = float(index_data["core_index"])
    clad_index = float(index_data["clad_index"])
    monitored_field, field_name, mode_parity = field_settings(args.polarization)

    core_medium = mp.Medium(index=core_index)
    clad_medium = mp.Medium(index=clad_index)

    span_x = args.mmi_length + 2.0 * (args.taper_length + args.straight_length + args.pml)
    span_y = args.mmi_width + 2.0 * (args.margin_y + args.pml)
    cell = mp.Vector3(span_x, span_y, 0)

    y_ports = port_centers(args.port_pitch)
    source_y = y_ports[args.input_port - 1]
    positions = source_and_monitor_positions(args)

    reference_geometry = build_reference_geometry(cell.x - 2.0 * args.pml, args.waveguide_width, source_y, core_medium)
    main_geometry = build_mmi_geometry(
        waveguide_width=args.waveguide_width,
        taper_width=args.taper_width,
        taper_length=args.taper_length,
        mmi_width=args.mmi_width,
        mmi_length=args.mmi_length,
        straight_length=args.straight_length,
        port_pitch=args.port_pitch,
        core_medium=core_medium,
    )

    reference_result = simulate_structure(
        args=args,
        geometry=reference_geometry,
        cell=cell,
        core_medium=core_medium,
        clad_medium=clad_medium,
        positions=positions,
        source_y=source_y,
        monitored_field=monitored_field,
        field_name=field_name,
        mode_parity=mode_parity,
        output_monitor_ys=[source_y],
        save_fields=False,
    )
    main_result = simulate_structure(
        args=args,
        geometry=main_geometry,
        cell=cell,
        core_medium=core_medium,
        clad_medium=clad_medium,
        positions=positions,
        source_y=source_y,
        monitored_field=monitored_field,
        field_name=field_name,
        mode_parity=mode_parity,
        output_monitor_ys=y_ports,
        save_fields=save_plot,
    )

    incident_mode_power = float(reference_result["input_mode"]["forward_power"])
    incident_flux = max(float(reference_result["input_flux"]), 0.0)
    if incident_mode_power <= 0:
        raise RuntimeError("Reference run produced zero forward guided-mode power.")

    guided_output_powers = [
        float(mode_data["forward_power"]) / incident_mode_power for mode_data in main_result["output_modes"]
    ]
    guided_reflection = float(main_result["input_mode"]["backward_power"]) / incident_mode_power
    total_guided_transmission = float(sum(guided_output_powers))
    guided_power_floor = 1e-6
    guided_split = [
        power / total_guided_transmission if total_guided_transmission > guided_power_floor else 0.0
        for power in guided_output_powers
    ]
    guided_split_valid = total_guided_transmission > guided_power_floor

    flux_output_powers = [
        max(flux_value, 0.0) / incident_flux if incident_flux > 0 else 0.0 for flux_value in main_result["output_fluxes"]
    ]
    flux_total = sum(flux_output_powers)
    flux_split = [power / flux_total if flux_total > 0 else 0.0 for power in flux_output_powers]

    target = 0.25
    target_transmission = 10 ** (-args.target_loss_db / 10.0)
    split_rms_error = float(np.sqrt(np.mean([(value - target) ** 2 for value in guided_split])))
    excess_loss = max(0.0, 1.0 - guided_reflection - total_guided_transmission)
    transmission_shortfall = max(0.0, target_transmission - total_guided_transmission)
    guided_insertion_loss_db = insertion_loss_db(total_guided_transmission)
    optimization_score = (
        args.weight_split * split_rms_error
        + args.weight_reflection * guided_reflection
        + args.weight_excess_loss * excess_loss
        + args.weight_transmission_shortfall * transmission_shortfall
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_path = output_dir / f"mmi4x4_port{args.input_port}_field.png"
    summary_path = output_dir / f"mmi4x4_port{args.input_port}_summary.json"

    if save_plot:
        plot_fields(
            eps_data=main_result["eps_data"],
            field_data=main_result["field_data"],
            cell=cell,
            y_ports=y_ports,
            output_path=figure_path,
            title=f"4x4 MMI, input port {args.input_port}, {args.polarization.upper()}-like",
            field_name=field_name,
        )

    summary: dict[str, object] = {
        "wavelength_um": args.wavelength,
        "frequency_1_per_um": 1.0 / args.wavelength,
        "input_port": args.input_port,
        "polarization": args.polarization,
        "run_method": args.run_method,
        "run_mode": main_result["run_mode"],
        "run_until": main_result["run_until"],
        "source": {
            "x_um": positions["source_x"],
            "y_um": source_y,
            "type": args.source_type,
            "kind": args.source_kind,
            "direction": "+x",
            "span_y_um": args.mode_span_y if args.source_kind == "eigenmode" else args.source_span_y,
            "field_component": field_name,
        },
        "resolution": args.resolution,
        "index_model": args.index_model,
        "effective_indices": {
            "core": core_index,
            "cladding": clad_index,
            "method": index_data["vertical_method"],
        },
        "soi_stack": {
            "soi_thickness_um": args.soi_thickness,
            "etch_depth_um": args.etch_depth,
            "si_index": args.si_index,
            "box_index": args.box_index,
            "top_clad_index": args.top_clad_index,
        },
        "cell_um": {"sx": cell.x, "sy": cell.y},
        "geometry_um": {
            "mmi_length": args.mmi_length,
            "mmi_width": args.mmi_width,
            "taper_length": args.taper_length,
            "taper_width": args.taper_width,
            "waveguide_width": args.waveguide_width,
            "port_pitch": args.port_pitch,
            "straight_length": args.straight_length,
        },
        "reference": {
            "incident_guided_power": incident_mode_power,
            "incident_flux": incident_flux,
            "input_forward_mode": {
                "real": float(reference_result["input_mode"]["forward"].real),
                "imag": float(reference_result["input_mode"]["forward"].imag),
            },
        },
        "input_monitor": {
            "forward_guided_power_main": float(main_result["input_mode"]["forward_power"]) / incident_mode_power,
            "backward_guided_power_main": guided_reflection,
            "backward_mode": {
                "real": float(main_result["input_mode"]["backward"].real),
                "imag": float(main_result["input_mode"]["backward"].imag),
            },
        },
        "guided_output_power": guided_output_powers,
        "guided_split_ratio": guided_split,
        "guided_split_valid": guided_split_valid,
        "guided_total_transmission": total_guided_transmission,
        "guided_insertion_loss_db": guided_insertion_loss_db,
        "guided_reflection": guided_reflection,
        "guided_excess_loss": excess_loss,
        "flux_output_power": flux_output_powers,
        "flux_split_ratio": flux_split,
        "raw_output_flux": main_result["output_fluxes"],
        "field_max_abs": main_result["field_max_abs"],
        "optimization": {
            "split_rms_error": split_rms_error,
            "target_loss_db": args.target_loss_db,
            "target_transmission": target_transmission,
            "transmission_shortfall": transmission_shortfall,
            "score": optimization_score,
            "target_per_port": target,
        },
        "field_plot": str(figure_path) if save_plot else None,
    }

    if write_summary:
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def run_optimization(args: argparse.Namespace) -> dict[str, object]:
    lengths = parse_float_list(args.optimize_mmi_lengths)
    widths = parse_float_list(args.optimize_mmi_widths)
    taper_lengths = parse_float_list(args.optimize_taper_lengths) or [args.taper_length]
    taper_widths = parse_float_list(args.optimize_taper_widths) or [args.taper_width]
    port_pitches = parse_float_list(args.optimize_port_pitches) or [args.port_pitch]
    straight_lengths = parse_float_list(args.optimize_straight_lengths) or [args.straight_length]
    if not lengths or not widths:
        raise ValueError("Optimization requires both --optimize-mmi-lengths and --optimize-mmi-widths.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates = []
    for length in lengths:
        for width in widths:
            for taper_length in taper_lengths:
                for taper_width in taper_widths:
                    for port_pitch in port_pitches:
                        for straight_length in straight_lengths:
                            values = {
                                "mmi_length": length,
                                "mmi_width": width,
                                "taper_length": taper_length,
                                "taper_width": taper_width,
                                "port_pitch": port_pitch,
                                "straight_length": straight_length,
                            }
                            candidate_output_dir = build_candidate_output_dir(output_dir, values, prefix="grid")
                            candidate = apply_candidate_parameters(args, values, candidate_output_dir)
                            summary = evaluate_design(candidate, write_summary=True, save_plot=False)
                            summary_path = Path(candidate.output_dir) / f"mmi4x4_port{args.input_port}_summary.json"
                            candidates.append(summarize_candidate(summary, values, summary_path))

    best = min(candidates, key=lambda item: item["score"])
    best_args = argparse.Namespace(**vars(args))
    best_args.mmi_length = best["mmi_length"]
    best_args.mmi_width = best["mmi_width"]
    best_args.taper_length = best["taper_length"]
    best_args.taper_width = best["taper_width"]
    best_args.port_pitch = best["port_pitch"]
    best_args.straight_length = best["straight_length"]
    best_args.optimize_mmi_lengths = None
    best_args.optimize_mmi_widths = None
    best_args.optimize_taper_lengths = None
    best_args.optimize_taper_widths = None
    best_args.optimize_port_pitches = None
    best_args.optimize_straight_lengths = None
    best_args.output_dir = str(output_dir / "best")
    best_summary = evaluate_design(best_args, write_summary=True, save_plot=True)

    optimization_summary = {
        "input_port": args.input_port,
        "run_method": args.run_method,
        "source_kind": args.source_kind,
        "source_type": args.source_type,
        "candidates": candidates,
        "best": {
            "mmi_length": best["mmi_length"],
            "mmi_width": best["mmi_width"],
            "taper_length": best["taper_length"],
            "taper_width": best["taper_width"],
            "port_pitch": best["port_pitch"],
            "straight_length": best["straight_length"],
            "score": best["score"],
            "guided_split_ratio": best_summary["guided_split_ratio"],
            "guided_total_transmission": best_summary["guided_total_transmission"],
            "guided_insertion_loss_db": best_summary["guided_insertion_loss_db"],
            "guided_reflection": best_summary["guided_reflection"],
            "guided_excess_loss": best_summary["guided_excess_loss"],
            "summary_path": str(Path(best_args.output_dir) / f"mmi4x4_port{args.input_port}_summary.json"),
            "field_plot": best_summary["field_plot"],
        },
    }
    (output_dir / "optimization_summary.json").write_text(
        json.dumps(optimization_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return optimization_summary


def run_pso_optimization(args: argparse.Namespace) -> dict[str, object]:
    bounds = resolve_pso_bounds(args)
    parameter_names = list(bounds.keys())
    variable_names = [name for name in parameter_names if bounds[name][1] - bounds[name][0] > 1e-9]
    if not variable_names:
        raise ValueError("PSO requires at least one parameter with a non-zero search range.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.pso_seed)
    lower = np.array([bounds[name][0] for name in variable_names], dtype=float)
    upper = np.array([bounds[name][1] for name in variable_names], dtype=float)
    span = upper - lower

    positions = rng.uniform(lower, upper, size=(args.pso_particles, len(variable_names)))
    velocities = rng.uniform(-0.2 * span, 0.2 * span, size=(args.pso_particles, len(variable_names)))

    base_values = np.array([float(getattr(args, name)) for name in variable_names], dtype=float)
    positions[0] = np.clip(base_values, lower, upper)
    velocities[0] = 0.0

    particle_best_positions = positions.copy()
    particle_best_scores = np.full(args.pso_particles, np.inf, dtype=float)
    particle_best_records: list[dict[str, object] | None] = [None] * args.pso_particles

    global_best_position = positions[0].copy()
    global_best_score = float("inf")
    global_best_record: dict[str, object] | None = None

    cache: dict[tuple[float, ...], dict[str, object]] = {}
    evaluations: list[dict[str, object]] = []
    history: list[dict[str, object]] = []

    fixed_values = {name: float(getattr(args, name)) for name in parameter_names if name not in variable_names}

    for iteration in range(args.pso_iterations):
        iteration_best_record: dict[str, object] | None = None

        for particle_index in range(args.pso_particles):
            values = dict(fixed_values)
            for dimension, name in enumerate(variable_names):
                values[name] = round(float(positions[particle_index, dimension]), args.pso_round_digits)

            key = tuple(values[name] for name in parameter_names)
            if key in cache:
                record = cache[key]
            else:
                candidate_output_dir = build_candidate_output_dir(
                    output_dir,
                    values,
                    prefix=f"pso_i{iteration:02d}_p{particle_index:02d}",
                )
                candidate = apply_candidate_parameters(args, values, candidate_output_dir)
                summary = evaluate_design(candidate, write_summary=True, save_plot=False)
                summary_path = Path(candidate.output_dir) / f"mmi4x4_port{args.input_port}_summary.json"
                record = summarize_candidate(summary, values, summary_path)
                cache[key] = record
                evaluations.append(record)

            score = float(record["score"])
            if score < particle_best_scores[particle_index]:
                particle_best_scores[particle_index] = score
                particle_best_positions[particle_index] = positions[particle_index].copy()
                particle_best_records[particle_index] = record

            if score < global_best_score:
                global_best_score = score
                global_best_position = positions[particle_index].copy()
                global_best_record = record

            if iteration_best_record is None or score < float(iteration_best_record["score"]):
                iteration_best_record = record

        if iteration_best_record is None or global_best_record is None:
            raise RuntimeError("PSO failed to evaluate any candidates.")

        history.append(
            {
                "iteration": iteration,
                "best_score": float(iteration_best_record["score"]),
                "best_guided_total_transmission": float(iteration_best_record["guided_total_transmission"]),
                "best_guided_insertion_loss_db": float(iteration_best_record["guided_insertion_loss_db"]),
                "best_parameters": {
                    name: float(iteration_best_record[name]) for name in parameter_names
                },
                "global_best_score": global_best_score,
            }
        )

        if iteration == args.pso_iterations - 1:
            break

        for particle_index in range(args.pso_particles):
            r1 = rng.random(len(variable_names))
            r2 = rng.random(len(variable_names))
            cognitive = args.pso_cognitive * r1 * (particle_best_positions[particle_index] - positions[particle_index])
            social = args.pso_social * r2 * (global_best_position - positions[particle_index])
            velocities[particle_index] = args.pso_inertia * velocities[particle_index] + cognitive + social
            positions[particle_index] = np.clip(positions[particle_index] + velocities[particle_index], lower, upper)

    assert global_best_record is not None
    best_values = {name: float(global_best_record[name]) for name in parameter_names}
    best_candidate = apply_candidate_parameters(args, best_values, output_dir / "best")
    best_summary = evaluate_design(best_candidate, write_summary=True, save_plot=True)

    optimization_summary = {
        "method": "pso",
        "input_port": args.input_port,
        "run_method": args.run_method,
        "source_kind": args.source_kind,
        "source_type": args.source_type,
        "particles": args.pso_particles,
        "iterations": args.pso_iterations,
        "inertia": args.pso_inertia,
        "cognitive": args.pso_cognitive,
        "social": args.pso_social,
        "seed": args.pso_seed,
        "bounds": {name: list(bounds[name]) for name in parameter_names},
        "evaluated_candidates": evaluations,
        "history": history,
        "best": {
            "mmi_length": best_values["mmi_length"],
            "mmi_width": best_values["mmi_width"],
            "taper_length": best_values["taper_length"],
            "taper_width": best_values["taper_width"],
            "port_pitch": best_values["port_pitch"],
            "straight_length": best_values["straight_length"],
            "score": best_summary["optimization"]["score"],
            "guided_split_ratio": best_summary["guided_split_ratio"],
            "guided_total_transmission": best_summary["guided_total_transmission"],
            "guided_insertion_loss_db": best_summary["guided_insertion_loss_db"],
            "guided_reflection": best_summary["guided_reflection"],
            "guided_excess_loss": best_summary["guided_excess_loss"],
            "summary_path": str(Path(best_candidate.output_dir) / f"mmi4x4_port{args.input_port}_summary.json"),
            "field_plot": best_summary["field_plot"],
        },
    }
    (output_dir / "optimization_summary.json").write_text(
        json.dumps(optimization_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return optimization_summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulate a 4x4 MMI coupler in Meep.")
    parser.add_argument("--input-port", type=int, default=1, choices=[1, 2, 3, 4])
    parser.add_argument("--wavelength", type=float, default=1.55, help="Vacuum wavelength in um.")
    parser.add_argument("--fwidth", type=float, default=0.03, help="Source frequency width for Gaussian excitation.")
    parser.add_argument("--source-type", choices=["gaussian", "continuous"], default="continuous")
    parser.add_argument("--source-kind", choices=["eigenmode", "line"], default="eigenmode")
    parser.add_argument("--source-width", type=float, default=20.0, help="ContinuousSource smoothing width.")
    parser.add_argument("--gaussian-cutoff", type=float, default=5.0)
    parser.add_argument("--run-method", choices=["time", "cw"], default="cw")
    parser.add_argument("--cw-tol", type=float, default=1e-8)
    parser.add_argument("--cw-max-iters", type=int, default=10000)
    parser.add_argument("--cw-L", type=int, default=2)
    parser.add_argument("--eig-tolerance", type=float, default=1e-12)
    parser.add_argument("--resolution", type=int, default=24, help="Pixels per um.")
    parser.add_argument("--polarization", choices=["te", "tm"], default="te")
    parser.add_argument("--index-model", choices=["effective", "material"], default="effective")
    parser.add_argument("--si-index", type=float, default=SOI_220_SI_INDEX)
    parser.add_argument("--box-index", type=float, default=SOI_220_OXIDE_INDEX)
    parser.add_argument("--top-clad-index", type=float, default=SOI_220_OXIDE_INDEX)
    parser.add_argument("--soi-thickness", type=float, default=SOI_220_THICKNESS_UM)
    parser.add_argument("--etch-depth", type=float, default=SOI_220_THICKNESS_UM)
    parser.add_argument("--effective-core-index", type=float, default=None)
    parser.add_argument("--effective-clad-index", type=float, default=None)
    parser.add_argument("--waveguide-width", type=float, default=0.45)
    parser.add_argument("--port-pitch", type=float, default=2.0)
    parser.add_argument("--taper-width", type=float, default=1.2)
    parser.add_argument("--taper-length", type=float, default=12.0)
    parser.add_argument("--mmi-width", type=float, default=8.0)
    parser.add_argument("--mmi-length", type=float, default=110.0)
    parser.add_argument("--straight-length", type=float, default=10.0)
    parser.add_argument("--margin-y", type=float, default=3.0)
    parser.add_argument("--pml", type=float, default=2.0)
    parser.add_argument("--source-span-y", type=float, default=2.5)
    parser.add_argument("--mode-span-y", type=float, default=3.0)
    parser.add_argument("--monitor-span-y", type=float, default=1.6)
    parser.add_argument("--decay-by", type=float, default=50.0)
    parser.add_argument("--field-decay", type=float, default=1e-6)
    parser.add_argument(
        "--until",
        type=float,
        default=None,
        help="Run to a fixed simulation time for time-domain snapshots.",
    )
    parser.add_argument("--optimize-mmi-lengths", type=str, default=None, help="Comma-separated MMI lengths.")
    parser.add_argument("--optimize-mmi-widths", type=str, default=None, help="Comma-separated MMI widths.")
    parser.add_argument("--optimize-taper-lengths", type=str, default=None, help="Comma-separated taper lengths.")
    parser.add_argument("--optimize-taper-widths", type=str, default=None, help="Comma-separated taper widths.")
    parser.add_argument("--optimize-port-pitches", type=str, default=None, help="Comma-separated port pitches.")
    parser.add_argument("--optimize-straight-lengths", type=str, default=None, help="Comma-separated straight lengths.")
    parser.add_argument("--optimize-method", choices=["grid", "pso"], default="grid")
    parser.add_argument("--pso-particles", type=int, default=6, help="Number of PSO particles.")
    parser.add_argument("--pso-iterations", type=int, default=4, help="Number of PSO iterations.")
    parser.add_argument("--pso-inertia", type=float, default=0.72, help="PSO inertia weight.")
    parser.add_argument("--pso-cognitive", type=float, default=1.49, help="PSO cognitive weight.")
    parser.add_argument("--pso-social", type=float, default=1.49, help="PSO social weight.")
    parser.add_argument("--pso-seed", type=int, default=42, help="Random seed for PSO.")
    parser.add_argument("--pso-round-digits", type=int, default=3, help="Decimal digits retained for PSO candidate caching.")
    parser.add_argument("--pso-mmi-length-bounds", type=str, default=None, help="Lower,upper bounds for MMI length.")
    parser.add_argument("--pso-mmi-width-bounds", type=str, default=None, help="Lower,upper bounds for MMI width.")
    parser.add_argument("--pso-taper-length-bounds", type=str, default=None, help="Lower,upper bounds for taper length.")
    parser.add_argument("--pso-taper-width-bounds", type=str, default=None, help="Lower,upper bounds for taper width.")
    parser.add_argument("--pso-port-pitch-bounds", type=str, default=None, help="Lower,upper bounds for port pitch.")
    parser.add_argument("--pso-straight-length-bounds", type=str, default=None, help="Lower,upper bounds for straight length.")
    parser.add_argument("--target-loss-db", type=float, default=2.0, help="Target insertion loss in dB.")
    parser.add_argument("--weight-split", type=float, default=1.0, help="Optimization weight for split uniformity.")
    parser.add_argument("--weight-reflection", type=float, default=1.0, help="Optimization weight for reflection.")
    parser.add_argument("--weight-excess-loss", type=float, default=1.0, help="Optimization weight for excess loss.")
    parser.add_argument(
        "--weight-transmission-shortfall",
        type=float,
        default=3.0,
        help="Optimization weight for falling short of the target transmission.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent / "output_modal"),
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    if args.optimize_method == "pso":
        optimization_summary = run_pso_optimization(args)
        best = optimization_summary["best"]
        print("=" * 60)
        print("4x4 MMI PSO optimization complete")
        print("=" * 60)
        print(f"Best MMI length: {best['mmi_length']:.3f} um")
        print(f"Best MMI width:  {best['mmi_width']:.3f} um")
        print(f"Best taper length: {best['taper_length']:.3f} um")
        print(f"Best taper width:  {best['taper_width']:.3f} um")
        print(f"Best port pitch:   {best['port_pitch']:.3f} um")
        print(f"Best straight len: {best['straight_length']:.3f} um")
        print(f"Score: {best['score']:.6f}")
        print("Best guided split ratio:")
        for index, value in enumerate(best["guided_split_ratio"], start=1):
            print(f"  Port {index}: {value:.6f}")
        print(f"Guided total transmission: {best['guided_total_transmission']:.6f}")
        print(f"Guided insertion loss: {best['guided_insertion_loss_db']:.6f} dB")
        print(f"Guided reflection: {best['guided_reflection']:.6f}")
        print(f"Guided excess loss: {best['guided_excess_loss']:.6f}")
        print(f"Field plot: {best['field_plot']}")
        return

    if args.optimize_mmi_lengths or args.optimize_mmi_widths:
        optimization_summary = run_optimization(args)
        best = optimization_summary["best"]
        print("=" * 60)
        print("4x4 MMI optimization complete")
        print("=" * 60)
        print(f"Best MMI length: {best['mmi_length']:.3f} um")
        print(f"Best MMI width:  {best['mmi_width']:.3f} um")
        print(f"Best taper length: {best['taper_length']:.3f} um")
        print(f"Best taper width:  {best['taper_width']:.3f} um")
        print(f"Best port pitch:   {best['port_pitch']:.3f} um")
        print(f"Best straight len: {best['straight_length']:.3f} um")
        print(f"Score: {best['score']:.6f}")
        print("Best guided split ratio:")
        for index, value in enumerate(best["guided_split_ratio"], start=1):
            print(f"  Port {index}: {value:.6f}")
        print(f"Guided total transmission: {best['guided_total_transmission']:.6f}")
        print(f"Guided insertion loss: {best['guided_insertion_loss_db']:.6f} dB")
        print(f"Guided reflection: {best['guided_reflection']:.6f}")
        print(f"Guided excess loss: {best['guided_excess_loss']:.6f}")
        print(f"Field plot: {best['field_plot']}")
        return

    summary = evaluate_design(args, write_summary=True, save_plot=True)

    print("=" * 60)
    print("4x4 MMI modal-power simulation complete")
    print("=" * 60)
    print(f"Input port: {summary['input_port']}")
    print(f"Wavelength: {summary['wavelength_um']} um")
    print(f"Polarization: {summary['polarization']}")
    print(f"Run method: {summary['run_method']}")
    print(f"Run mode: {summary['run_mode']}")
    print(f"Source type: {summary['source']['type']}")
    print(f"Source kind: {summary['source']['kind']}")
    print(
        "Effective indices: "
        f"core={summary['effective_indices']['core']:.4f}, "
        f"cladding={summary['effective_indices']['cladding']:.4f}"
    )
    print("Guided output power (normalized to reference input mode):")
    for index, value in enumerate(summary["guided_output_power"], start=1):
        print(f"  Port {index}: {value:.6f}")
    print("Guided split ratio:")
    for index, value in enumerate(summary["guided_split_ratio"], start=1):
        print(f"  Port {index}: {value:.6f}")
    print(f"Guided total transmission: {summary['guided_total_transmission']:.6f}")
    print(f"Guided insertion loss: {summary['guided_insertion_loss_db']:.6f} dB")
    print(f"Guided reflection: {summary['guided_reflection']:.6f}")
    print(f"Guided excess loss: {summary['guided_excess_loss']:.6f}")
    print(f"Optimization score: {summary['optimization']['score']:.6f}")
    print(f"Field plot: {summary['field_plot']}")


if __name__ == "__main__":
    main()
