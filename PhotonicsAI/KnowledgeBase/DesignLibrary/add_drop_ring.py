"""Add-Drop Ring Resonator Filter

---
Name: add_drop_ring
Description: |
    双总线环形谐振器滤波器(Add-Drop Ring Resonator)。
    用于WDM系统中的波长选择性分插。谐振波长从input端口耦合到drop端口输出,
    非谐振波长从through端口直通输出。可用于波分复用器/解复用器。
ports: ['o1', 'o2', 'o3', 'o4']
NodeLabels:
    - filter
    - ring
    - add-drop
    - 4-port
    - passive
    - resonator
Bandwidth: C-band (50nm)
Args:
    - radius: Ring radius in μm (default: 10, range: 5-50). Affects FSR.
    - gap: Coupling gap in μm (default: 0.2, range: 0.1-0.5). Affects Q factor.
    - coupling_length: Coupling length for racetrack in μm (default: 0). Set 0 for circular ring.
Reference: https://opg.optica.org/abstract.cfm?uri=ol-40-15-3556
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp


@gf.cell
def add_drop_ring(
    radius: float = 10.0,
    gap: float = 0.2,
    coupling_length: float = 0.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """Create an add-drop ring resonator.
    
    Args:
        radius: Ring radius in μm.
        gap: Coupling gap between bus waveguide and ring in μm.
        coupling_length: Straight coupling length (0 for circular ring).
        cross_section: Waveguide cross section.
        
    Returns:
        gf.Component with ports o1, o2, o3, o4.
        
    Port layout::
    
        o3 (add)       o4 (drop)
           ↓              ↑
        ===+==============+===  (upper bus)
               ╭──────╮
               │ ring │
               ╰──────╯
        ===+==============+===  (lower bus)  
           ↑              ↓
        o1 (input)     o2 (through)
    """
    c = gf.Component()
    
    # Use gdsfactory's ring_double component
    ring = gf.components.ring_double(
        gap=gap,
        radius=radius,
        length_x=coupling_length,
        cross_section=cross_section,
    )
    
    ref = c << ring
    
    # Port mapping
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    c.add_port("o3", port=ref.ports["o3"])
    c.add_port("o4", port=ref.ports["o4"])
    
    return c


def _analytical_model(
    wl=1.55,
    radius=10.0,
    gap=0.2,
    loss_dB_cm=3.0,
    neff=2.45,
    kappa=None,
):
    """Analytical S-parameter model for add-drop ring.
    
    Based on transfer matrix formalism for symmetric double-bus ring resonator.
    
    Args:
        wl: Wavelength in μm.
        radius: Ring radius in μm.
        gap: Coupling gap in μm (used to estimate kappa if kappa is None).
        loss_dB_cm: Waveguide propagation loss in dB/cm.
        neff: Effective refractive index.
        kappa: Coupling coefficient (0-1). If None, estimated from gap.
        
    Returns:
        dict: S-parameter dictionary {(port_in, port_out): complex_value}
    """
    # Estimate coupling coefficient from gap if not provided
    if kappa is None:
        # Empirical estimation: kappa decreases exponentially with gap
        # Typical values: gap=0.1μm -> kappa~0.4, gap=0.2μm -> kappa~0.15, gap=0.3μm -> kappa~0.06
        kappa = 0.4 * jnp.exp(-10 * (gap - 0.1))
        kappa = jnp.clip(kappa, 0.01, 0.5)
    
    # Ring circumference
    L = 2 * jnp.pi * radius  # μm
    
    # Amplitude transmission (loss)
    alpha = loss_dB_cm / 4.343 / 1e4 * 1e6  # convert dB/cm to 1/μm
    a = jnp.exp(-alpha * L / 2)  # amplitude after half round-trip
    
    # Round-trip phase
    phi = 2 * jnp.pi * neff * L / wl
    
    # Coupling coefficients (symmetric coupler)
    t = jnp.sqrt(1 - kappa**2)  # self-coupling (transmission)
    k = kappa                    # cross-coupling
    
    # Denominator (common)
    denom = 1 - t**2 * a * jnp.exp(1j * phi)
    
    # Through port: o1 -> o2
    # Light passes through bottom coupler, doesn't couple to ring
    # OR couples to ring, goes around, couples back
    S21 = (t - a * t * jnp.exp(1j * phi)) / denom
    
    # Drop port: o1 -> o4
    # Light couples from input to ring, propagates half-way, couples to drop
    S41 = -k**2 * jnp.sqrt(a) * jnp.exp(1j * phi / 2) / denom
    
    # Build full S-matrix (4x4, symmetric device)
    # Using reciprocity: S_ij = S_ji
    # Using device symmetry
    return {
        ("o1", "o1"): 0j,      # No back-reflection (ideal)
        ("o1", "o2"): S21,     # Through
        ("o1", "o3"): 0j,      # Isolation (input to add)
        ("o1", "o4"): S41,     # Drop
        ("o2", "o1"): S21,     # Reciprocal
        ("o2", "o2"): 0j,
        ("o2", "o3"): S41,     # Through to add (same as drop by symmetry)
        ("o2", "o4"): 0j,      # Isolation
        ("o3", "o1"): 0j,      # Isolation
        ("o3", "o2"): S41,     # Add to through
        ("o3", "o3"): 0j,
        ("o3", "o4"): S21,     # Add to drop (same as input to through)
        ("o4", "o1"): S41,     # Reciprocal
        ("o4", "o2"): 0j,
        ("o4", "o3"): S21,
        ("o4", "o4"): 0j,
    }


def get_model(model="analytical"):
    """Get SAX-compatible model for circuit simulation.
    
    Args:
        model: Model type
            - "analytical": Use analytical formula (fast, approximate)
            - "fdtd": Use pre-computed FDTD data (accurate, requires npz file)
        
    Returns:
        dict: {"add_drop_ring": model_function}
        
    Example:
        >>> models = get_model()
        >>> ring_model = models["add_drop_ring"]
        >>> S = ring_model(wl=1.55, radius=10)
        >>> print(S["o1", "o2"])  # Through transmission
    """
    if model == "fdtd":
        try:
            from PhotonicsAI.Photon.utils import model_from_npz, get_file_path
            npz_model = model_from_npz(
                get_file_path("add_drop_ring/add_drop_ring_radius10um.npz")
            )
            return {"add_drop_ring": npz_model}
        except (FileNotFoundError, ImportError) as e:
            print(f"Warning: FDTD data not found ({e}), using analytical model")
            return {"add_drop_ring": _analytical_model}
    else:
        return {"add_drop_ring": _analytical_model}


# ============================================================================
# Test / Demo
# ============================================================================
if __name__ == "__main__":
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    
    matplotlib.use("TkAgg")  # or "macosx" on Mac
    
    print("=" * 60)
    print("Add-Drop Ring Resonator Test")
    print("=" * 60)
    
    # Test 1: GDS Generation
    print("\n[1] Generating GDS...")
    c = add_drop_ring(radius=10, gap=0.2)
    print(f"    Ports: {list(c.ports.keys())}")
    print(f"    Size: {c.size}")
    
    # Test 2: S-parameter Model
    print("\n[2] Testing S-parameter model...")
    model = get_model()["add_drop_ring"]
    
    # Single wavelength test
    S = model(wl=1.55, radius=10)
    print(f"    @ λ=1.55μm, radius=10μm:")
    print(f"    |S21|² (through) = {np.abs(S['o1', 'o2'])**2:.4f}")
    print(f"    |S41|² (drop)    = {np.abs(S['o1', 'o4'])**2:.4f}")
    
    # Test 3: Spectrum Plot
    print("\n[3] Plotting transmission spectrum...")
    wl = np.linspace(1.52, 1.58, 1000)
    
    # Vectorize the model call
    S21_arr = np.array([model(w, radius=10, gap=0.2)["o1", "o2"] for w in wl])
    S41_arr = np.array([model(w, radius=10, gap=0.2)["o1", "o4"] for w in wl])
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Transmission in dB
    ax1 = axes[0]
    ax1.plot(wl * 1000, 10 * np.log10(np.abs(S21_arr)**2 + 1e-10), 
             'b-', label='Through (o1→o2)', linewidth=1.5)
    ax1.plot(wl * 1000, 10 * np.log10(np.abs(S41_arr)**2 + 1e-10), 
             'r-', label='Drop (o1→o4)', linewidth=1.5)
    ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Transmission (dB)')
    ax1.set_title('Add-Drop Ring Response (R=10μm, gap=0.2μm)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-40, 5)
    
    # Phase
    ax2 = axes[1]
    ax2.plot(wl * 1000, np.unwrap(np.angle(S21_arr)), 'b-', label='Through', linewidth=1.5)
    ax2.plot(wl * 1000, np.unwrap(np.angle(S41_arr)), 'r-', label='Drop', linewidth=1.5)
    ax2.set_xlabel('Wavelength (nm)')
    ax2.set_ylabel('Phase (rad)')
    ax2.set_title('Phase Response')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("add_drop_ring_test.png", dpi=150)
    print("    Saved: add_drop_ring_test.png")
    
    # Test 4: FSR calculation
    print("\n[4] Estimating FSR...")
    # Find resonances (minima in through)
    through_power = np.abs(S21_arr)**2
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(-through_power, distance=20)
    if len(peaks) >= 2:
        fsr_nm = (wl[peaks[1]] - wl[peaks[0]]) * 1000
        print(f"    Estimated FSR: {fsr_nm:.2f} nm")
    
    plt.show()
    
    # Optional: show GDS
    # c.show()
