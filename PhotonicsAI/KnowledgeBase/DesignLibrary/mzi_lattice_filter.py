"""
Name: mzi_lattice_filter

Description: Programmable MZI lattice filter for reconfigurable optical signal
processing. Uses cascaded Mach-Zehnder interferometers with tunable phase
shifters to implement arbitrary FIR and IIR filter responses.

ports:
  - o1: Input port
  - o2: Through output
  - o3: Cross output (if 2x2)

NodeLabels:
  - Lattice_Filter
  - Programmable
  - MZI_Cascade
  - DSP

Bandwidth:
  - FSR: Configurable via stage delays
  - Operation: C-band

Args:
  - num_stages: Number of MZI stages
  - stage_delay_um: Delay between stages in µm

Reference:
  - Multiple papers on programmable photonics and lattice filters
  - VTT, MIT, and other groups
  - Bloch sphere design methodology
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from multiple sources
PAPER_PARAMS = {
    # Architecture
    "topology": "Cascaded MZI lattice",
    "filter_type": "FIR (all pass) or IIR (with feedback)",
    
    # Programmability
    "phase_shifter_type": "Thermo-optic",
    "reconfigurable": True,
    "design_method": "Bloch sphere representation",
    
    # Typical specifications
    "arbitrary_splitting_ratios": True,
    "robust_to_fabrication_errors": True,
    
    # Implementations
    "platforms": [
        "Silicon photonics",
        "Silicon nitride",
        "Micron-scale thick SOI",
    ],
    
    # Applications
    "applications": [
        "Wavelength filtering",
        "WDM demultiplexing",
        "Programmable optical processing",
        "Neuromorphic photonics",
        "Optical equalizers",
    ],
}


@gf.cell
def mzi_lattice_filter(
    num_stages: int = 4,
    stage_delay_um: float = 100.0,
    mzi_length: float = 200.0,
    waveguide_width: float = 0.5,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Programmable MZI lattice filter.
    
    Based on various programmable photonics papers
    demonstrating reconfigurable optical filters.
    
    Args:
        num_stages: Number of MZI stages
        stage_delay_um: Differential delay per stage
        mzi_length: MZI arm length
        waveguide_width: Waveguide width in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: MZI lattice filter
    """
    c = gf.Component()
    
    # Create cascaded MZI stages
    prev_port_bar = None
    prev_port_cross = None
    
    for i in range(num_stages):
        mzi = c << gf.components.mzi(
            delta_length=stage_delay_um,
            length_x=mzi_length / 2,
            length_y=20,
            cross_section=cross_section,
        )
        mzi.movex(i * (mzi_length + 50))
        
        if i == 0:
            c.add_port("o1", port=mzi.ports["o1"])
        
        prev_port_bar = mzi.ports["o2"]
    
    # Add output port
    c.add_port("o2", port=prev_port_bar)
    
    # Add info
    c.info["num_stages"] = num_stages
    c.info["stage_delay"] = stage_delay_um
    c.info["filter_type"] = "Programmable lattice"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the MZI lattice filter.
    
    The model includes:
    - Multi-stage interference
    - Programmable phase control
    - Spectral response calculation
    """
    
    def mzi_lattice_filter_model(
        wl: float = 1.55,
        # Lattice parameters
        num_stages: int = 4,
        stage_delay_um: float = 100.0,
        # Phase settings for each stage (programmable)
        phase_shifts_rad: list = None,  # Phase shift per stage
        coupling_ratios: list = None,   # Coupling per coupler
        # Waveguide parameters
        n_eff: float = 2.45,
        n_g: float = 4.2,
        loss_dB_cm: float = 2.0,
    ) -> dict:
        """
        Analytical model for MZI lattice filter.
        
        Args:
            wl: Wavelength in µm
            num_stages: Number of MZI stages
            stage_delay_um: Differential delay per stage
            phase_shifts_rad: Phase settings per stage
            coupling_ratios: Power coupling ratio per coupler
            n_eff: Effective index
            n_g: Group index
            loss_dB_cm: Propagation loss
            
        Returns:
            dict: Filter performance metrics
        """
        # Default to uniform settings if not specified
        if phase_shifts_rad is None:
            phase_shifts_rad = [jnp.pi / 2] * num_stages
        if coupling_ratios is None:
            coupling_ratios = [0.5] * (num_stages + 1)
        
        # Free spectral range from stage delay
        fsr_nm = (wl * 1000)**2 / (n_g * stage_delay_um * 1000)
        fsr_GHz = 3e8 / (n_g * stage_delay_um * 1e-6) / 1e9
        
        # Phase per stage from wavelength
        base_phase = 2 * jnp.pi * n_eff * stage_delay_um / (wl * 1000)
        
        # Calculate transfer function using transfer matrix method
        # Start with identity matrix
        T_total = jnp.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex)
        
        for i in range(min(num_stages, len(phase_shifts_rad))):
            # Coupling matrix (directional coupler)
            k = jnp.sqrt(coupling_ratios[min(i, len(coupling_ratios)-1)])
            t = jnp.sqrt(1 - coupling_ratios[min(i, len(coupling_ratios)-1)])
            C = jnp.array([[t, 1j*k], [1j*k, t]], dtype=complex)
            
            # Phase matrix (delay + programmable phase)
            phi = base_phase + phase_shifts_rad[i]
            P = jnp.array([[jnp.exp(1j * phi), 0], [0, 1]], dtype=complex)
            
            # Multiply
            T_total = C @ P @ T_total
        
        # Final coupler
        k = jnp.sqrt(coupling_ratios[-1])
        t = jnp.sqrt(1 - coupling_ratios[-1])
        C_final = jnp.array([[t, 1j*k], [1j*k, t]], dtype=complex)
        T_total = C_final @ T_total
        
        # Through and cross transmission
        T_through = jnp.abs(T_total[0, 0])**2
        T_cross = jnp.abs(T_total[1, 0])**2
        
        # Convert to dB
        through_dB = 10 * jnp.log10(T_through + 1e-10)
        cross_dB = 10 * jnp.log10(T_cross + 1e-10)
        
        # Extinction ratio
        extinction_ratio_dB = jnp.abs(through_dB - cross_dB)
        
        # Loss
        total_length_cm = num_stages * stage_delay_um * 1e-4
        propagation_loss_dB = loss_dB_cm * total_length_cm
        
        # Phase response
        phase_through = jnp.angle(T_total[0, 0])
        phase_cross = jnp.angle(T_total[1, 0])
        
        # Group delay (from phase derivative)
        # Approximation: GD ~ num_stages * stage_delay / 2
        group_delay_ps = num_stages * n_g * stage_delay_um / (3e8) * 1e6
        
        return {
            # Transmission
            "through_transmission": float(T_through),
            "cross_transmission": float(T_cross),
            "through_dB": float(through_dB),
            "cross_dB": float(cross_dB),
            "extinction_ratio_dB": float(extinction_ratio_dB),
            # Spectral
            "fsr_nm": float(fsr_nm),
            "fsr_GHz": float(fsr_GHz),
            # Phase
            "phase_through_rad": float(phase_through),
            "phase_cross_rad": float(phase_cross),
            "group_delay_ps": float(group_delay_ps),
            # Losses
            "propagation_loss_dB": float(propagation_loss_dB),
            # Configuration
            "num_stages": num_stages,
            "stage_delay_um": stage_delay_um,
        }
    
    return mzi_lattice_filter_model


# Test code
if __name__ == "__main__":
    # Create component
    c = mzi_lattice_filter()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    
    print("\n--- MZI Lattice Filter ---")
    result = model()
    print(f"  Stages: {result['num_stages']}")
    print(f"  Stage delay: {result['stage_delay_um']} µm")
    print(f"  FSR: {result['fsr_GHz']:.1f} GHz ({result['fsr_nm']:.2f} nm)")
    
    print("\n--- Transmission ---")
    print(f"  Through: {result['through_dB']:.2f} dB")
    print(f"  Cross: {result['cross_dB']:.2f} dB")
    print(f"  ER: {result['extinction_ratio_dB']:.1f} dB")
    
    print("\n--- Phase Response ---")
    print(f"  Through phase: {result['phase_through_rad']:.2f} rad")
    print(f"  Cross phase: {result['phase_cross_rad']:.2f} rad")
    print(f"  Group delay: {result['group_delay_ps']:.2f} ps")
    
    # Different configurations
    print("\n--- Configurable Responses ---")
    configs = [
        ([0, 0, 0, 0], "All zeros"),
        ([jnp.pi/2]*4, "All π/2"),
        ([jnp.pi]*4, "All π"),
        ([0, jnp.pi/2, jnp.pi, 3*jnp.pi/2], "Progressive"),
    ]
    for phases, name in configs:
        result = model(phase_shifts_rad=phases)
        print(f"  {name}: through={result['through_dB']:.2f} dB, "
              f"cross={result['cross_dB']:.2f} dB")
    
    # Stage count sweep
    print("\n--- Stage Count Dependence ---")
    for n in [2, 4, 6, 8]:
        result = model(num_stages=n)
        print(f"  {n} stages: FSR={result['fsr_GHz']:.0f} GHz, "
              f"GD={result['group_delay_ps']:.1f} ps")
    
    # Paper parameters
    print("\n--- Paper Parameters ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
