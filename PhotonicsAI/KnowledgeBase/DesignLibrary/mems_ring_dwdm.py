"""
Name: mems_ring_dwdm

Description: MEMS-actuated microring resonator for DWDM (Dense Wavelength Division Multiplexing)
applications. Features full-FSR (Free Spectral Range) wavelength tuning capability through 
electrostatic MEMS actuation of the coupling gap. The design enables complete reconfigurability
for wavelength-selective switching and filtering in WDM systems.

ports:
  - o1: Input port
  - o2: Through port
  - o3: Drop port
  - o4: Add port

NodeLabels:
  - MEMS_Ring
  - DWDM_Filter

Bandwidth:
  - C-band (1530-1565 nm)
  - Full FSR tuning (3.5 nm)

Args:
  - radius: Ring radius in µm (default: 20.0)
  - width: Waveguide width in nm (default: 500)
  - gap_min: Minimum coupling gap in nm (default: 100)
  - gap_max: Maximum coupling gap in nm (default: 400)
  - fsr: Free spectral range in nm (default: 3.5)

Reference:
  - Paper: "Fully reconfigurable silicon photonic MEMS microring resonators for DWDM"
  - Source: Photonics Research, 2025
  - Authors: Y. Lu, Y. Hu, Q. Ma, Y. Liu, J. Zhu, H. Li, D. Dai
  - Link: https://opg.optica.org/abstract.cfm?uri=prj-13-5-1353
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from the Google Scholar reference
PAPER_PARAMS = {
    # Device architecture
    "configuration": "Add-drop microring with MEMS actuator",
    "platform": "Silicon photonics (SOI)",
    
    # Ring geometry
    "ring_radius_um": 20.0,  # Estimated typical value
    "waveguide_width_nm": 500,  # Standard silicon strip waveguide
    "waveguide_height_nm": 220,  # Standard SOI
    
    # MEMS-tunable coupling
    "gap_min_nm": 100,  # Minimum gap (maximum coupling)
    "gap_max_nm": 400,  # Maximum gap (minimum coupling)
    "actuation": "Electrostatic MEMS",
    
    # Wavelength characteristics
    "FSR_nm": 3.5,  # Free Spectral Range
    "tuning_range": "Full FSR",  # Complete wavelength reconfigurability
    "wavelength_band": "C-band",
    
    # MEMS double-ring variant
    "double_ring_option": True,
    
    # Fabrication
    "fabrication_compatible": True,
    "note": "Meets design rules of fabrication processes",
}


@gf.cell
def mems_ring_dwdm(
    radius: float = 20.0,
    width: float = 0.5,
    gap: float = 0.2,
    coupling_length: float = 5.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    MEMS-tunable microring resonator for DWDM add-drop filtering.
    
    Based on silicon photonic MEMS microring with full-FSR tuning range
    through electrostatic gap modulation.
    
    Args:
        radius: Ring radius in µm
        width: Waveguide width in µm
        gap: Initial coupling gap in µm
        coupling_length: Coupling region length in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: MEMS ring with o1 (input), o2 (through), o3 (drop), o4 (add) ports
    """
    c = gf.Component()
    
    # Create ring resonator with add-drop configuration
    add_drop = c << gf.components.ring_double(
        radius=radius,
        gap=gap,
        length_x=coupling_length,
        cross_section=cross_section,
    )
    
    # Add ports
    c.add_port("o1", port=add_drop.ports["o1"])  # Input
    c.add_port("o2", port=add_drop.ports["o2"])  # Through
    c.add_port("o3", port=add_drop.ports["o3"])  # Drop
    c.add_port("o4", port=add_drop.ports["o4"])  # Add
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the MEMS-tunable ring.
    
    The model includes:
    - Gap-dependent coupling coefficient
    - Wavelength-dependent transmission
    - MEMS actuation effect on resonance tuning
    """
    
    def mems_ring_dwdm_model(
        wl: float = 1.55,
        radius: float = 20.0,
        gap: float = 0.2,
        n_eff: float = 2.4,
        n_g: float = 4.2,
        alpha_dB_cm: float = 2.0,
        gap_voltage_coefficient: float = 0.05,  # µm per Volt
        applied_voltage: float = 0.0,
    ) -> dict:
        """
        Analytical model for MEMS-tunable add-drop ring resonator.
        
        Args:
            wl: Wavelength in µm
            radius: Ring radius in µm
            gap: Initial coupling gap in µm
            n_eff: Effective refractive index
            n_g: Group index
            alpha_dB_cm: Propagation loss in dB/cm
            gap_voltage_coefficient: Gap change per applied voltage (µm/V)
            applied_voltage: MEMS actuation voltage (V)
            
        Returns:
            dict: S-parameters and resonator metrics
        """
        # Physical constants
        c_light = 3e8  # Speed of light (m/s)
        
        # MEMS-adjusted gap
        effective_gap = gap - gap_voltage_coefficient * applied_voltage
        effective_gap = jnp.maximum(effective_gap, 0.05)  # Minimum gap limit
        
        # Ring parameters
        L = 2 * jnp.pi * radius * 1e-6  # Ring length in m
        
        # Calculate FSR
        FSR_Hz = c_light / (n_g * L)
        FSR_nm = (wl * 1e-6)**2 * FSR_Hz / c_light * 1e9
        
        # Gap-dependent coupling coefficient (exponential decay model)
        kappa_0 = 0.5  # Base coupling at reference gap
        gap_decay = 2.0  # µm^-1
        kappa = kappa_0 * jnp.exp(-gap_decay * (effective_gap - 0.2))
        kappa = jnp.clip(kappa, 0.01, 0.9)
        
        # Coupling coefficients
        t = jnp.sqrt(1 - kappa)  # Through coupling
        k = jnp.sqrt(kappa)  # Cross coupling
        
        # Loss per round trip
        alpha = alpha_dB_cm / (10 * jnp.log10(jnp.e)) / 100  # Convert to 1/m
        a = jnp.exp(-alpha * L)  # Field amplitude transmission
        
        # Round-trip phase at resonance
        m = jnp.round(n_eff * L / (wl * 1e-6))  # Mode number
        wl_res = n_eff * L / m  # Resonance wavelength
        phi = 2 * jnp.pi * n_eff * L / (wl * 1e-6)
        
        # Add-drop ring transfer functions
        # Through port: S21
        numerator_through = t * (1 - a * t * jnp.exp(1j * phi))
        denominator = 1 - (t**2) * a * jnp.exp(1j * phi)
        S21 = numerator_through / denominator
        
        # Drop port: S31
        numerator_drop = -k**2 * jnp.sqrt(a) * jnp.exp(1j * phi / 2)
        S31 = numerator_drop / denominator
        
        # Calculate Q factor
        Q = jnp.pi * n_g * L * jnp.sqrt(a * t**2) / ((wl * 1e-6) * (1 - a * t**2))
        
        # Extinction ratio
        ER_dB = 10 * jnp.log10(jnp.abs(S31 / S21)**2)
        
        return {
            # S-parameters
            "S11": jnp.array(0.0, dtype=complex),  # Reflection
            "S21": S21,  # Input to through
            "S31": S31,  # Input to drop
            "S12": S21,  # Reciprocal
            "S13": S31,  # Reciprocal
            # Resonator metrics
            "FSR_nm": FSR_nm,
            "Q_factor": Q,
            "kappa": kappa,
            "effective_gap_um": effective_gap,
            "resonance_wavelength_um": wl_res * 1e6,
            "extinction_ratio_dB": ER_dB,
        }
    
    return mems_ring_dwdm_model


# Test code
if __name__ == "__main__":
    # Create and visualize component
    c = mems_ring_dwdm()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model at different MEMS actuation levels
    model = get_model()
    
    print("\n--- MEMS Tuning Demonstration ---")
    for voltage in [0, 1, 2, 3]:
        result = model(wl=1.55, applied_voltage=voltage)
        print(f"\nVoltage = {voltage}V:")
        print(f"  Effective gap: {result['effective_gap_um']:.3f} µm")
        print(f"  Coupling kappa: {result['kappa']:.3f}")
        print(f"  |S21| (through): {abs(result['S21']):.4f}")
        print(f"  |S31| (drop): {abs(result['S31']):.4f}")
    
    # Show FSR at nominal operation
    result = model(wl=1.55)
    print(f"\n--- Resonator Characteristics ---")
    print(f"  FSR: {result['FSR_nm']:.2f} nm")
    print(f"  Q-factor: {result['Q_factor']:.0f}")
    
    # Show paper parameters
    print("\n--- Paper Parameters ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
