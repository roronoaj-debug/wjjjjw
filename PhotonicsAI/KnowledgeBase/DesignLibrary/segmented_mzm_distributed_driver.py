"""
Name: segmented_mzm_distributed_driver

Description: Monolithically integrated five-segment Mach-Zehnder modulator with
distributed CMOS driver in 45-nm process. Enables high-speed operation with
reduced drive voltage through segmented electrode design with matched driver.

ports:
  - o1: Optical input
  - o2: Optical output
  - rf_in: RF data input
  - vbias: Bias voltage

NodeLabels:
  - Segmented_MZM
  - CMOS_Driver
  - 45nm
  - Monolithic

Bandwidth:
  - Speed: 50+ Gb/s
  - Operation: C-band

Args:
  - num_segments: Number of modulator segments
  - segment_length: Length per segment in µm

Reference:
  - Paper: "A Monolithically Integrated Five-Segment Mach–Zehnder Modulator With
           Distributed Driver in 45-nm CMOS"
  - IEEE (Buckwalter, Schow et al.)
  - Also: "A 50-Gb/s Optical Transmitter Based on Co-design of a 45-nm CMOS SOI
          Distributed Driver and 90-nm Silicon Photonic Mach-Zehnder Modulator"
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from IEEE
PAPER_PARAMS = {
    # Platform
    "photonic_platform": "90-nm/45-nm silicon photonics",
    "driver_platform": "45-nm CMOS SOI",
    "integration": "Monolithic",
    
    # Architecture
    "num_segments": 5,
    "electrode_type": "Segmented with distributed driver",
    
    # Performance
    "data_rate_Gbps": "50+",
    "modulation_format": "NRZ",
    
    # Co-design benefits
    "benefits": [
        "Reduced drive voltage (each segment)",
        "Velocity matching via segmentation",
        "Impedance matching per segment",
        "Scalable architecture",
    ],
    
    # Applications
    "applications": [
        "Data center interconnects",
        "High-speed optical links",
        "Co-packaged optics",
        "CMOS photonics integration",
    ],
}


@gf.cell
def segmented_mzm_distributed_driver(
    num_segments: int = 5,
    segment_length: float = 500.0,
    segment_gap: float = 50.0,
    waveguide_width: float = 0.5,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Segmented MZM with distributed CMOS driver.
    
    Based on IEEE work from UCSB demonstrating 50+ Gb/s
    operation with monolithic CMOS/photonic integration.
    
    Args:
        num_segments: Number of MZM segments
        segment_length: Length per segment in µm
        segment_gap: Gap between segments in µm
        waveguide_width: Waveguide width in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: Segmented MZM
    """
    c = gf.Component()
    
    # Input splitter
    splitter = c << gf.components.mmi1x2(cross_section=cross_section)
    
    # Create segmented arms
    total_length = num_segments * (segment_length + segment_gap)
    
    # Top arm segments
    arm_y_offset = 20.0
    prev_port_top = splitter.ports["o2"]
    prev_port_bot = splitter.ports["o3"]
    
    segments_top = []
    segments_bot = []
    
    x_pos = 50.0
    
    for i in range(num_segments):
        # Top arm segment
        seg_top = c << gf.components.straight(
            length=segment_length,
            cross_section=cross_section,
        )
        seg_top.move((x_pos, arm_y_offset))
        segments_top.append(seg_top)
        
        # Bottom arm segment
        seg_bot = c << gf.components.straight(
            length=segment_length,
            cross_section=cross_section,
        )
        seg_bot.move((x_pos, -arm_y_offset))
        segments_bot.append(seg_bot)
        
        x_pos += segment_length + segment_gap
    
    # Output combiner
    combiner = c << gf.components.mmi2x2(cross_section=cross_section)
    combiner.movex(x_pos + 20)
    
    # Add ports
    c.add_port("o1", port=splitter.ports["o1"])
    c.add_port("o2", port=combiner.ports["o3"])
    
    # Add segment info
    c.info["num_segments"] = num_segments
    c.info["segment_length"] = segment_length
    c.info["total_length"] = total_length
    c.info["data_rate"] = "50+ Gb/s"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the segmented MZM.
    
    The model includes:
    - Per-segment modulation
    - Driver timing/skew effects
    - Cumulative phase shift
    """
    
    def segmented_mzm_model(
        wl: float = 1.55,
        # Segment parameters
        num_segments: int = 5,
        segment_length_um: float = 500.0,
        # Drive conditions per segment
        Vdrive_per_segment_V: float = 1.0,
        Vpi_per_segment_V: float = 2.0,
        bias_V: float = 1.0,  # Quadrature
        # Timing
        segment_delay_ps: float = 5.0,  # Time shift between segments
        data_rate_Gbps: float = 50.0,
        # Losses
        loss_per_segment_dB: float = 0.5,
        coupling_loss_dB: float = 1.0,
    ) -> dict:
        """
        Analytical model for segmented MZM with distributed driver.
        
        Args:
            wl: Wavelength in µm
            num_segments: Number of segments
            segment_length_um: Length per segment
            Vdrive_per_segment_V: RF voltage per segment
            Vpi_per_segment_V: Vπ for each segment
            bias_V: DC bias voltage
            segment_delay_ps: Timing skew between driver outputs
            data_rate_Gbps: Data rate
            loss_per_segment_dB: Loss per segment
            coupling_loss_dB: Input/output coupling loss
            
        Returns:
            dict: MZM performance metrics
        """
        # Total length
        total_length_mm = num_segments * segment_length_um / 1000
        
        # Phase shift per segment
        phase_per_segment = jnp.pi * Vdrive_per_segment_V / Vpi_per_segment_V
        
        # Total phase (sum of segments)
        # With proper timing, all segments add constructively
        total_phase = num_segments * phase_per_segment
        
        # Effective Vpi (reduced due to segmentation)
        effective_Vpi = Vpi_per_segment_V / num_segments
        
        # Timing analysis
        # Maximum allowable skew for constructive addition
        bit_period_ps = 1000 / data_rate_Gbps  # ps
        total_skew_ps = (num_segments - 1) * segment_delay_ps
        
        # Timing efficiency (penalty from misalignment)
        timing_efficiency = jnp.sinc(total_skew_ps / (2 * bit_period_ps))
        timing_penalty_dB = -20 * jnp.log10(timing_efficiency + 1e-10)
        
        # Total insertion loss
        segment_loss_total_dB = num_segments * loss_per_segment_dB
        total_loss_dB = segment_loss_total_dB + coupling_loss_dB * 2
        
        # Extinction ratio
        extinction_ratio_dB = 10 * jnp.log10((1 + jnp.sin(total_phase/2)) / 
                                              (1 - jnp.sin(total_phase/2) + 1e-10))
        extinction_ratio_dB = jnp.minimum(extinction_ratio_dB, 25)  # Practical limit
        
        # Driver power
        # Each segment driver: P = V^2 / R_load
        R_load = 50  # ohms
        power_per_segment_mW = (Vdrive_per_segment_V**2 / R_load) * 1000
        total_driver_power_mW = num_segments * power_per_segment_mW
        
        # Energy per bit
        energy_per_bit_pJ = total_driver_power_mW / data_rate_Gbps
        
        # Bandwidth (segmented can maintain BW while reducing Vpi)
        # Approximation: BW limited by RC of segments
        RC_per_segment_ps = 20  # Typical
        bandwidth_GHz = 1 / (2 * jnp.pi * RC_per_segment_ps * 1e-3)
        
        # OMA (Optical Modulation Amplitude)
        T_max = 0.5 * (1 + jnp.cos(jnp.pi * bias_V / effective_Vpi))
        T_min = 0.5 * (1 + jnp.cos(jnp.pi * bias_V / effective_Vpi + total_phase))
        oma_dB = 10 * jnp.log10(jnp.abs(T_max - T_min) + 1e-10)
        
        return {
            # Segment info
            "num_segments": num_segments,
            "segment_length_um": segment_length_um,
            "total_length_mm": total_length_mm,
            # Modulation
            "effective_Vpi_V": float(effective_Vpi),
            "total_phase_rad": float(total_phase),
            "extinction_ratio_dB": float(extinction_ratio_dB),
            "oma_dB": float(oma_dB),
            # Timing
            "timing_penalty_dB": float(timing_penalty_dB),
            "total_skew_ps": total_skew_ps,
            # Losses
            "total_loss_dB": total_loss_dB,
            # Driver
            "total_driver_power_mW": total_driver_power_mW,
            "energy_per_bit_pJ": float(energy_per_bit_pJ),
            # Performance
            "data_rate_Gbps": data_rate_Gbps,
            "bandwidth_GHz": float(bandwidth_GHz),
        }
    
    return segmented_mzm_model


# Test code
if __name__ == "__main__":
    # Create component
    c = segmented_mzm_distributed_driver()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    
    print("\n--- Segmented MZM with Distributed Driver ---")
    result = model()
    print(f"  Segments: {result['num_segments']}")
    print(f"  Total length: {result['total_length_mm']:.2f} mm")
    print(f"  Effective Vπ: {result['effective_Vpi_V']:.2f} V")
    print(f"  Extinction ratio: {result['extinction_ratio_dB']:.1f} dB")
    
    print("\n--- Driver Performance ---")
    print(f"  Total driver power: {result['total_driver_power_mW']:.1f} mW")
    print(f"  Energy/bit: {result['energy_per_bit_pJ']:.2f} pJ/bit")
    print(f"  Bandwidth: {result['bandwidth_GHz']:.1f} GHz")
    
    print("\n--- Timing Analysis ---")
    print(f"  Timing penalty: {result['timing_penalty_dB']:.2f} dB")
    print(f"  Total skew: {result['total_skew_ps']:.0f} ps")
    
    # Segment count comparison
    print("\n--- Segment Count Trade-off ---")
    for n in [2, 3, 5, 7, 10]:
        result = model(num_segments=n)
        print(f"  {n} segments: Vπ={result['effective_Vpi_V']:.2f}V, "
              f"power={result['total_driver_power_mW']:.0f}mW, "
              f"timing penalty={result['timing_penalty_dB']:.2f}dB")
    
    # Paper parameters
    print("\n--- Paper Parameters (IEEE) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
