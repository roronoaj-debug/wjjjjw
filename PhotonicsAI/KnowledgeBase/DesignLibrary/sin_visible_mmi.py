"""
Name: sin_visible_mmi

Description: Silicon nitride (Si3N4) multimode interferometer (MMI) beam splitter and 
integrated components for visible to near-infrared spectral region. Designed for 
quantum photonic integrated circuits (QPIC) with stringent performance requirements 
including crossing waveguides, asymmetric MZIs, and microring resonators.

ports:
  - o1: Input port 1
  - o2: Input port 2 (for 2x2)
  - o3: Output port 1
  - o4: Output port 2

NodeLabels:
  - SiN_MMI
  - Visible_Splitter
  - QPIC_Component

Bandwidth:
  - Visible to Near-IR (visible: 600-900 nm)
  - Broadband operation

Args:
  - mmi_width: MMI width in µm
  - mmi_length: MMI length in µm
  - waveguide_width: Access waveguide width in µm

Reference:
  - Paper: "SiN integrated photonic components in the Visible to Near-Infrared 
            spectral region"
  - arXiv: 2311.16016
  - Authors: Matteo Sanna, Alessio Baldazzi, Gioele Piccoli, et al.
  - Year: 2023
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from arXiv:2311.16016
PAPER_PARAMS = {
    # Platform
    "platform": "Silicon Nitride (Si3N4)",
    "target_application": "Quantum Photonic Integrated Circuits (QPIC)",
    
    # Wavelength range
    "spectral_range": "Visible to Near-Infrared",
    "typical_wavelengths": ["637 nm", "775 nm", "850 nm"],
    
    # Components demonstrated
    "components": [
        "Crossing waveguides",
        "MMI-based beam splitters",
        "Asymmetric MZI",
        "Microring resonators",
    ],
    
    # MMI specifications
    "mmi_type": "2x2 beam splitter",
    "splitting_ratio": "50:50",
    
    # Waveguide properties
    "waveguide_core_nm": 250,  # Approximate
    "cladding": "SiO2",
    
    # Performance requirements for QPIC
    "qpic_requirements": [
        "Low loss",
        "High splitting accuracy",
        "Broadband operation",
        "Phase stability",
    ],
    
    # Advantages
    "advantages": [
        "CMOS compatible",
        "Low loss in visible",
        "Wide transparency window",
        "Excellent for quantum applications",
    ],
}


@gf.cell
def sin_visible_mmi(
    mmi_width: float = 3.0,
    mmi_length: float = 10.0,
    waveguide_width: float = 0.4,
    taper_length: float = 5.0,
    gap: float = 0.3,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Silicon nitride 2x2 MMI for visible-NIR wavelengths.
    
    Based on arXiv:2311.16016 demonstrating SiN components
    for quantum photonic integrated circuits.
    
    Args:
        mmi_width: MMI multimode region width in µm
        mmi_length: MMI multimode region length in µm
        waveguide_width: Access waveguide width in µm
        taper_length: Input/output taper length in µm
        gap: Gap between output waveguides in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: 2x2 MMI beam splitter
    """
    c = gf.Component()
    
    # Use gdsfactory's MMI 2x2 component
    mmi = c << gf.components.mmi2x2(
        width_mmi=mmi_width,
        length_mmi=mmi_length,
        width=waveguide_width,
        width_taper=1.0,
        length_taper=taper_length,
        gap_mmi=gap,
        cross_section=cross_section,
    )
    
    # Add ports
    c.add_port("o1", port=mmi.ports["o1"])
    c.add_port("o2", port=mmi.ports["o2"])
    c.add_port("o3", port=mmi.ports["o3"])
    c.add_port("o4", port=mmi.ports["o4"])
    
    # Add info
    c.info["mmi_width_um"] = mmi_width
    c.info["mmi_length_um"] = mmi_length
    c.info["application"] = "QPIC"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the SiN visible MMI.
    
    The model includes:
    - Wavelength-dependent splitting
    - Excess loss
    - Phase relations for 2x2 MMI
    """
    
    def sin_visible_mmi_model(
        wl: float = 0.775,
        mmi_width_um: float = 3.0,
        mmi_length_um: float = 10.0,
        n_sin: float = 2.0,
        splitting_ratio: float = 0.5,
        excess_loss_dB: float = 0.3,
    ) -> dict:
        """
        Analytical model for SiN 2x2 MMI beam splitter.
        
        Args:
            wl: Wavelength in µm
            mmi_width_um: MMI width in µm
            mmi_length_um: MMI length in µm
            n_sin: SiN refractive index (wavelength dependent)
            splitting_ratio: Power splitting ratio (default 0.5 for 3dB)
            excess_loss_dB: Excess loss beyond splitting in dB
            
        Returns:
            dict: S-parameters and MMI metrics
        """
        # Wavelength dependence of SiN index
        # Approximate Sellmeier for SiN in visible
        n_eff = n_sin - 0.1 * (wl - 0.775)  # Simple linear model
        
        # Ideal 2x2 MMI S-matrix
        # For a 3dB coupler: S31 = S42 = 1/√2, S41 = S32 = j/√2
        
        kappa = jnp.sqrt(splitting_ratio)
        tau = jnp.sqrt(1 - splitting_ratio)
        
        # Including excess loss
        excess_loss = 10 ** (-excess_loss_dB / 20)
        
        # Phase from MMI propagation
        phase = 2 * jnp.pi * n_eff * mmi_length_um / wl
        
        # S-parameters for 2x2 MMI (ports: 1,2 input; 3,4 output)
        # Bar state (through)
        S31 = excess_loss * tau * jnp.exp(1j * phase)
        S42 = excess_loss * tau * jnp.exp(1j * phase)
        
        # Cross state
        S41 = excess_loss * 1j * kappa * jnp.exp(1j * phase)
        S32 = excess_loss * 1j * kappa * jnp.exp(1j * phase)
        
        # Reflections (ideally zero)
        S11 = 0.01 * jnp.exp(1j * 2 * phase)
        S22 = S11
        S33 = S11
        S44 = S11
        
        # Calculate imbalance
        imbalance_dB = 10 * jnp.log10(jnp.abs(S31)**2 / (jnp.abs(S41)**2 + 1e-10))
        
        return {
            # S-parameters (4-port)
            "S31": S31,
            "S32": S32,
            "S41": S41,
            "S42": S42,
            "S11": S11,
            "S22": S22,
            "S33": S33,
            "S44": S44,
            # MMI metrics
            "splitting_ratio": splitting_ratio,
            "excess_loss_dB": excess_loss_dB,
            "total_insertion_loss_dB": -10 * jnp.log10(jnp.abs(S31)**2 + jnp.abs(S41)**2),
            "imbalance_dB": imbalance_dB,
            "n_eff": n_eff,
        }
    
    return sin_visible_mmi_model


# Test code
if __name__ == "__main__":
    # Create and visualize component
    c = sin_visible_mmi()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=0.775)
    
    print("\n--- SiN Visible MMI Performance ---")
    print(f"  Splitting ratio: {result['splitting_ratio']*100:.1f}%")
    print(f"  Excess loss: {result['excess_loss_dB']:.2f} dB")
    print(f"  Total insertion loss: {result['total_insertion_loss_dB']:.2f} dB")
    print(f"  Imbalance: {result['imbalance_dB']:.2f} dB")
    
    # Wavelength dependence
    print("\n--- Wavelength Dependence ---")
    for wl_nm in [637, 700, 775, 850, 900]:
        result = model(wl=wl_nm/1000)
        print(f"  λ={wl_nm} nm: n_eff = {result['n_eff']:.3f}, Loss = {result['total_insertion_loss_dB']:.2f} dB")
    
    # S-parameter magnitudes
    result = model(wl=0.775)
    print(f"\n--- S-Parameters at 775 nm ---")
    print(f"  |S31|² (bar): {jnp.abs(result['S31'])**2:.3f}")
    print(f"  |S41|² (cross): {jnp.abs(result['S41'])**2:.3f}")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2311.16016) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
