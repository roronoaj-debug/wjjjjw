"""
Name: soh_modulator

Description: Silicon-Organic-Hybrid (SOH) electro-optic modulator utilizing organic χ⁽²⁾ 
nonlinear materials infiltrated into silicon slot waveguides. SOH devices offer improved 
speed and energy efficiency compared to conventional silicon photonics modulators through 
the Pockels effect in organic electro-optic polymers.

ports:
  - o1: Optical input
  - o2: Optical output

NodeLabels:
  - SOH_Modulator
  - Slot_MZM

Bandwidth:
  - > 100 GHz (Pockels effect limited)
  - C-band (1550 nm)

Args:
  - slot_width: Slot width in nm (default: 120)
  - rail_width: Rail width in nm (default: 220)
  - arm_length: Modulator arm length in µm (default: 500)
  - r33: EO coefficient in pm/V (default: 150)

Reference:
  - Paper: "Physics to System-level Modeling of Silicon-organic-hybrid Nanophotonic Devices"
  - arXiv: 2401.10701
  - Authors: M. Moridsadat, M. Tamura, L. Chrostowski, et al.
  - Year: 2024
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from arXiv:2401.10701
PAPER_PARAMS = {
    # Architecture
    "modulator_type": "Silicon-Organic-Hybrid (SOH) MZM/MRM",
    "waveguide": "Slot waveguide",
    
    # Slot waveguide geometry
    "slot_width_nm": 120,  # Typical slot width
    "rail_width_nm": 220,  # Silicon rail width
    "rail_height_nm": 220,  # Standard SOI
    
    # Organic EO material
    "eo_material": "EO polymer (e.g., JRD1, SEO100)",
    "r33_pm_V": 150,  # Typical Pockels coefficient
    "n_polymer": 1.7,  # Refractive index of organic
    
    # Performance advantages over Si PN
    "advantages": [
        "Higher speed (pure Pockels effect)",
        "Lower energy consumption",
        "No carrier dynamics limitation",
    ],
    
    # Modulator configurations
    "configurations": ["Microring modulator (MRM)", "Mach-Zehnder modulator (MZM)"],
    
    # Applications
    "applications": [
        "Neuromorphic computing",
        "Data center interconnects",
        "Sensing",
    ],
    
    # Wavelength
    "wavelength_band": "C-band",
    
    # Modeling compatibility
    "eda_compatible": True,
    "effects_modeled": ["Pockels effect", "Kerr effect"],
}


@gf.cell
def soh_modulator(
    slot_width: float = 0.12,
    rail_width: float = 0.22,
    arm_length: float = 500.0,
    delta_length: float = 0.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Silicon-Organic-Hybrid (SOH) Mach-Zehnder Modulator.
    
    Based on arXiv:2401.10701 demonstrating physics-to-system-level
    modeling of SOH nanophotonic devices.
    
    Args:
        slot_width: Slot width in µm
        rail_width: Rail width in µm
        arm_length: Modulator arm length in µm
        delta_length: Path length difference in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: SOH MZM with optical ports
    """
    c = gf.Component()
    
    # Create MZI structure (representing SOH MZM)
    mzm = c << gf.components.mzi(
        delta_length=delta_length,
        length_x=arm_length,
        cross_section=cross_section,
    )
    
    # Add ports
    c.add_port("o1", port=mzm.ports["o1"])
    c.add_port("o2", port=mzm.ports["o2"])
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the SOH modulator.
    
    The model includes:
    - Pockels effect modulation (no carrier dynamics)
    - Slot waveguide field enhancement
    - Ultra-fast response
    """
    
    def soh_modulator_model(
        wl: float = 1.55,
        arm_length_um: float = 500.0,
        slot_width_nm: float = 120.0,
        rail_width_nm: float = 220.0,
        r33_pm_V: float = 150.0,
        n_eo: float = 1.7,
        applied_voltage: float = 0.0,
        electrode_gap_um: float = 0.5,
        insertion_loss_dB: float = 3.0,
    ) -> dict:
        """
        Analytical model for SOH electro-optic modulator.
        
        Args:
            wl: Wavelength in µm
            arm_length_um: Phase shifter length in µm
            slot_width_nm: Slot width in nm
            rail_width_nm: Silicon rail width in nm
            r33_pm_V: Pockels coefficient in pm/V
            n_eo: EO polymer refractive index
            applied_voltage: Applied voltage in V
            electrode_gap_um: Electrode gap in µm
            insertion_loss_dB: Optical insertion loss in dB
            
        Returns:
            dict: S-parameters and modulator metrics
        """
        # Physical constants
        c_light = 3e8
        
        # Convert to SI units
        arm_length = arm_length_um * 1e-6  # m
        slot_width = slot_width_nm * 1e-9  # m
        r33 = r33_pm_V * 1e-12  # m/V
        electrode_gap = electrode_gap_um * 1e-6  # m
        
        # Electric field in slot
        E_field = applied_voltage / electrode_gap  # V/m
        
        # Pockels effect index change
        # Δn = -0.5 * n³ * r33 * E
        delta_n = -0.5 * n_eo**3 * r33 * E_field
        
        # Field confinement factor in slot (approximate)
        # Higher confinement in narrow slots
        gamma = 0.3 + 0.1 * (150 / slot_width_nm)  # Simple model
        gamma = jnp.clip(gamma, 0.2, 0.8)
        
        # Effective index change
        delta_n_eff = gamma * delta_n
        
        # Phase shift
        delta_phi = 2 * jnp.pi * delta_n_eff * arm_length / (wl * 1e-6)
        
        # Vπ calculation
        # At Vπ: delta_phi = π
        v_pi = jnp.pi * electrode_gap * wl * 1e-6 / (jnp.pi * gamma * n_eo**3 * r33 * arm_length)
        
        # VπL product
        vpi_l_V_cm = v_pi * arm_length_um / 1e4
        
        # MZM transfer (at quadrature bias)
        phi_bias = jnp.pi / 2
        total_phi = phi_bias + delta_phi
        
        insertion_loss_linear = 10 ** (-insertion_loss_dB / 20)
        T_field = insertion_loss_linear * jnp.cos(total_phi / 2)
        
        S21 = T_field * jnp.exp(1j * total_phi / 2)
        
        # Bandwidth (limited by RC, not carrier dynamics)
        # SOH can achieve very high bandwidth
        bandwidth_GHz = 100.0  # Typical estimate
        
        return {
            # S-parameters
            "S11": jnp.array(0.0, dtype=complex),
            "S21": S21,
            "S12": S21,
            "S22": jnp.array(0.0, dtype=complex),
            # Modulator metrics
            "V_pi": v_pi,
            "VpiL_V_cm": vpi_l_V_cm,
            "delta_n": delta_n,
            "delta_phi": delta_phi,
            "transmission": jnp.abs(T_field) ** 2,
            "confinement_factor": gamma,
            "bandwidth_GHz": bandwidth_GHz,
        }
    
    return soh_modulator_model


# Test code
if __name__ == "__main__":
    # Create and visualize component
    c = soh_modulator()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=1.55, applied_voltage=0)
    
    print(f"\n--- SOH Modulator Characteristics ---")
    print(f"  Vπ: {result['V_pi']:.2f} V")
    print(f"  VπL: {result['VpiL_V_cm']:.3f} V·cm")
    print(f"  Confinement factor: {result['confinement_factor']:.2f}")
    
    # Modulation response
    print("\n--- Voltage Sweep ---")
    for voltage in [0, 1, 2, 3, 4]:
        result = model(wl=1.55, applied_voltage=voltage)
        print(f"  V={voltage}V: Δφ = {result['delta_phi']:.3f} rad, T = {result['transmission']:.3f}")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2401.10701) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
