"""PCM-clad Tunable Silicon Micro-ring Resonator

---
Name: pcm_tunable_ring
Description: |
    相变材料(Sb2S3)覆盖的可调环形谐振器。
    利用PCM的非易失性相变实现低功耗波长调谐。
    结合热光效应可实现7-bit (127级)精细调谐。
    适用于可编程光子集成电路、光开关和神经形态计算。
ports: ['o1', 'o2']
NodeLabels:
    - tunable
    - ring
    - resonator
    - pcm
    - phase-change
    - nonvolatile
    - programmable
Bandwidth: C-band (1500-1560 nm)
Args:
    - radius: Ring radius in μm (default: 10)
    - gap: Bus-ring coupling gap in nm (default: 270)
    - pcm_length: PCM stripe length in μm (default: 10)
    - pcm_width: PCM stripe width in nm (default: 450)
    - wg_width: Waveguide width in nm (default: 500)
    - etch_depth: Partial etch depth in nm (default: 120)
Reference: arXiv:2412.07447, APL Photonics (2024)
Authors: Jayita Dutta, Rui Chen, Virat Tara, Arka Majumdar
DOI: https://doi.org/10.48550/arXiv.2412.07447
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp


# ==============================================================================
# Extracted Parameters from arXiv:2412.07447
# ==============================================================================
PAPER_PARAMS = {
    # Fabrication (SOI platform)
    "platform": "SOI (220nm Si / 2μm BOX)",
    "foundry": "WaferPro",
    "waveguide_width_nm": 500,
    "waveguide_height_nm": 220,
    "etch_depth_nm": 120,  # partial etch
    "bus_ring_gap_nm": 270,  # near-critical coupling
    
    # PCM parameters
    "pcm_material": "Sb2S3",
    "pcm_length_um": 10,
    "pcm_width_nm": 450,
    "pcm_thickness_nm": 20,
    "capping_material": "Al2O3",
    "capping_thickness_nm": 40,
    
    # Heater (PIN diode)
    "heater_type": "PIN silicon microheater",
    "intrinsic_width_um": 0.9,  # optimized for low voltage
    
    # Performance
    "fsr_nm": 2.42,
    "resonance_shift_nm": 0.25,  # a-phase to c-phase
    "switching_voltage_amorphization_V": 2.75,
    "switching_voltage_crystallization_V": 1.6,
    "switching_energy_amorphization_nJ": 35.33,
    "switching_energy_crystallization_mJ": 0.48,
    "endurance_cycles": 2000,  # demonstrated
    "operation_levels": 127,  # 7-bit with hybrid TO/PCM
    "wavelength_nm": 1550,
}


@gf.cell
def pcm_tunable_ring(
    radius: float = 10.0,
    gap: float = 0.27,  # 270 nm from paper
    pcm_length: float = 10.0,
    wg_width: float = 0.5,  # 500 nm
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """Create a PCM-clad tunable silicon micro-ring resonator.
    
    Based on design from arXiv:2412.07447. This is a single-bus (all-pass)
    ring resonator with PCM on top for non-volatile tuning.
    
    Args:
        radius: Ring radius in μm.
        gap: Bus-ring coupling gap in μm.
        pcm_length: Length of PCM stripe on ring in μm.
        wg_width: Waveguide width in μm.
        cross_section: Waveguide cross section.
        
    Returns:
        gf.Component with ports o1 (input) and o2 (output/through).
        
    Port layout::
    
        o1 (input) ═══════╦═══════ o2 (through)
                          ║
                     ╭────╨────╮
                     │  ring   │ ← PCM stripe
                     │   +     │
                     │  PIN    │
                     ╰─────────╯
    """
    c = gf.Component()
    
    # Create ring_single (all-pass configuration)
    ring = gf.components.ring_single(
        gap=gap,
        radius=radius,
        length_x=0,
        length_y=0,
        cross_section=cross_section,
    )
    
    ref = c << ring
    
    # Port mapping
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    
    # Note: PCM layer and heater not shown in basic GDS
    # Full layout would include additional metal and PCM layers
    
    return c


def _analytical_model(
    wl=1.55,
    radius=10.0,
    gap=0.27,
    loss_dB_cm=3.0,
    neff=2.45,
    kappa=None,
    pcm_state="amorphous",  # "amorphous" or "crystalline"
):
    """Analytical S-parameter model for PCM-clad ring resonator.
    
    The PCM state affects the effective index, causing resonance shift.
    
    Args:
        wl: Wavelength in μm.
        radius: Ring radius in μm.
        gap: Coupling gap in μm.
        loss_dB_cm: Waveguide propagation loss in dB/cm.
        neff: Effective refractive index (baseline).
        kappa: Coupling coefficient. If None, estimated from gap.
        pcm_state: "amorphous" or "crystalline" phase of Sb2S3.
        
    Returns:
        dict: S-parameter dictionary {(port_in, port_out): complex_value}
    """
    # Estimate coupling coefficient from gap
    if kappa is None:
        kappa = 0.3 * jnp.exp(-8 * (gap - 0.15))
        kappa = jnp.clip(kappa, 0.05, 0.4)
    
    # PCM-induced effective index change
    # Based on paper: ~0.25 nm resonance shift over FSR=2.42 nm → Δneff ≈ 0.01
    delta_neff_pcm = 0.0 if pcm_state == "amorphous" else 0.01
    neff_total = neff + delta_neff_pcm
    
    # Ring circumference
    L = 2 * jnp.pi * radius
    
    # Loss
    alpha = loss_dB_cm / 4.343 / 1e4 * 1e6  # 1/μm
    a = jnp.exp(-alpha * L)  # round-trip amplitude transmission
    
    # Phase
    phi = 2 * jnp.pi * neff_total * L / wl
    
    # Coupling (single bus)
    t = jnp.sqrt(1 - kappa**2)
    
    # All-pass transfer function: H = (t - a*exp(j*phi)) / (1 - t*a*exp(j*phi))
    S21 = (t - jnp.sqrt(a) * jnp.exp(1j * phi)) / (1 - t * jnp.sqrt(a) * jnp.exp(1j * phi))
    
    return {
        ("o1", "o1"): 0j,
        ("o1", "o2"): S21,
        ("o2", "o1"): S21,  # reciprocal
        ("o2", "o2"): 0j,
    }


def get_model(model="analytical"):
    """Get SAX-compatible model.
    
    Args:
        model: "analytical" for formula-based model.
        
    Returns:
        dict: {"pcm_tunable_ring": model_function}
    """
    return {"pcm_tunable_ring": _analytical_model}


# ==============================================================================
# Test
# ==============================================================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    
    print("=" * 60)
    print("PCM Tunable Ring Resonator (arXiv:2412.07447)")
    print("=" * 60)
    print("\nExtracted Parameters:")
    for k, v in PAPER_PARAMS.items():
        print(f"  {k}: {v}")
    
    # GDS test
    print("\n[1] Generating GDS...")
    c = pcm_tunable_ring(radius=10, gap=0.27)
    print(f"    Ports: {list(c.ports.keys())}")
    
    # Model test
    print("\n[2] Testing S-parameter model...")
    model = get_model()["pcm_tunable_ring"]
    
    wl = np.linspace(1.54, 1.56, 1000)
    
    # Compare amorphous vs crystalline states
    S21_amorphous = np.array([model(w, pcm_state="amorphous")["o1", "o2"] for w in wl])
    S21_crystalline = np.array([model(w, pcm_state="crystalline")["o1", "o2"] for w in wl])
    
    plt.figure(figsize=(10, 4))
    
    plt.subplot(121)
    plt.plot(wl * 1000, 10 * np.log10(np.abs(S21_amorphous)**2 + 1e-10), 
             'b-', label='Amorphous', linewidth=1.5)
    plt.plot(wl * 1000, 10 * np.log10(np.abs(S21_crystalline)**2 + 1e-10), 
             'r--', label='Crystalline', linewidth=1.5)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmission (dB)')
    plt.title('PCM Tunable Ring - Phase States')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(122)
    # Show resonance shift
    T_amor = np.abs(S21_amorphous)**2
    T_crys = np.abs(S21_crystalline)**2
    
    # Find resonance (minimum)
    idx_amor = np.argmin(T_amor)
    idx_crys = np.argmin(T_crys)
    shift_nm = (wl[idx_crys] - wl[idx_amor]) * 1000
    
    plt.plot(wl * 1000, T_amor, 'b-', label='Amorphous', linewidth=1.5)
    plt.plot(wl * 1000, T_crys, 'r--', label='Crystalline', linewidth=1.5)
    plt.axvline(wl[idx_amor] * 1000, color='b', linestyle=':', alpha=0.5)
    plt.axvline(wl[idx_crys] * 1000, color='r', linestyle=':', alpha=0.5)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmission (linear)')
    plt.title(f'Resonance Shift: ~{shift_nm:.2f} nm')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("pcm_tunable_ring_test.png", dpi=150)
    print(f"    Resonance shift (a→c): {shift_nm:.2f} nm")
    print("    Saved: pcm_tunable_ring_test.png")
    
    plt.show()
