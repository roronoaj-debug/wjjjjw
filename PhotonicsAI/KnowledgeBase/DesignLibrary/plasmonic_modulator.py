"""
Name: plasmonic_modulator

Description: Ultra-compact silicon-plasmonic hybrid electro-optic modulator utilizing 
metal-insulator-silicon nanoplasmonic waveguides. Features sub-micron device lengths 
with high modulation bandwidth enabled by surface plasmon polariton (SPP) field 
enhancement near the metal interface.

ports:
  - o1: Optical input
  - o2: Optical output

NodeLabels:
  - Plasmonic_MZM
  - Hybrid_Modulator
  - Nanoplasmonic_EOM

Bandwidth:
  - >100 GHz (sub-RC limited)
  - C-band (1550 nm)

Args:
  - device_length: Plasmonic modulator length in µm (default: 10)
  - gap_width: Metal-insulator gap width in nm (default: 50)
  - silicon_width: Silicon core width in nm (default: 300)

Reference:
  - Paper: "Ultracompact Si electro-optic modulator based on horizontal 
            Cu-insulator-Si-insulator-Cu nanoplasmonic waveguide"
  - IEEE: 6532850
  - Authors: Shiyang Zhu, G.Q. Lo, D.L. Kwong
  - Year: 2013
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from IEEE 6532850
PAPER_PARAMS = {
    # Architecture
    "modulator_type": "Silicon-Plasmonic Hybrid MZM",
    "waveguide": "Horizontal Cu-insulator-Si-insulator-Cu nanoplasmonic",
    
    # Structure
    "metal": "Copper (Cu)",
    "insulator": "SiO2 or Al2O3",
    "core": "Silicon",
    
    # Geometry
    "gap_width_nm": 50,  # Metal-insulator gap
    "silicon_width_nm": 300,
    "device_length_um": 10,  # Ultra-compact
    
    # Key advantages
    "advantages": [
        "Ultra-compact footprint",
        "High field confinement in gap",
        "Enhanced modulation efficiency",
        "CMOS compatible materials",
    ],
    
    # Performance
    "bandwidth_GHz": ">100",  # Limited by RC
    
    # Operating principle
    "mechanism": "Plasma dispersion effect + plasmonic field enhancement",
    
    # Wavelength
    "wavelength_band": "C-band",
}


@gf.cell
def plasmonic_modulator(
    device_length: float = 10.0,
    gap_width: float = 0.05,
    silicon_width: float = 0.3,
    taper_length: float = 5.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Silicon-Plasmonic hybrid electro-optic modulator.
    
    Based on IEEE 6532850 demonstrating ultra-compact modulator
    using Cu-insulator-Si-insulator-Cu nanoplasmonic waveguide.
    
    Args:
        device_length: Plasmonic modulator length in µm
        gap_width: Metal-insulator gap width in µm
        silicon_width: Silicon core width in µm
        taper_length: Si-plasmonic taper length in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: Plasmonic modulator with optical ports
    """
    c = gf.Component()
    
    # Input taper (Si to plasmonic)
    taper_in = c << gf.components.taper(
        length=taper_length,
        width1=0.5,
        width2=silicon_width,
        cross_section=cross_section,
    )
    
    # Plasmonic section (represented as narrow waveguide)
    plasmonic = c << gf.components.straight(
        length=device_length,
        width=silicon_width,
        cross_section=cross_section,
    )
    plasmonic.connect("o1", taper_in.ports["o2"])
    
    # Output taper (plasmonic to Si)
    taper_out = c << gf.components.taper(
        length=taper_length,
        width1=silicon_width,
        width2=0.5,
        cross_section=cross_section,
    )
    taper_out.connect("o1", plasmonic.ports["o2"])
    
    # Add ports
    c.add_port("o1", port=taper_in.ports["o1"])
    c.add_port("o2", port=taper_out.ports["o2"])
    
    # Add info
    c.info["device_length_um"] = device_length
    c.info["gap_width_nm"] = gap_width * 1000
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the plasmonic modulator.
    
    The model includes:
    - Plasmonic field enhancement
    - Plasma dispersion effect
    - Metal absorption loss
    """
    
    def plasmonic_modulator_model(
        wl: float = 1.55,
        device_length_um: float = 10.0,
        gap_width_nm: float = 50.0,
        silicon_width_nm: float = 300.0,
        applied_voltage: float = 0.0,
        carrier_concentration: float = 1e18,
        propagation_loss_dB_um: float = 0.1,
    ) -> dict:
        """
        Analytical model for silicon-plasmonic hybrid modulator.
        
        Args:
            wl: Wavelength in µm
            device_length_um: Modulator length in µm
            gap_width_nm: Metal-insulator gap in nm
            silicon_width_nm: Silicon core width in nm
            applied_voltage: Applied voltage in V
            carrier_concentration: Free carrier concentration in cm⁻³
            propagation_loss_dB_um: Plasmonic propagation loss in dB/µm
            
        Returns:
            dict: S-parameters and modulator metrics
        """
        # Physical constants
        e = 1.6e-19  # Electron charge
        m_e = 9.1e-31  # Electron mass
        c = 3e8  # Speed of light
        
        # Effective indices
        n_si = 3.48
        n_metal_real = 0.1  # Real part of Cu permittivity at optical frequencies
        
        # Plasmonic field enhancement factor
        # Smaller gap → higher enhancement
        enhancement = 1.0 + (100 / gap_width_nm) ** 0.5
        
        # Free carrier effect (plasma dispersion)
        # Δn = -8.8e-22 * ΔN - 8.5e-18 * ΔP^0.8
        delta_N = carrier_concentration * (applied_voltage / 1.0)  # Simple model
        delta_n_fc = -8.8e-22 * delta_N
        
        # Total effective index change (enhanced by plasmonic confinement)
        delta_n_eff = enhancement * delta_n_fc
        
        # Phase shift
        device_length = device_length_um * 1e-6  # m
        delta_phi = 2 * jnp.pi * delta_n_eff * device_length / (wl * 1e-6)
        
        # Propagation loss (higher for plasmonic)
        total_loss_dB = propagation_loss_dB_um * device_length_um
        transmission = 10 ** (-total_loss_dB / 10)
        
        # Field amplitude
        t_field = jnp.sqrt(transmission)
        
        # S-parameters for MZM at quadrature
        phi_bias = jnp.pi / 2
        total_phi = phi_bias + delta_phi
        
        S21 = t_field * jnp.cos(total_phi / 2) * jnp.exp(1j * total_phi / 2)
        S11 = 0.01 * jnp.exp(1j * 2 * total_phi)  # Low reflection
        
        # Vπ estimation (for comparison)
        # At Vπ: delta_phi = π
        v_pi = jnp.abs(jnp.pi * wl * 1e-6 / (2 * jnp.pi * enhancement * 8.8e-22 * carrier_concentration * device_length))
        
        return {
            # S-parameters
            "S11": S11,
            "S21": S21,
            "S12": S21,
            "S22": S11,
            # Modulator metrics
            "delta_n_eff": delta_n_eff,
            "delta_phi": delta_phi,
            "transmission": transmission,
            "insertion_loss_dB": total_loss_dB,
            "field_enhancement": enhancement,
            "V_pi": v_pi,
        }
    
    return plasmonic_modulator_model


# Test code
if __name__ == "__main__":
    # Create and visualize component
    c = plasmonic_modulator()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=1.55, applied_voltage=0)
    
    print("\n--- Plasmonic Modulator Characteristics ---")
    print(f"  Field enhancement: {result['field_enhancement']:.2f}x")
    print(f"  Insertion loss: {result['insertion_loss_dB']:.2f} dB")
    print(f"  Vπ: {result['V_pi']:.2f} V")
    
    # Gap width effect
    print("\n--- Gap Width Effect on Enhancement ---")
    for gap in [30, 50, 80, 100, 150]:
        result = model(wl=1.55, gap_width_nm=gap)
        print(f"  Gap={gap} nm: Enhancement = {result['field_enhancement']:.2f}x")
    
    # Paper parameters
    print("\n--- Paper Parameters (IEEE 6532850) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
