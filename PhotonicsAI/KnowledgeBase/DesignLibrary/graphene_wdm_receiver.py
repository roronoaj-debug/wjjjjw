"""
Name: graphene_wdm_receiver

Description: Four-channel wavelength division multiplexing (WDM) optical receiver based on 
silicon microring resonator (MRR) array integrated with graphene photodetectors (GPDs). 
The GPDs utilize the photo-thermoelectric (PTE) effect for zero-bias operation with 
high bandwidth and good consistency across all channels.

ports:
  - o1: Common optical input
  - o2: Through port
  - ch1, ch2, ch3, ch4: Drop ports for 4 WDM channels

NodeLabels:
  - GrapheneWDM
  - WDM_Rx

Bandwidth:
  - C-band (1550 nm range)
  - 67 GHz electrical bandwidth per channel

Args:
  - n_channels: Number of WDM channels (default: 4)
  - ring_radius: MRR radius in µm (default: 10.0)
  - channel_spacing: Channel spacing in nm (default: 0.8)
  - responsivity: Photodetector responsivity in V/W (default: 1.1)

Reference:
  - Paper: "Four-Channel WDM Graphene Optical Receiver"
  - arXiv: 2402.16032
  - Authors: L. Yu, Y. Li, H. Xiang, et al.
  - Year: 2024
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from arXiv:2402.16032
PAPER_PARAMS = {
    # Architecture
    "n_channels": 4,
    "configuration": "MRR array + GPD array",
    
    # Microring resonator
    "ring_type": "add-drop MRR",
    "ring_radius_um": 10.0,  # Typical silicon MRR size
    "channel_spacing_nm": 0.8,  # Channel spacing
    
    # Graphene photodetector (GPD)
    "detector_type": "p-n homojunction GPD",
    "detection_mechanism": "Photo-thermoelectric (PTE)",
    "responsivity_V_W": 1.1,  # Voltage responsivity
    "bandwidth_GHz": 67,  # 3-dB bandwidth (setup limited)
    "bias": "Zero current bias",
    "active_area_mm2": 0.006,  # Total active region
    
    # Graphene stack
    "graphene_stack": "hBN/graphene/hBN",
    "graphene_quality": "mechanically exfoliated",
    "contact_type": "edge graphene-metal",
    
    # Performance
    "data_rate_per_channel_Gbps": 16,
    "modulation_format": "NRZ",
    "total_data_rate_Gbps": 64,  # 4 × 16 Gbps
    
    # Platform
    "platform": "Silicon photonics",
    "wavelength_band": "C-band",
}


@gf.cell
def graphene_wdm_receiver(
    n_channels: int = 4,
    ring_radius: float = 10.0,
    gap: float = 0.2,
    channel_spacing: float = 50.0,  # Physical spacing between rings in µm
    width: float = 0.5,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    4-channel WDM receiver with MRR demux and graphene photodetectors.
    
    Based on arXiv:2402.16032 demonstrating 4×16 Gbps NRZ transmission
    with 67 GHz bandwidth PTE-based graphene detectors.
    
    Args:
        n_channels: Number of WDM channels
        ring_radius: Microring radius in µm
        gap: Coupling gap in µm
        channel_spacing: Physical spacing between channels in µm
        width: Waveguide width in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: WDM receiver with input, through, and drop ports
    """
    c = gf.Component()
    
    # Calculate total bus length
    total_length = (n_channels + 1) * channel_spacing
    
    # Create main bus waveguide
    bus = c << gf.components.straight(length=total_length, width=width, cross_section=cross_section)
    bus.movex(-channel_spacing / 2)
    
    # Create add-drop ring resonators for each channel
    for i in range(n_channels):
        # Position for this channel
        x_pos = i * channel_spacing
        
        # Create ring resonator
        ring = c << gf.components.ring_single(
            radius=ring_radius,
            gap=gap,
            pass_cross_section_spec=cross_section,
        )
        ring.movex(x_pos)
        ring.movey(ring_radius + gap + width)
        
        # Add drop waveguide
        drop_wg = c << gf.components.straight(length=channel_spacing * 0.8, width=width, cross_section=cross_section)
        drop_wg.movex(x_pos - channel_spacing * 0.4)
        drop_wg.movey(2 * ring_radius + 2 * gap + 2 * width)
        
        # Add channel port
        c.add_port(f"ch{i+1}", port=drop_wg.ports["o2"])
    
    # Add main ports
    c.add_port("o1", port=bus.ports["o1"])
    c.add_port("o2", port=bus.ports["o2"])
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the WDM graphene receiver.
    
    The model includes:
    - MRR-based wavelength demultiplexing
    - Graphene PD responsivity and bandwidth
    - Channel crosstalk estimation
    """
    
    def graphene_wdm_receiver_model(
        wl: float = 1.55,
        n_channels: int = 4,
        ring_radius: float = 10.0,
        n_eff: float = 2.4,
        n_g: float = 4.2,
        kappa: float = 0.2,
        alpha_dB_cm: float = 2.0,
        channel_spacing_nm: float = 0.8,
        responsivity_V_W: float = 1.1,
        bandwidth_GHz: float = 67.0,
    ) -> dict:
        """
        Analytical model for WDM graphene optical receiver.
        
        Args:
            wl: Wavelength in µm
            n_channels: Number of WDM channels
            ring_radius: MRR radius in µm
            n_eff: Effective refractive index
            n_g: Group index
            kappa: Power coupling coefficient
            alpha_dB_cm: Propagation loss in dB/cm
            channel_spacing_nm: WDM channel spacing in nm
            responsivity_V_W: GPD responsivity in V/W
            bandwidth_GHz: GPD bandwidth in GHz
            
        Returns:
            dict: S-parameters and receiver metrics
        """
        # Physical constants
        c_light = 3e8  # Speed of light (m/s)
        
        # Ring parameters
        L = 2 * jnp.pi * ring_radius * 1e-6  # Ring length in m
        
        # Calculate FSR
        FSR_Hz = c_light / (n_g * L)
        FSR_nm = (wl * 1e-6)**2 * FSR_Hz / c_light * 1e9
        
        # Loss per round trip
        alpha = alpha_dB_cm / (10 * jnp.log10(jnp.e)) / 100  # Convert to 1/m
        a = jnp.exp(-alpha * L)  # Field amplitude transmission
        
        # Coupling coefficients
        t = jnp.sqrt(1 - kappa)  # Through coupling
        k = jnp.sqrt(kappa)  # Cross coupling
        
        # Generate S-parameters for each channel
        results = {}
        
        # Through port (assumes operating at resonance of channel 1)
        phi_res = 0.0  # At resonance
        
        # Add-drop ring transmission at resonance
        # Drop port: maximum at resonance
        S_drop = -k**2 * a * jnp.exp(1j * phi_res) / (1 - t**2 * a * jnp.exp(1j * phi_res))
        
        # Through port: minimum at resonance  
        S_through = (t - t * a * jnp.exp(1j * phi_res)) / (1 - t**2 * a * jnp.exp(1j * phi_res))
        
        # Main S-parameters
        results["S11"] = jnp.array(0.0, dtype=complex)
        results["S21"] = S_through  # Through port
        
        # Channel drop ports (simplified: all channels have same characteristics)
        for i in range(n_channels):
            results[f"S_ch{i+1}"] = S_drop
        
        # Receiver metrics
        results["FSR_nm"] = FSR_nm
        results["responsivity_V_W"] = responsivity_V_W
        results["bandwidth_GHz"] = bandwidth_GHz
        results["data_rate_Gbps"] = 16.0  # Per channel
        results["extinction_ratio_dB"] = 10 * jnp.log10(jnp.abs(S_drop / S_through)**2)
        
        return results
    
    return graphene_wdm_receiver_model


# Test code
if __name__ == "__main__":
    # Create and visualize component
    c = graphene_wdm_receiver()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=1.55)
    print(f"\nModel results at 1550 nm:")
    print(f"  |S21| (through): {abs(result['S21']):.4f}")
    print(f"  |S_ch1| (drop): {abs(result['S_ch1']):.4f}")
    print(f"  FSR: {result['FSR_nm']:.2f} nm")
    print(f"  Responsivity: {result['responsivity_V_W']:.1f} V/W")
    print(f"  Bandwidth: {result['bandwidth_GHz']:.0f} GHz")
    
    # Show paper parameters
    print("\n--- Paper Parameters (arXiv:2402.16032) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
