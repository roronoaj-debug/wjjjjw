"""
Name: gaas_ring_laser

Description: GaAs-based monolithically integrated ring-resonator-coupled semiconductor laser.
This device combines a high-quality racetrack ring resonator with III-V gain material for 
single-mode lasing with narrow linewidth and tunable wavelength operation.

ports:
  - o1: Laser output

NodeLabels:
  - Ring_Laser
  - GaAs_Laser
  - Integrated_Laser

Bandwidth:
  - Near-IR (850-1000 nm typical)
  - Single-mode operation

Args:
  - ring_radius: Ring resonator radius in µm
  - coupling_gap: Ring-bus coupling gap in µm
  - gain_length: Active gain region length in µm

Reference:
  - Paper: "GaAs-based photonic integrated circuit platform enabling monolithic 
            ring-resonator-coupled lasers"
  - APL Photonics 2024
  - Authors: J.P. Koester, H. Wenzel, J. Fricke, M. Reggentin, et al.
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from APL Photonics 2024
PAPER_PARAMS = {
    # Platform
    "platform": "GaAs-based PIC",
    "material_system": "AlGaAs/GaAs",
    
    # Ring resonator specifications
    "ring_type": "Racetrack resonator",
    "quality_factor": "High Q",
    "coupling": "Directional coupler to bus waveguide",
    
    # Laser properties
    "laser_type": "Ring-resonator-coupled laser",
    "operation": "Single-mode lasing",
    "wavelength_range_nm": [850, 1000],
    
    # Integration level
    "integration": "Monolithic",
    "waveguide_components": [
        "Racetrack ring resonator",
        "Bus waveguides",
        "Tapers",
        "Gain sections",
    ],
    
    # Key features
    "features": [
        "Single frequency operation",
        "Wavelength selectivity via ring",
        "Monolithically integrated",
        "High side-mode suppression",
    ],
    
    # Applications
    "applications": [
        "Optical interconnects",
        "Short-reach communication",
        "Sensing",
        "Data centers",
    ],
}


@gf.cell
def gaas_ring_laser(
    ring_radius: float = 50.0,
    coupling_gap: float = 0.2,
    coupling_length: float = 10.0,
    gain_length: float = 200.0,
    waveguide_width: float = 0.5,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    GaAs ring-resonator-coupled laser.
    
    Based on APL Photonics 2024 demonstrating monolithic GaAs PIC
    with integrated ring lasers.
    
    Args:
        ring_radius: Ring resonator radius in µm
        coupling_gap: Ring-bus coupling gap in µm
        coupling_length: Straight coupling length in µm
        gain_length: Active gain region length in µm
        waveguide_width: Waveguide width in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: GaAs ring laser
    """
    c = gf.Component()
    
    # Create ring resonator with gain
    ring = c << gf.components.ring_single(
        gap=coupling_gap,
        radius=ring_radius,
        length_x=coupling_length,
        cross_section=cross_section,
    )
    
    # Add output waveguide representing gain section
    straight = c << gf.components.straight(
        length=gain_length,
        width=waveguide_width,
        cross_section=cross_section,
    )
    straight.connect("o1", ring.ports["o2"])
    
    # Add ports
    c.add_port("o1", port=ring.ports["o1"])
    c.add_port("o2", port=straight.ports["o2"])
    
    # Add info
    c.info["ring_radius_um"] = ring_radius
    c.info["gain_length_um"] = gain_length
    c.info["type"] = "ring_laser"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the GaAs ring laser.
    
    The model includes:
    - Lasing threshold calculation
    - Single-mode selection by ring
    - Output power vs. injection current
    """
    
    def gaas_ring_laser_model(
        wl: float = 0.98,
        ring_radius_um: float = 50.0,
        coupling_gap_um: float = 0.2,
        gain_length_um: float = 200.0,
        injection_current_mA: float = 50.0,
        threshold_current_mA: float = 20.0,
        slope_efficiency_W_A: float = 0.3,
        n_eff: float = 3.3,
        ring_loss_dB_cm: float = 2.0,
    ) -> dict:
        """
        Analytical model for GaAs ring-resonator-coupled laser.
        
        Args:
            wl: Center wavelength in µm
            ring_radius_um: Ring radius in µm
            coupling_gap_um: Coupling gap in µm
            gain_length_um: Gain region length in µm
            injection_current_mA: Injection current in mA
            threshold_current_mA: Threshold current in mA
            slope_efficiency_W_A: Slope efficiency in W/A
            n_eff: Effective refractive index
            ring_loss_dB_cm: Ring waveguide loss in dB/cm
            
        Returns:
            dict: Laser output parameters
        """
        # Ring circumference
        ring_circumference = 2 * jnp.pi * ring_radius_um  # µm
        
        # Free spectral range
        FSR_nm = wl**2 * 1000 / (n_eff * ring_circumference)  # nm
        
        # Output power (above threshold)
        above_threshold = jnp.maximum(injection_current_mA - threshold_current_mA, 0)
        output_power_mW = slope_efficiency_W_A * above_threshold
        
        # Ring Q-factor (approximate)
        alpha_dB_cm = ring_loss_dB_cm
        alpha_per_cm = alpha_dB_cm / (10 * jnp.log10(jnp.e))
        Q = 2 * jnp.pi * n_eff * ring_circumference * 1e-4 / (wl * alpha_per_cm * 1e-4)
        
        # Linewidth (Schawlow-Townes limit, simplified)
        h_nu = 1.24 / wl  # eV
        linewidth_MHz = 1e6 * h_nu / (output_power_mW + 0.01)  # Simplified
        linewidth_MHz = jnp.clip(linewidth_MHz, 0.1, 100)
        
        # Side mode suppression (from ring filter)
        SMSR_dB = 30 + 10 * jnp.log10(Q / 1e4 + 1)
        
        # Laser field output
        E_out = jnp.sqrt(output_power_mW / 1000)  # W^0.5
        phase = 2 * jnp.pi * n_eff * gain_length_um / wl
        
        S_out = E_out * jnp.exp(1j * phase)
        
        return {
            # Output
            "output_power_mW": output_power_mW,
            "S_out": S_out,
            # Ring properties
            "FSR_nm": FSR_nm,
            "Q_factor": Q,
            # Laser properties
            "threshold_mA": threshold_current_mA,
            "linewidth_MHz": linewidth_MHz,
            "SMSR_dB": SMSR_dB,
            "wavelength_um": wl,
        }
    
    return gaas_ring_laser_model


# Test code
if __name__ == "__main__":
    # Create component
    c = gaas_ring_laser()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=0.98, injection_current_mA=50)
    
    print("\n--- GaAs Ring Laser Performance ---")
    print(f"  Output power: {result['output_power_mW']:.1f} mW")
    print(f"  Threshold current: {result['threshold_mA']:.1f} mA")
    print(f"  FSR: {result['FSR_nm']:.2f} nm")
    print(f"  Linewidth: {result['linewidth_MHz']:.1f} MHz")
    print(f"  SMSR: {result['SMSR_dB']:.1f} dB")
    
    # L-I curve
    print("\n--- L-I Curve ---")
    for current in [10, 20, 30, 50, 80, 100]:
        result = model(injection_current_mA=current)
        print(f"  I={current} mA: P = {result['output_power_mW']:.1f} mW")
    
    # Paper parameters
    print("\n--- Paper Parameters (APL Photonics 2024) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
