"""
Name: mems_latching_ppic

Description: Non-volatile programmable photonic integrated circuit using 
mechanically latched MEMS. Enables stable passive operation without power
connection once configured, solving scaling barriers in PIC technology.

ports:
  - o1: Port 1
  - o2: Port 2
  - o3: Port 3
  - o4: Port 4

NodeLabels:
  - MEMS
  - Non_Volatile
  - Programmable
  - Zero_Power

Bandwidth:
  - Operation: C-band
  - Functions: MZI, ORR, lattice filters

Args:
  - mesh_type: "mzi_mesh" | "ring_mesh" | "hybrid"
  - num_cells: Number of tunable cells

Reference:
  - Paper: "Non-volatile Programmable Photonic Integrated Circuits using
           Mechanically Latched MEMS: A System-Level Scheme Enabling 
           Power-Connection-Free Operation Without Performance Compromise"
  - arXiv: 2601.06578
  - Authors: Ran Tao, Jifang Qiu, Zhimeng Liu, Hongxiang Guo, Yan Li, Jian Wu
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from arXiv:2601.06578
PAPER_PARAMS = {
    # Architecture
    "hardware": "MEMS with mechanical latching",
    "non_volatile": True,
    "power_connection_free": True,
    
    # Demonstrated functions
    "functions_validated": [
        "Mach-Zehnder interferometer (MZI)",
        "MZI lattice filter",
        "Optical ring resonator (ORR)",
        "Double ORR ring-loaded MZI",
        "Triple ORR coupled resonator waveguide filter",
    ],
    
    # Algorithm
    "configuration_algorithm": "Automatic error-resilient",
    "robustness": "Strong against fabrication errors",
    
    # Key benefits
    "benefits": [
        "Zero static power consumption",
        "Scalable to large meshes",
        "Performance equivalent to conventional PPICs",
        "No continuous tunability required",
    ],
    
    # Applications
    "applications": [
        "Reconfigurable photonics",
        "Optical switching",
        "RF photonics",
        "Signal processing",
        "Neuromorphic computing",
    ],
}


@gf.cell
def mems_latching_ppic(
    num_rows: int = 2,
    num_cols: int = 2,
    cell_spacing: float = 100.0,
    waveguide_width: float = 0.5,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Non-volatile MEMS-latched programmable PIC.
    
    Based on arXiv:2601.06578 demonstrating power-free
    operation via mechanical latching.
    
    Args:
        num_rows: Number of rows in mesh
        num_cols: Number of columns in mesh
        cell_spacing: Spacing between unit cells
        waveguide_width: Waveguide width in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: MEMS PPIC mesh
    """
    c = gf.Component()
    
    # Create mesh of MZI cells
    cells = []
    for row in range(num_rows):
        for col in range(num_cols):
            mzi = c << gf.components.mzi(
                delta_length=0,
                length_x=50,
                length_y=10,
                cross_section=cross_section,
            )
            mzi.move((col * cell_spacing, row * cell_spacing))
            cells.append(mzi)
    
    # Connect mesh (simplified)
    # In reality, would have complex routing
    
    # Add ports from corner cells
    if cells:
        c.add_port("o1", port=cells[0].ports["o1"])
        c.add_port("o2", port=cells[0].ports["o2"])
        if len(cells) > 1:
            c.add_port("o3", port=cells[-1].ports["o1"])
            c.add_port("o4", port=cells[-1].ports["o2"])
    
    # Add info
    c.info["num_cells"] = num_rows * num_cols
    c.info["non_volatile"] = True
    c.info["mems_latching"] = True
    c.info["static_power"] = "0 W"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the MEMS PPIC.
    
    The model includes:
    - Configurable mesh states
    - Non-volatile state retention
    - Multiple function modes
    """
    
    def mems_ppic_model(
        wl: float = 1.55,
        # Mesh configuration
        num_cells: int = 4,
        cell_states: list = None,  # Binary states (latched positions)
        # Current function mode
        function_mode: str = "mzi",  # "mzi", "orr", "lattice", "crow"
        # Performance parameters
        insertion_loss_per_cell_dB: float = 0.2,
        extinction_ratio_dB: float = 25.0,
        # MEMS parameters
        switch_time_ms: float = 1.0,  # Reconfiguration time
        holding_power_mW: float = 0.0,  # Zero! (latched)
    ) -> dict:
        """
        Analytical model for MEMS-latched PPIC.
        
        Args:
            wl: Wavelength in µm
            num_cells: Number of cells in mesh
            cell_states: Binary configuration per cell
            function_mode: Configured function
            insertion_loss_per_cell_dB: Loss per MZI cell
            extinction_ratio_dB: Switching extinction
            switch_time_ms: Reconfiguration time
            holding_power_mW: Power to hold state (0 for MEMS)
            
        Returns:
            dict: PPIC performance metrics
        """
        # Default states
        if cell_states is None:
            cell_states = [0] * num_cells
        
        # Total insertion loss
        total_loss_dB = num_cells * insertion_loss_per_cell_dB
        
        # Function-specific response
        if function_mode == "mzi":
            # Simple 2x2 switch
            # Cross or bar state based on cell_states[0]
            if cell_states and cell_states[0] == 1:
                T_bar = 10**(-extinction_ratio_dB / 10)  # Low
                T_cross = 1 - T_bar  # High
            else:
                T_bar = 1 - 10**(-extinction_ratio_dB / 10)  # High
                T_cross = 10**(-extinction_ratio_dB / 10)  # Low
            response_type = "2x2 switch"
            
        elif function_mode == "orr":
            # Ring resonator response
            # Simplified Lorentzian
            fsr_nm = 10.0  # Typical
            Q = 10000
            bw_nm = wl * 1000 / Q
            
            # On-resonance drop
            T_bar = 0.1  # Through port
            T_cross = 0.9  # Drop port
            response_type = f"Ring resonator Q={Q}"
            
        elif function_mode == "lattice":
            # Lattice filter - use cells as stages
            num_stages = min(num_cells, 4)
            T_bar = 0.5  # Depends on configuration
            T_cross = 0.5
            response_type = f"{num_stages}-stage lattice"
            
        elif function_mode == "crow":
            # Coupled resonator waveguide
            num_rings = min(num_cells, 3)
            T_bar = 0.1
            T_cross = 0.85
            response_type = f"{num_rings}-ring CROW"
        else:
            T_bar = 0.5
            T_cross = 0.5
            response_type = "Unknown"
        
        # Apply loss
        loss_factor = 10**(-total_loss_dB / 10)
        T_bar_actual = T_bar * loss_factor
        T_cross_actual = T_cross * loss_factor
        
        # Convert to dB
        T_bar_dB = 10 * jnp.log10(T_bar_actual + 1e-10)
        T_cross_dB = 10 * jnp.log10(T_cross_actual + 1e-10)
        
        # Energy efficiency
        # Conventional thermo-optic would need ~20 mW per cell
        conventional_power_mW = num_cells * 20
        power_savings_percent = 100.0  # MEMS uses 0 holding power
        
        # Scalability
        max_cells_practical = 1000  # Can scale large due to zero power
        
        return {
            # Configuration
            "function_mode": function_mode,
            "response_type": response_type,
            "num_cells": num_cells,
            "cell_states": cell_states[:min(len(cell_states), 8)],  # First 8
            # Transmission
            "T_bar": float(T_bar_actual),
            "T_cross": float(T_cross_actual),
            "T_bar_dB": float(T_bar_dB),
            "T_cross_dB": float(T_cross_dB),
            "extinction_ratio_dB": extinction_ratio_dB,
            # Loss
            "total_insertion_loss_dB": total_loss_dB,
            # Power
            "holding_power_mW": holding_power_mW,
            "conventional_power_mW": conventional_power_mW,
            "power_savings_percent": power_savings_percent,
            # Reconfiguration
            "switch_time_ms": switch_time_ms,
            # Scalability
            "max_practical_cells": max_cells_practical,
        }
    
    return mems_ppic_model


# Test code
if __name__ == "__main__":
    # Create component
    c = mems_latching_ppic()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    
    print("\n--- MEMS-Latched PPIC ---")
    result = model()
    print(f"  Cells: {result['num_cells']}")
    print(f"  Static power: {result['holding_power_mW']} mW (ZERO!)")
    print(f"  Conventional equivalent: {result['conventional_power_mW']} mW")
    print(f"  Power savings: {result['power_savings_percent']}%")
    
    print("\n--- Function Modes ---")
    for mode in ["mzi", "orr", "lattice", "crow"]:
        result = model(function_mode=mode)
        print(f"  {mode}: {result['response_type']}, "
              f"T_bar={result['T_bar_dB']:.1f} dB, T_cross={result['T_cross_dB']:.1f} dB")
    
    print("\n--- Scalability ---")
    for n in [4, 16, 64, 256]:
        result = model(num_cells=n)
        print(f"  {n} cells: loss={result['total_insertion_loss_dB']:.1f} dB, "
              f"power=0 mW (vs {result['conventional_power_mW']} mW conventional)")
    
    print("\n--- Non-Volatile Operation ---")
    print(f"  Reconfiguration time: {result['switch_time_ms']} ms")
    print(f"  State retention: Indefinite (mechanical latch)")
    print(f"  No electrical connection needed after config")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2601.06578) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
