"""ScAlN Micro-ring Resonator (CMOS-compatible)

---
Name: scaln_ring
Description: |
    氮化铝钪(ScAlN)薄膜环形谐振器。
    CMOS兼容的新型光子集成平台,具有优良的非线性光学特性。
    经过表面抛光和退火处理,实现低损耗高Q值。
    适用于非线性光学、电光调制和大规模光子集成电路。
ports: ['o1', 'o2']
NodeLabels:
    - ring
    - resonator
    - scaln
    - nitride
    - cmos-compatible
    - low-loss
    - high-q
Bandwidth: C-band
Args:
    - radius: Ring radius in μm (default: 50)
    - gap: Bus-ring coupling gap in μm (default: 0.3)
    - wg_width: Waveguide width in μm (default: 1.0)
    - wg_height: Waveguide height in nm (default: 400)
Reference: arXiv:2403.14212, APL Photonics 9, 066109 (2024)
Authors: Sihao Wang et al.
DOI: https://doi.org/10.1063/5.0208517
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp


# ==============================================================================
# Extracted Parameters from arXiv:2403.14212
# ==============================================================================
PAPER_PARAMS = {
    # Fabrication
    "platform": "ScAlN-on-insulator (CMOS 200mm line)",
    "material": "Scandium Aluminum Nitride (ScAlN)",
    "waveguide_height_nm": 400,
    "etch_type": "fully etched",
    "deposition": "sputtered thin-film",
    
    # Processing
    "surface_treatment": "polishing + annealing",
    
    # Performance
    "intrinsic_q_factor": 1.47e5,
    "propagation_loss_dB_cm": 2.4,
    
    # Material properties (ScAlN advantages)
    "nonlinear_properties": "favorable χ(2) and χ(3)",
    "cmos_compatible": True,
    "scalable": "200mm wafer",
}


@gf.cell
def scaln_ring(
    radius: float = 50.0,
    gap: float = 0.3,
    wg_width: float = 1.0,
    length_x: float = 0.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """Create a ScAlN micro-ring resonator.
    
    Based on design from arXiv:2403.14212. High-Q ring resonator on
    CMOS-compatible ScAlN-on-insulator platform.
    
    Args:
        radius: Ring radius in μm.
        gap: Bus-ring coupling gap in μm.
        wg_width: Waveguide width in μm.
        length_x: Straight coupling length (0 for circular).
        cross_section: Waveguide cross section.
        
    Returns:
        gf.Component with ports o1 and o2.
    """
    c = gf.Component()
    
    ring = gf.components.ring_single(
        gap=gap,
        radius=radius,
        length_x=length_x,
        cross_section=cross_section,
    )
    
    ref = c << ring
    
    c.add_port("o1", port=ref.ports["o1"])
    c.add_port("o2", port=ref.ports["o2"])
    
    return c


def _analytical_model(
    wl=1.55,
    radius=50.0,
    gap=0.3,
    loss_dB_cm=2.4,  # from paper
    neff=1.85,  # ScAlN effective index estimate
    q_factor=1.47e5,  # intrinsic Q from paper
):
    """Analytical S-parameter model for ScAlN ring resonator.
    
    High-Q resonator with low propagation loss.
    
    Args:
        wl: Wavelength in μm.
        radius: Ring radius in μm.
        gap: Coupling gap in μm.
        loss_dB_cm: Propagation loss (2.4 dB/cm from paper).
        neff: Effective refractive index.
        q_factor: Intrinsic quality factor (1.47e5 from paper).
        
    Returns:
        dict: S-parameter dictionary
    """
    # Ring circumference
    L = 2 * jnp.pi * radius  # μm
    
    # Loss from propagation
    alpha = loss_dB_cm / 4.343 / 1e4 * 1e6  # 1/μm
    a = jnp.exp(-alpha * L)  # round-trip amplitude
    
    # Estimate coupling from Q factor
    # Q = λ / FWHM, and for critical coupling: Q ≈ π*ng*L / (λ*(1-t²))
    # For high-Q, coupling is weak
    kappa = 0.05  # weak coupling for high Q
    t = jnp.sqrt(1 - kappa**2)
    
    # Phase
    phi = 2 * jnp.pi * neff * L / wl
    
    # All-pass transfer function
    S21 = (t - jnp.sqrt(a) * jnp.exp(1j * phi)) / (1 - t * jnp.sqrt(a) * jnp.exp(1j * phi))
    
    return {
        ("o1", "o1"): 0j,
        ("o1", "o2"): S21,
        ("o2", "o1"): S21,
        ("o2", "o2"): 0j,
    }


def get_model(model="analytical"):
    """Get SAX-compatible model.
    
    Returns:
        dict: {"scaln_ring": model_function}
    """
    return {"scaln_ring": _analytical_model}


# ==============================================================================
# Test
# ==============================================================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    
    print("=" * 60)
    print("ScAlN Ring Resonator (arXiv:2403.14212)")
    print("=" * 60)
    print("\nExtracted Parameters:")
    for k, v in PAPER_PARAMS.items():
        print(f"  {k}: {v}")
    
    # GDS
    c = scaln_ring(radius=50, gap=0.3)
    print(f"\nPorts: {list(c.ports.keys())}")
    
    # Model test - narrow wavelength range to see sharp resonances
    model = get_model()["scaln_ring"]
    wl = np.linspace(1.549, 1.551, 2000)
    
    S21 = np.array([model(w, radius=50)["o1", "o2"] for w in wl])
    
    plt.figure(figsize=(10, 4))
    plt.subplot(121)
    plt.plot(wl * 1000, 10 * np.log10(np.abs(S21)**2 + 1e-15), 'b-', linewidth=1)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmission (dB)')
    plt.title('ScAlN Ring (R=50μm, Q~1.5×10⁵)')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(122)
    plt.plot(wl * 1000, np.abs(S21)**2, 'b-', linewidth=1)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmission (linear)')
    plt.title('High-Q Resonance')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("scaln_ring_test.png", dpi=150)
    print("Saved: scaln_ring_test.png")
    plt.show()
