"""
Name: midir_gas_sensor

Description: Mid-infrared MMI-based multispecies gas sensor using chalcogenide waveguides.
Features 1x2 MMI wavelength multiplexer for simultaneous detection of multiple gas species
through their characteristic absorption fingerprints in the mid-IR spectral region.

ports:
  - o1: Input port
  - o2: Output channel 1 (gas species 1)
  - o3: Output channel 2 (gas species 2)

NodeLabels:
  - MidIR_Sensor
  - Gas_Sensor
  - Chalcogenide

Bandwidth:
  - Mid-infrared (3-10 µm typical)
  - Multi-species sensing windows

Args:
  - mmi_width: MMI width in µm
  - mmi_length: MMI length in µm
  - sensing_length: Exposed sensing section length in µm

Reference:
  - Paper: "Design of a multimode interferometer-based mid-infrared multispecies gas sensor"
  - IEEE Sensors Journal, 2020
  - Authors: L. Bodiou, Y. Dumeige et al.
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from IEEE Sensors Journal 2020
PAPER_PARAMS = {
    # Platform
    "platform": "Chalcogenide glass",
    "material": "Ge-Se-Te or Ge-Sb-Se",
    "substrate": "Silicon or CaF2",
    
    # Spectral range
    "wavelength_range_um": "3-10",
    "target_bands": {
        "CO2": "4.26 µm",
        "CH4": "3.31 µm",
        "N2O": "4.47 µm",
        "CO": "4.67 µm",
    },
    
    # MMI design
    "mmi_type": "1x2 wavelength demultiplexer",
    "output_channels": 2,
    
    # Sensing
    "sensing_mechanism": "Evanescent field absorption",
    "interaction_length_mm": "1-10",
    
    # Performance
    "detection_limit_ppm": "sub-ppm achievable",
    "response_time_s": "Real-time capable",
    
    # Applications
    "applications": [
        "Environmental monitoring",
        "Industrial safety",
        "Breath analysis",
        "Atmospheric sensing",
    ],
}


@gf.cell
def midir_gas_sensor(
    mmi_width: float = 50.0,
    mmi_length: float = 500.0,
    sensing_length: float = 5000.0,
    waveguide_width: float = 5.0,
    taper_length: float = 100.0,
    output_gap: float = 20.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Mid-IR MMI-based multispecies gas sensor.
    
    Based on IEEE Sensors Journal 2020 demonstrating
    chalcogenide MMI for gas detection.
    
    Args:
        mmi_width: MMI width in µm
        mmi_length: MMI length in µm
        sensing_length: Sensing region length in µm
        waveguide_width: Waveguide width in µm
        taper_length: Taper length in µm
        output_gap: Gap between outputs in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: Mid-IR gas sensor
    """
    c = gf.Component()
    
    # Create MMI demultiplexer
    mmi = c << gf.components.mmi1x2(
        width=waveguide_width,
        width_mmi=mmi_width,
        length_mmi=mmi_length,
        gap_mmi=output_gap,
        cross_section=cross_section,
    )
    
    # Add sensing waveguides after each output
    for i, port in enumerate(["o2", "o3"]):
        sensing_wg = c << gf.components.straight(
            length=sensing_length,
            cross_section=cross_section,
        )
        sensing_wg.connect("o1", mmi.ports[port])
    
    # Add ports
    c.add_port("o1", port=mmi.ports["o1"])
    c.add_port("o2", center=(sensing_length + mmi_length, 0), orientation=0, width=waveguide_width)
    c.add_port("o3", center=(sensing_length + mmi_length, output_gap), orientation=0, width=waveguide_width)
    
    # Add info
    c.info["wavelength_range"] = "3-10 µm"
    c.info["material"] = "Chalcogenide"
    c.info["sensing_length_um"] = sensing_length
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the mid-IR gas sensor.
    
    The model includes:
    - MMI wavelength demultiplexing
    - Evanescent field interaction
    - Beer-Lambert absorption
    """
    
    def midir_gas_sensor_model(
        wl: float = 4.26,  # µm, CO2 absorption
        mmi_width_um: float = 50.0,
        mmi_length_um: float = 500.0,
        sensing_length_mm: float = 5.0,
        # Waveguide parameters
        n_core: float = 2.5,  # Chalcogenide
        n_clad: float = 1.0,  # Air sensing region
        waveguide_width_um: float = 5.0,
        # Gas parameters
        gas_concentration_ppm: float = 400.0,  # e.g., atmospheric CO2
        absorption_cross_section: float = 1e-18,  # cm² per molecule
        # Channel selection
        channel: int = 1,  # 1 or 2
    ) -> dict:
        """
        Analytical model for mid-IR gas sensor.
        
        Args:
            wl: Wavelength in µm
            mmi_width_um: MMI width in µm
            mmi_length_um: MMI length in µm
            sensing_length_mm: Sensing region length in mm
            n_core: Core refractive index (chalcogenide)
            n_clad: Cladding index (air)
            waveguide_width_um: Waveguide width in µm
            gas_concentration_ppm: Gas concentration in ppm
            absorption_cross_section: Molecular absorption cross-section
            channel: Output channel (1 or 2)
            
        Returns:
            dict: S-parameters and sensor metrics
        """
        # MMI beat length for mid-IR
        n_eff = n_core * 0.95  # Approximate effective index
        W_eff = mmi_width_um + wl / (n_core * jnp.pi)
        L_pi = 4 * n_eff * W_eff**2 / (3 * wl)
        
        # MMI splitting (wavelength dependent)
        # Channel 1 gets wavelength λ1, Channel 2 gets λ2
        wl_design = 4.0  # Design wavelength
        wl_spacing = 0.5  # Channel spacing µm
        
        # Splitting ratio depends on wavelength
        phase_error = 2 * jnp.pi * (wl - wl_design) / wl_spacing * mmi_length_um / L_pi
        
        if channel == 1:
            eta_channel = 0.5 * (1 + jnp.cos(phase_error))
        else:
            eta_channel = 0.5 * (1 - jnp.cos(phase_error))
        
        # Evanescent field fraction
        # Simplified: fraction of mode extending into cladding
        V = 2 * jnp.pi / wl * waveguide_width_um / 2 * jnp.sqrt(n_core**2 - n_clad**2)
        gamma = jnp.exp(-V / 2)  # Approximate evanescent decay
        
        # Confinement factor (fraction of power in sensing region)
        Gamma = 0.1 + 0.4 * gamma  # 10-50% typical for mid-IR
        
        # Beer-Lambert absorption
        # Convert ppm to molecules/cm³ (at STP)
        molecules_per_cm3 = gas_concentration_ppm * 2.687e19 / 1e6
        
        # Absorption coefficient
        alpha_gas = absorption_cross_section * molecules_per_cm3  # cm^-1
        
        # Effective absorption with confinement factor
        alpha_eff = alpha_gas * Gamma
        
        # Sensing path length
        sensing_length_cm = sensing_length_mm / 10
        
        # Transmission through sensing region
        T_gas = jnp.exp(-alpha_eff * sensing_length_cm)
        
        # Propagation loss (chalcogenide)
        alpha_prop = 0.5  # dB/cm typical
        T_prop = 10 ** (-alpha_prop * sensing_length_cm / 10)
        
        # Total transmission
        T_total = eta_channel * T_gas * T_prop
        
        # Sensitivity (dT/dc)
        sensitivity = -T_total * Gamma * absorption_cross_section * sensing_length_cm * 2.687e19 / 1e6
        
        # Detection limit estimate (assuming SNR > 1)
        min_detectable_absorption = 0.01  # 1% change
        lod_ppm = min_detectable_absorption / (Gamma * absorption_cross_section * 
                                                 sensing_length_cm * 2.687e19 / 1e6 + 1e-20)
        
        return {
            # Transmission
            "T_channel": eta_channel,
            "T_gas_absorption": T_gas,
            "T_propagation": T_prop,
            "T_total": T_total,
            # Absorption
            "alpha_gas_per_cm": alpha_gas,
            "alpha_effective_per_cm": alpha_eff,
            "absorption_dB": -10 * jnp.log10(T_gas + 1e-10),
            # Sensor metrics
            "confinement_factor": Gamma,
            "sensitivity_per_ppm": jnp.abs(sensitivity),
            "LOD_ppm": lod_ppm,
            # MMI metrics
            "L_pi_um": L_pi,
            "channel": channel,
        }
    
    return midir_gas_sensor_model


# Test code
if __name__ == "__main__":
    # Create component
    c = midir_gas_sensor()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    
    print("\n--- Mid-IR Gas Sensor: CO2 Detection ---")
    result = model(
        wl=4.26,  # CO2 absorption band
        gas_concentration_ppm=400,
        sensing_length_mm=5.0,
        channel=1
    )
    print(f"  Wavelength: 4.26 µm (CO2)")
    print(f"  Concentration: 400 ppm")
    print(f"  Gas absorption: {result['absorption_dB']:.2f} dB")
    print(f"  Total transmission: {result['T_total']*100:.1f}%")
    print(f"  Detection limit: {result['LOD_ppm']:.1f} ppm")
    
    # Concentration sweep
    print("\n--- Absorption vs Concentration ---")
    for conc in [100, 400, 1000, 5000, 10000]:
        result = model(wl=4.26, gas_concentration_ppm=conc)
        print(f"  {conc:5d} ppm: Abs = {result['absorption_dB']:.2f} dB, "
              f"T = {result['T_gas_absorption']*100:.1f}%")
    
    # Multi-species (different wavelengths)
    print("\n--- Multi-Species Detection ---")
    gases = [("CO2", 4.26), ("CH4", 3.31), ("CO", 4.67), ("N2O", 4.47)]
    for gas, wl in gases:
        result = model(wl=wl, gas_concentration_ppm=100)
        print(f"  {gas:4s} @ {wl} µm: Abs = {result['absorption_dB']:.3f} dB")
    
    # Paper parameters
    print("\n--- Paper Parameters (IEEE Sensors 2020) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
