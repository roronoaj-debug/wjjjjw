"""
Name: mems_latching_mzi

Description: Non-volatile programmable photonic MZI using mechanically latched MEMS actuators.
Enables power-connection-free stable operation once configured, eliminating static power 
consumption in programmable photonic integrated circuits.

ports:
  - o1: Input port 1
  - o2: Input port 2
  - o3: Output port 1
  - o4: Output port 2

NodeLabels:
  - MEMS_MZI
  - Non_Volatile_MZI
  - Programmable_MZI

Bandwidth:
  - C-band (1550 nm)
  - Broadband operation

Args:
  - arm_length: MZI arm length in µm
  - mems_gap: MEMS actuator gap in nm
  - num_levels: Number of discrete phase states

Reference:
  - Paper: "Non-volatile Programmable Photonic Integrated Circuits using 
            Mechanically Latched MEMS"
  - arXiv: 2601.06578
  - Authors: Ran Tao, Jifang Qiu, Zhimeng Liu, et al.
  - Year: 2026
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from arXiv:2601.06578
PAPER_PARAMS = {
    # Architecture
    "architecture": "Non-volatile PPIC with MEMS mechanical latching",
    "operation_mode": "Power-connection-free after configuration",
    
    # MEMS properties
    "mems_type": "Mechanically latched actuators",
    "latching_mechanism": "Bistable/multistable mechanical states",
    "non_volatile": True,
    "static_power": 0,  # Zero static power
    
    # Demonstrated functions
    "demonstrated_functions": [
        "Mach-Zehnder interferometer (MZI)",
        "MZI lattice filter",
        "Optical ring resonator (ORR)",
        "Double ORR ring-loaded MZI",
        "Triple ORR coupled resonator waveguide filter",
    ],
    
    # Configuration
    "configuration_method": "Error-resilient algorithm",
    "fabrication_tolerance": "Robust against errors",
    
    # Key features
    "features": [
        "Zero static power consumption",
        "Stable passive operation",
        "Equivalent performance to conventional PPICs",
        "Scalable architecture",
    ],
    
    # Applications
    "applications": [
        "Programmable photonic circuits",
        "Optical computing",
        "Reconfigurable filters",
        "Energy-efficient PICs",
    ],
}


@gf.cell
def mems_latching_mzi(
    arm_length: float = 200.0,
    delta_length: float = 0.0,
    mems_section_length: float = 50.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Non-volatile MEMS-latched MZI.
    
    Based on arXiv:2601.06578 demonstrating power-free
    programmable photonics with mechanical latching.
    
    Args:
        arm_length: MZI arm length in µm
        delta_length: Path length imbalance in µm
        mems_section_length: MEMS actuator section length in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: MEMS-latched MZI
    """
    c = gf.Component()
    
    # Create MZI structure
    mzi = c << gf.components.mzi(
        delta_length=delta_length,
        length_x=arm_length,
        cross_section=cross_section,
    )
    
    # Add ports
    c.add_port("o1", port=mzi.ports["o1"])
    c.add_port("o2", port=mzi.ports["o2"])
    
    # Add info
    c.info["arm_length_um"] = arm_length
    c.info["mems_section_um"] = mems_section_length
    c.info["non_volatile"] = True
    c.info["static_power_mW"] = 0
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the MEMS-latched MZI.
    
    The model includes:
    - Discrete phase states from MEMS positions
    - MZI transfer function
    - Non-volatile operation
    """
    
    def mems_latching_mzi_model(
        wl: float = 1.55,
        arm_length_um: float = 200.0,
        n_eff: float = 2.45,
        mems_state: int = 0,
        num_states: int = 8,
        phase_range: float = 2 * jnp.pi,
        insertion_loss_dB: float = 0.5,
    ) -> dict:
        """
        Analytical model for MEMS-latched MZI.
        
        Args:
            wl: Wavelength in µm
            arm_length_um: MZI arm length in µm
            n_eff: Effective refractive index
            mems_state: Current MEMS latched state (0 to num_states-1)
            num_states: Number of discrete MEMS states
            phase_range: Total phase range in radians
            insertion_loss_dB: Insertion loss in dB
            
        Returns:
            dict: S-parameters and MZI metrics
        """
        # Discrete phase from MEMS state
        phase_per_state = phase_range / (num_states - 1)
        delta_phi = mems_state * phase_per_state
        
        # Base phase from path length
        arm_length = arm_length_um * 1e-6  # m
        phi_base = 2 * jnp.pi * n_eff * arm_length / (wl * 1e-6)
        
        # Total phase difference between arms
        phi_total = delta_phi
        
        # MZI transfer function
        # Assuming 50:50 splitters
        loss = 10 ** (-insertion_loss_dB / 20)
        
        # Bar (through) port
        S31 = loss * jnp.cos(phi_total / 2) * jnp.exp(1j * phi_base)
        # Cross port
        S41 = loss * 1j * jnp.sin(phi_total / 2) * jnp.exp(1j * phi_base)
        
        # Power splitting
        P_bar = jnp.abs(S31)**2
        P_cross = jnp.abs(S41)**2
        
        # Splitting ratio
        splitting_ratio = P_cross / (P_bar + P_cross + 1e-10)
        
        # Equivalent thermal power saved
        # Typical thermo-optic phase shifter: ~25 mW for π shift
        equivalent_power_saved_mW = (delta_phi / jnp.pi) * 25
        
        return {
            # S-parameters
            "S31": S31,  # Bar
            "S41": S41,  # Cross
            "S13": S31,  # Reciprocal
            "S14": S41,
            # Powers
            "bar_power": P_bar,
            "cross_power": P_cross,
            "splitting_ratio": splitting_ratio,
            # Phase info
            "phase_state": mems_state,
            "phase_shift_rad": delta_phi,
            "phase_shift_deg": jnp.degrees(delta_phi),
            # Power saving
            "static_power_mW": 0.0,
            "equivalent_saved_power_mW": equivalent_power_saved_mW,
        }
    
    return mems_latching_mzi_model


# Test code
if __name__ == "__main__":
    # Create component
    c = mems_latching_mzi()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    print(f"Static power: {c.info['static_power_mW']} mW (non-volatile)")
    
    # Test model at different MEMS states
    model = get_model()
    
    print("\n--- MEMS States and Splitting Ratios ---")
    for state in range(8):
        result = model(mems_state=state, num_states=8)
        print(f"  State {state}: Phase = {result['phase_shift_deg']:.0f}°, "
              f"Split = {result['splitting_ratio']*100:.1f}%")
    
    # Power savings
    print("\n--- Power Savings vs Thermo-Optic ---")
    result = model(mems_state=4, num_states=8)  # π shift
    print(f"  π phase shift: 0 mW (MEMS) vs ~{result['equivalent_saved_power_mW']:.0f} mW (thermo-optic)")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2601.06578) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
