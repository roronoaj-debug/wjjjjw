"""
Name: multibeam_opa

Description: Multibeam optical phased array (MBOPA) for multi-user optical wireless
communication. Uses wavelength-division multiplexing with path-length differences
for spatial carrier aggregation and multiplexing to multiple users.

ports:
  - optical_in: Optical input from WDM source
  - beam_out_1: Beam output port 1
  - beam_out_2: Beam output port 2
  - beam_out_N: Additional beam outputs

NodeLabels:
  - MBOPA
  - OPA
  - OWC
  - WDM_Steering

Bandwidth:
  - Data rate: 54 Gbps per user
  - Operation: C-band with WDM

Args:
  - num_channels: Number of wavelength channels
  - num_beams: Number of output beams
  - element_spacing: Antenna element spacing in µm

Reference:
  - Paper: "Electronic-Photonic Interface for Multiuser Optical Wireless Communication"
  - arXiv: 2510.13608
  - Authors: Youngin Kim, Laurenz Kulmer, Jae-Yong Kim, Juerg Leuthold, Hua Wang
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from arXiv:2510.13608
PAPER_PARAMS = {
    # Platform
    "plc_platform": "Silica planar lightwave circuit",
    "modulator_platform": "45-nm monolithic silicon photonics",
    
    # System performance
    "data_rate_Gbps_per_user": 54,
    "wireless_distance_m": 1,
    "num_users": 2,  # Demonstrated 2 users
    
    # OPA characteristics
    "multibeam_capability": True,
    "wdm_steering": True,
    "path_length_difference_steering": True,
    
    # Modulator integration
    "modulator_type": "Traveling-wave MZM",
    "cmos_driver": "High-speed, wide-output-swing",
    "modulation_format": ["PAM-2", "PAM-4"],
    
    # Applications
    "applications": [
        "Multi-user optical wireless communication",
        "Free-space optical links",
        "Indoor optical wireless",
        "Data center OWC",
        "Last-mile connectivity",
    ],
}


@gf.cell
def multibeam_opa(
    num_elements: int = 8,
    element_spacing: float = 10.0,
    delay_increment: float = 100.0,
    waveguide_width: float = 0.5,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Multibeam optical phased array for multi-user OWC.
    
    Based on arXiv:2510.13608 demonstrating 54 Gbps per user
    over 1m wireless distance.
    
    Args:
        num_elements: Number of array elements
        element_spacing: Element spacing in µm
        delay_increment: Path length increment per element in µm
        waveguide_width: Waveguide width in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: MBOPA component
    """
    c = gf.Component()
    
    # Input splitter (1xN)
    splitter = c << gf.components.mmi1x2(cross_section=cross_section)
    
    # Create array elements with progressive delays
    prev_port = splitter.ports["o2"]
    elements = []
    
    for i in range(num_elements):
        # Delay line
        delay_length = delay_increment * (i + 1)
        delay = c << gf.components.straight(
            length=delay_length,
            cross_section=cross_section,
        )
        
        if i == 0:
            delay.connect("o1", splitter.ports["o2"])
        else:
            # Space vertically
            delay.movey(-element_spacing * (i + 1))
            delay.movex(50)
        
        elements.append(delay)
    
    # Add ports
    c.add_port("o1", port=splitter.ports["o1"])
    for i, elem in enumerate(elements):
        c.add_port(f"beam_{i+1}", port=elem.ports["o2"])
    
    # Add info
    c.info["num_elements"] = num_elements
    c.info["data_rate"] = "54 Gbps/user"
    c.info["steering_method"] = "WDM + path length"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the multibeam OPA.
    
    The model includes:
    - WDM-based beam steering
    - Path-length difference steering
    - Multi-user spatial multiplexing
    """
    
    def multibeam_opa_model(
        wl: float = 1.55,
        # Array parameters
        num_elements: int = 8,
        element_spacing_um: float = 10.0,
        delay_increment_um: float = 100.0,
        # Operating conditions
        wavelength_channels: int = 4,
        wavelength_spacing_nm: float = 0.8,
        # Environment
        propagation_distance_m: float = 1.0,
        pointing_angle_deg: float = 0.0,
        # System performance
        modulation_data_rate_Gbps: float = 54.0,
        # Losses
        insertion_loss_dB: float = 6.0,
        coupling_loss_dB: float = 3.0,
    ) -> dict:
        """
        Analytical model for multi-beam OPA.
        
        Args:
            wl: Center wavelength in µm
            num_elements: Number of array elements
            element_spacing_um: Element pitch in µm
            delay_increment_um: Path length increment
            wavelength_channels: Number of WDM channels
            wavelength_spacing_nm: WDM channel spacing
            propagation_distance_m: Free-space propagation distance
            pointing_angle_deg: Beam pointing angle
            modulation_data_rate_Gbps: Data rate per channel
            insertion_loss_dB: On-chip loss
            coupling_loss_dB: Fiber-to-chip coupling loss
            
        Returns:
            dict: OPA performance metrics
        """
        # Wavelength to beam angle mapping
        # Δθ = (Δλ/λ) * (delay/spacing)
        effective_delay_factor = delay_increment_um / element_spacing_um
        
        # Beam angles for each wavelength channel
        center_wl_nm = wl * 1000
        beam_angles_deg = []
        
        for ch in range(wavelength_channels):
            wl_offset_nm = (ch - wavelength_channels/2) * wavelength_spacing_nm
            angle_offset = (wl_offset_nm / center_wl_nm) * effective_delay_factor * 180 / jnp.pi
            beam_angles_deg.append(float(pointing_angle_deg + angle_offset * 10))  # Scaling
        
        # Array factor
        # Calculate beam pattern
        theta_rad = jnp.deg2rad(pointing_angle_deg)
        k = 2 * jnp.pi / (wl * 1e-6)  # Wavenumber
        d = element_spacing_um * 1e-6  # Element spacing in meters
        
        # Progressive phase for steering
        psi = k * d * jnp.sin(theta_rad)
        
        # Array factor magnitude
        N = num_elements
        numerator = jnp.sin(N * psi / 2)
        denominator = jnp.sin(psi / 2) + 1e-10
        array_factor = jnp.abs(numerator / denominator) / N
        
        # Beam divergence (far-field)
        aperture_um = num_elements * element_spacing_um
        aperture_m = aperture_um * 1e-6
        beam_divergence_rad = wl * 1e-6 / aperture_m
        beam_divergence_mrad = beam_divergence_rad * 1000
        
        # Spot size at distance
        spot_size_mm = propagation_distance_m * beam_divergence_rad * 1000
        
        # Link budget
        free_space_loss_dB = 20 * jnp.log10(4 * jnp.pi * propagation_distance_m / (wl * 1e-6))
        # Simplified for close-range OWC
        close_range_loss_dB = jnp.minimum(free_space_loss_dB, 30.0)
        
        total_loss_dB = insertion_loss_dB + coupling_loss_dB + 10.0  # 10 dB for close-range
        
        # Capacity
        total_capacity_Gbps = wavelength_channels * modulation_data_rate_Gbps
        
        # Steering range
        max_steering_angle_deg = (wavelength_channels * wavelength_spacing_nm / center_wl_nm) * \
                                  effective_delay_factor * 180 / jnp.pi * 10
        
        return {
            # Beam characteristics
            "beam_angles_deg": beam_angles_deg,
            "beam_divergence_mrad": float(beam_divergence_mrad),
            "spot_size_mm": float(spot_size_mm),
            "array_factor": float(array_factor),
            # Multi-user
            "num_spatial_channels": wavelength_channels,
            "data_rate_per_user_Gbps": modulation_data_rate_Gbps,
            "total_capacity_Gbps": total_capacity_Gbps,
            # Steering
            "steering_range_deg": float(max_steering_angle_deg),
            "steering_method": "WDM wavelength tuning",
            # Link budget
            "total_loss_dB": total_loss_dB,
            # Array
            "num_elements": num_elements,
            "aperture_um": float(aperture_um),
        }
    
    return multibeam_opa_model


# Test code
if __name__ == "__main__":
    # Create component
    c = multibeam_opa()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    
    print("\n--- Multibeam OPA for OWC ---")
    result = model()
    print(f"  WDM channels: {result['num_spatial_channels']}")
    print(f"  Data rate per user: {result['data_rate_per_user_Gbps']} Gbps")
    print(f"  Total capacity: {result['total_capacity_Gbps']} Gbps")
    print(f"  Beam divergence: {result['beam_divergence_mrad']:.2f} mrad")
    print(f"  Spot size at 1m: {result['spot_size_mm']:.2f} mm")
    
    # Beam angles for different channels
    print("\n--- WDM Channel Beam Angles ---")
    print(f"  Channel beam angles: {result['beam_angles_deg']}")
    
    # Distance dependence
    print("\n--- Distance Dependence ---")
    for dist in [0.5, 1.0, 2.0, 5.0]:
        result = model(propagation_distance_m=dist)
        print(f"  {dist}m: spot = {result['spot_size_mm']:.2f} mm, "
              f"loss = {result['total_loss_dB']:.1f} dB")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2510.13608) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
