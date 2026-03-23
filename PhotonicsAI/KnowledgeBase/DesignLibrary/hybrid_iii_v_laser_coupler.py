"""
Name: hybrid_iii_v_laser_coupler

Description: Heterogeneous integrated III-V laser on thin SOI with single-stage adiabatic 
coupler. Enables efficient optical coupling between III-V gain material and silicon 
waveguides for on-chip laser integration with high coupling efficiency.

ports:
  - o1: III-V laser input (bonded)
  - o2: Silicon output waveguide

NodeLabels:
  - III_V_Laser_Coupler
  - Heterogeneous
  - Adiabatic

Bandwidth:
  - C-band (1550 nm)
  - Broadband coupling

Args:
  - coupler_length: Adiabatic coupler length in µm
  - taper_tip_width: Taper tip width in nm
  - si_waveguide_width: Silicon waveguide width in nm

Reference:
  - Paper: "Heterogeneous integrated III–V laser on thin SOI with single-stage adiabatic 
            coupler: device realization and performance analysis"
  - IEEE Journal of Selected Topics in Quantum Electronics, 2015
  - Authors: J. Pu, V. Krishnamurthy et al.
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from IEEE JSTQE 2015
PAPER_PARAMS = {
    # Platform
    "platform": "Heterogeneous III-V on thin SOI",
    "iii_v_material": "InP/InGaAsP",
    "si_layer_nm": 220,  # Thin SOI
    
    # Coupler design
    "coupler_type": "Single-stage adiabatic",
    "tapering": "III-V taper + Si inverse taper",
    "coupling_mechanism": "Evanescent mode transfer",
    
    # Performance
    "coupling_efficiency_percent": ">90",
    "alignment_tolerance_um": "±0.5",
    "wavelength_range_nm": "C-band",
    
    # Laser integration
    "laser_type": "Fabry-Perot or DFB",
    "gain_coupling": "Efficient",
    "thermal_management": "Si substrate heat sink",
    
    # Applications
    "applications": [
        "On-chip laser sources",
        "Optical interconnects",
        "Photonic integrated transceivers",
        "Data center optics",
    ],
}


@gf.cell
def hybrid_iii_v_laser_coupler(
    coupler_length: float = 100.0,
    taper_tip_width: float = 0.08,
    si_wg_width: float = 0.5,
    iii_v_width: float = 3.0,
    taper_length: float = 50.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Adiabatic coupler for III-V laser to silicon waveguide.
    
    Based on IEEE JSTQE 2015 demonstrating heterogeneous
    integration with single-stage adiabatic coupling.
    
    Args:
        coupler_length: Total coupler length in µm
        taper_tip_width: Silicon taper tip width in µm
        si_wg_width: Silicon waveguide width in µm
        iii_v_width: III-V laser width in µm
        taper_length: Taper transition length in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: III-V Si laser coupler
    """
    c = gf.Component()
    
    # Silicon inverse taper (tip to full width)
    si_taper = c << gf.components.taper(
        length=taper_length,
        width1=taper_tip_width,
        width2=si_wg_width,
        cross_section=cross_section,
    )
    
    # Output straight section
    si_wg = c << gf.components.straight(
        length=coupler_length - taper_length,
        cross_section=cross_section,
    )
    si_wg.connect("o1", si_taper.ports["o2"])
    
    # Add ports
    c.add_port("o1", port=si_taper.ports["o1"])
    c.add_port("o2", port=si_wg.ports["o2"])
    
    # Add info
    c.info["coupler_type"] = "III-V to Si adiabatic"
    c.info["coupling_efficiency"] = ">90%"
    c.info["integration_type"] = "Heterogeneous"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the III-V/Si laser coupler.
    
    The model includes:
    - Adiabatic mode conversion efficiency
    - Index matching
    - Coupling losses
    """
    
    def iii_v_laser_coupler_model(
        wl: float = 1.55,
        coupler_length_um: float = 100.0,
        taper_tip_um: float = 0.08,
        # Material indices
        n_iii_v: float = 3.45,  # InGaAsP
        n_si: float = 3.48,
        n_oxide: float = 1.44,
        # Adiabaticity
        adiabaticity: float = 0.95,
        # Losses
        iii_v_loss_dB_cm: float = 5.0,
        si_loss_dB_cm: float = 1.0,
        # Alignment
        lateral_offset_um: float = 0.0,
    ) -> dict:
        """
        Analytical model for III-V/Si adiabatic coupler.
        
        Args:
            wl: Wavelength in µm
            coupler_length_um: Coupler length in µm
            taper_tip_um: Silicon taper tip width in µm
            n_iii_v: III-V effective index
            n_si: Silicon effective index
            n_oxide: Oxide cladding index
            adiabaticity: Adiabatic following efficiency (0-1)
            iii_v_loss_dB_cm: III-V propagation loss
            si_loss_dB_cm: Silicon propagation loss
            lateral_offset_um: Lateral alignment offset in µm
            
        Returns:
            dict: S-parameters and coupling metrics
        """
        # Adiabatic coupling efficiency
        # Depends on index matching and taper profile
        
        # Index difference
        delta_n = jnp.abs(n_iii_v - n_si)
        
        # Mode overlap (depends on taper design)
        # Perfect when indices match through tapering
        mode_overlap = adiabaticity * (1 - delta_n / 0.5)
        mode_overlap = jnp.clip(mode_overlap, 0.8, 1.0)
        
        # Alignment penalty
        alignment_tolerance_um = 0.5
        misalignment_penalty = jnp.exp(-(lateral_offset_um / alignment_tolerance_um)**2)
        
        # Propagation losses
        L_cm = coupler_length_um / 1e4
        prop_loss_iii_v = 10 ** (-iii_v_loss_dB_cm * L_cm / 2 / 10)  # Half in III-V
        prop_loss_si = 10 ** (-si_loss_dB_cm * L_cm / 2 / 10)
        
        # Total coupling efficiency
        coupling_efficiency = mode_overlap * misalignment_penalty * prop_loss_iii_v * prop_loss_si
        
        # S-parameters
        S21 = jnp.sqrt(coupling_efficiency) * jnp.exp(1j * 2 * jnp.pi * n_si * coupler_length_um / wl)
        S11 = jnp.sqrt(1 - coupling_efficiency) * 0.1  # Small reflection
        
        # Coupling loss
        coupling_loss_dB = -10 * jnp.log10(coupling_efficiency + 1e-10)
        
        # Laser output power estimate (assuming 10 mW III-V gain)
        P_iii_v_mW = 10.0
        P_si_output_mW = P_iii_v_mW * coupling_efficiency
        
        return {
            # S-parameters
            "S21": S21,
            "S11": S11,
            # Coupling
            "coupling_efficiency": coupling_efficiency,
            "coupling_loss_dB": coupling_loss_dB,
            "mode_overlap": mode_overlap,
            # Alignment
            "misalignment_penalty": misalignment_penalty,
            "lateral_offset_um": lateral_offset_um,
            # Power
            "output_power_mW": P_si_output_mW,
            # Design
            "adiabaticity": adiabaticity,
        }
    
    return iii_v_laser_coupler_model


# Test code
if __name__ == "__main__":
    # Create component
    c = hybrid_iii_v_laser_coupler()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    
    print("\n--- III-V/Si Laser Coupler Performance ---")
    result = model(wl=1.55, coupler_length_um=100)
    print(f"  Coupling efficiency: {result['coupling_efficiency']*100:.1f}%")
    print(f"  Coupling loss: {result['coupling_loss_dB']:.2f} dB")
    print(f"  Mode overlap: {result['mode_overlap']*100:.1f}%")
    print(f"  Output power (10 mW in): {result['output_power_mW']:.1f} mW")
    
    # Alignment tolerance
    print("\n--- Alignment Tolerance ---")
    for offset in [0.0, 0.2, 0.5, 1.0, 2.0]:
        result = model(lateral_offset_um=offset)
        print(f"  Offset={offset} µm: η = {result['coupling_efficiency']*100:.1f}%, "
              f"Loss = {result['coupling_loss_dB']:.2f} dB")
    
    # Coupler length sweep
    print("\n--- Length Optimization ---")
    for length in [50, 100, 150, 200]:
        result = model(coupler_length_um=length)
        print(f"  L={length} µm: η = {result['coupling_efficiency']*100:.1f}%")
    
    # Paper parameters
    print("\n--- Paper Parameters (IEEE JSTQE 2015) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
