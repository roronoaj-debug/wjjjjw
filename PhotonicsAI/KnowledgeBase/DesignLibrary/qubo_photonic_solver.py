"""
Name: qubo_photonic_solver

Description: 16-channel programmable photonic solver for quadratic unconstrained binary 
optimization (QUBO) problems on silicon photonics. Features high-speed electro-optic 
modulators, thermo-optic phase shifters, and photodetectors for optical vector-matrix 
multiplication (OVMM) at ~2 TFLOP/s computing speed.

ports:
  - input_1 to input_16: 16 optical input channels
  - output_1 to output_16: 16 photodetector outputs

NodeLabels:
  - QUBO_Solver
  - Photonic_Computing
  - Optical_VMM

Bandwidth:
  - C-band (1550 nm)
  - Multi-GHz modulation

Args:
  - num_channels: Number of computing channels (default 16)
  - mzm_length: Modulator length in µm
  - ps_length: Phase shifter length in µm

Reference:
  - Paper: "16-channel Photonic Solver for Optimization Problems on a Silicon Chip"
  - arXiv:2407.04713
  - Authors: Jiayi Ouyang et al.
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from arXiv:2407.04713
PAPER_PARAMS = {
    # Platform
    "platform": "Silicon-on-Insulator (SOI)",
    "architecture": "Hybrid optoelectronic",
    
    # Scale
    "num_channels": 16,
    "problem_type": "QUBO (Quadratic Unconstrained Binary Optimization)",
    
    # Components integrated
    "components": [
        "High-speed electro-optic modulators",
        "Thermo-optic phase shifters",
        "Photodetectors",
        "Optical splitters/combiners",
    ],
    
    # Performance
    "computing_speed_TFLOPS": "~2",
    "operation": "Optical vector-matrix multiplication",
    
    # Key achievements
    "achievements": [
        "Largest programmable on-chip photonic solver reported",
        "16-dimensional QUBO problems solved",
        "High success probability",
    ],
    
    # Applications
    "applications": [
        "Combinatorial optimization",
        "Machine learning acceleration",
        "Ising machines",
        "Quantum-inspired computing",
    ],
}


@gf.cell
def qubo_photonic_solver(
    num_channels: int = 16,
    mzm_length: float = 500.0,
    ps_length: float = 100.0,
    channel_spacing: float = 25.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    16-channel photonic QUBO solver on SOI.
    
    Based on arXiv:2407.04713 demonstrating ~2 TFLOP/s 
    optical computing for optimization.
    
    Args:
        num_channels: Number of computing channels
        mzm_length: EO modulator length in µm
        ps_length: Phase shifter length in µm
        channel_spacing: Spacing between channels in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: QUBO photonic solver
    """
    c = gf.Component()
    
    # Create channel array (simplified representation)
    total_width = num_channels * channel_spacing
    
    for i in range(num_channels):
        y_pos = i * channel_spacing
        
        # Input waveguide
        wg_in = c << gf.components.straight(length=50, cross_section=cross_section)
        wg_in.move((0, y_pos))
        
        # Modulator section
        mod = c << gf.components.straight(length=mzm_length, cross_section=cross_section)
        mod.connect("o1", wg_in.ports["o2"])
        
        # Phase shifter
        ps = c << gf.components.straight(length=ps_length, cross_section=cross_section)
        ps.connect("o1", mod.ports["o2"])
        
        # Add input port
        c.add_port(f"input_{i+1}", port=wg_in.ports["o1"])
        c.add_port(f"output_{i+1}", port=ps.ports["o2"])
    
    # Add info
    c.info["num_channels"] = num_channels
    c.info["computing_speed"] = "~2 TFLOP/s"
    c.info["problem_type"] = "QUBO"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the photonic QUBO solver.
    
    The model includes:
    - Vector-matrix multiplication
    - MZM encoding
    - Heuristic cost function evaluation
    """
    
    def qubo_solver_model(
        wl: float = 1.55,
        num_channels: int = 16,
        # Weight matrix (NxN)
        Q_matrix: jnp.ndarray = None,  # QUBO matrix
        # Binary variables
        x_vector: jnp.ndarray = None,  # Binary solution vector
        # Hardware parameters
        mzm_Vpi: float = 5.0,  # V
        mzm_bandwidth_GHz: float = 10.0,
        ps_efficiency_mW: float = 20.0,  # mW/π
        pd_responsivity_A_W: float = 0.8,
    ) -> dict:
        """
        Analytical model for photonic QUBO solver.
        
        Args:
            wl: Wavelength in µm
            num_channels: Number of channels
            Q_matrix: NxN QUBO cost matrix
            x_vector: Binary solution vector
            mzm_Vpi: Modulator Vπ in V
            mzm_bandwidth_GHz: Modulator bandwidth
            ps_efficiency_mW: Phase shifter efficiency
            pd_responsivity_A_W: Photodetector responsivity
            
        Returns:
            dict: Computing results and metrics
        """
        # Default Q matrix (random symmetric)
        if Q_matrix is None:
            Q_matrix = jnp.eye(num_channels) * 0.5
        
        # Default x vector (all zeros)
        if x_vector is None:
            x_vector = jnp.zeros(num_channels)
        
        # QUBO cost function: E(x) = x^T Q x
        cost = jnp.dot(x_vector, jnp.dot(Q_matrix, x_vector))
        
        # Optical implementation
        # Each row of Q encoded by MZMs
        # Column multiplication via photodetection
        
        # Modulator encoding (amplitude from voltage)
        # Assume binary x encoded as optical amplitude
        optical_amplitudes = jnp.sqrt(x_vector)
        
        # Matrix-vector product (optical domain)
        # Output = sum of weighted inputs
        optical_outputs = jnp.dot(Q_matrix, optical_amplitudes)
        
        # Photodetection (square-law)
        detected_currents = pd_responsivity_A_W * optical_outputs**2
        
        # Total photocurrent (proportional to cost)
        total_current_uA = jnp.sum(detected_currents) * 1e6
        
        # Computing speed estimate
        # OVMM: N² MACs per iteration
        macs_per_op = num_channels ** 2
        iteration_time_ns = 1 / mzm_bandwidth_GHz  # Limited by modulator
        tflops = macs_per_op * 2 / (iteration_time_ns * 1e-9) / 1e12
        
        # Power consumption estimate
        static_power_mW = num_channels * ps_efficiency_mW * 0.5  # Average phase
        dynamic_power_mW = num_channels * (mzm_Vpi / 50)**2 * 1000  # RF power
        total_power_W = (static_power_mW + dynamic_power_mW) / 1000
        
        # Energy per operation
        energy_per_op_pJ = total_power_W * 1e12 / (tflops * 1e12)
        
        return {
            # QUBO result
            "cost_function": cost,
            "solution_vector": x_vector,
            "optical_outputs": optical_outputs,
            # Computing metrics
            "computing_speed_TFLOPS": tflops,
            "MACs_per_iteration": macs_per_op,
            # Power/energy
            "total_power_W": total_power_W,
            "energy_per_op_pJ": energy_per_op_pJ,
            # Hardware
            "detected_currents_uA": detected_currents,
            "total_photocurrent_uA": total_current_uA,
        }
    
    return qubo_solver_model


# Test code
if __name__ == "__main__":
    # Create component
    c = qubo_photonic_solver(num_channels=4)  # Smaller for visualization
    print(f"Component: {c.name}")
    print(f"Ports: {len([p for p in c.ports.keys()])}")
    
    # Test model
    model = get_model()
    
    print("\n--- QUBO Photonic Solver ---")
    
    # Simple 4x4 problem
    Q = jnp.array([
        [1, -1, 0, 0],
        [-1, 1, -1, 0],
        [0, -1, 1, -1],
        [0, 0, -1, 1],
    ], dtype=float)
    
    # Test different solutions
    print("\n--- Solution Space Exploration ---")
    solutions = [
        jnp.array([0, 0, 0, 0]),
        jnp.array([1, 0, 0, 0]),
        jnp.array([1, 0, 1, 0]),
        jnp.array([1, 1, 1, 1]),
    ]
    
    for x in solutions:
        result = model(num_channels=4, Q_matrix=Q, x_vector=x)
        print(f"  x={[int(xi) for xi in x]}: Cost = {result['cost_function']:.2f}")
    
    # Full 16-channel performance
    print("\n--- 16-Channel Performance ---")
    result = model(num_channels=16)
    print(f"  Computing speed: {result['computing_speed_TFLOPS']:.1f} TFLOP/s")
    print(f"  MACs per iteration: {result['MACs_per_iteration']}")
    print(f"  Power: {result['total_power_W']:.2f} W")
    print(f"  Energy efficiency: {result['energy_per_op_pJ']:.2f} pJ/op")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2407.04713) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
