"""
Name: saw_sin_modulator

Description: Thermoelastic surface acoustic wave (SAW) modulator in silicon nitride (Si3N4) 
integrated circuits. Enables acousto-optic modulation without requiring piezoelectric 
materials by utilizing thermoelastic SAW excitation in low-loss SiN platforms.

ports:
  - o1: Optical input
  - o2: Optical output

NodeLabels:
  - SAW_Modulator
  - Acousto_Optic
  - SiN_Modulator

Bandwidth:
  - C-band optical
  - RF modulation: ~100 MHz - 1 GHz

Args:
  - interaction_length: SAW-optical interaction length in µm
  - acoustic_frequency: SAW frequency in MHz
  - multipass: Number of SAW interaction passes

Reference:
  - Paper: "Thermoelastic surface acoustic waves in low-loss silicon nitride 
            integrated circuits"
  - arXiv: 2602.06732
  - Authors: Zheng Zheng, Ahmet Tarık Işık, Akshay Keloth, et al.
  - Year: 2026
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from arXiv:2602.06732
PAPER_PARAMS = {
    # Platform
    "platform": "Silicon Nitride (Si3N4)",
    "propagation_loss_dB_m": 8,  # Ultra-low loss
    
    # SAW properties
    "saw_type": "Thermoelastic surface acoustic wave",
    "excitation_method": "Thermoelastic (no piezo needed)",
    "no_extra_materials": True,
    
    # Performance
    "phase_modulation_enhancement_dB": 13.6,
    "sideband_suppression_dB": 8,
    "multipass_config": "Multi-pass for enhancement",
    
    # Ring resonator integration
    "ring_integration": "Intensity modulation via ring spectral",
    
    # Applications
    "applications": [
        "Integrated microwave photonics",
        "Programmable photonics",
        "Optical frequency shifting",
        "Sensing",
    ],
    
    # Key advantages
    "advantages": [
        "No additional materials required",
        "Compatible with low-loss SiN",
        "Multi-pass enhancement",
        "CMOS compatible",
    ],
}


@gf.cell
def saw_sin_modulator(
    interaction_length: float = 500.0,
    waveguide_width: float = 0.8,
    num_passes: int = 1,
    ring_radius: float = 50.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Thermoelastic SAW modulator in SiN.
    
    Based on arXiv:2602.06732 demonstrating acousto-optic
    modulation in low-loss SiN without piezoelectric materials.
    
    Args:
        interaction_length: SAW-optical interaction length in µm
        waveguide_width: Waveguide width in µm
        num_passes: Number of SAW interaction passes
        ring_radius: Ring radius for intensity modulation in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: SAW SiN modulator
    """
    c = gf.Component()
    
    # Straight interaction region
    straight = c << gf.components.straight(
        length=interaction_length,
        width=waveguide_width,
        cross_section=cross_section,
    )
    
    # Optional ring for intensity modulation
    if ring_radius > 0:
        ring = c << gf.components.ring_single(
            gap=0.2,
            radius=ring_radius,
            cross_section=cross_section,
        )
        ring.move((interaction_length + 20, 0))
    
    # Add ports
    c.add_port("o1", port=straight.ports["o1"])
    if ring_radius > 0:
        c.add_port("o2", port=ring.ports["o2"])
    else:
        c.add_port("o2", port=straight.ports["o2"])
    
    # Add info
    c.info["interaction_length_um"] = interaction_length
    c.info["num_passes"] = num_passes
    c.info["type"] = "SAW_modulator"
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the SAW SiN modulator.
    
    The model includes:
    - Acousto-optic phase modulation
    - Multi-pass enhancement
    - Ring-based intensity modulation
    """
    
    def saw_sin_modulator_model(
        wl: float = 1.55,
        interaction_length_um: float = 500.0,
        acoustic_frequency_MHz: float = 500.0,
        acoustic_power_mW: float = 10.0,
        num_passes: int = 1,
        n_eff: float = 1.8,
        photoelastic_coeff: float = 0.1,
        ring_detuning: float = 0.0,
    ) -> dict:
        """
        Analytical model for SAW SiN modulator.
        
        Args:
            wl: Wavelength in µm
            interaction_length_um: Interaction length in µm
            acoustic_frequency_MHz: SAW frequency in MHz
            acoustic_power_mW: Acoustic drive power in mW
            num_passes: Number of passes through SAW region
            n_eff: Effective refractive index of SiN
            photoelastic_coeff: Effective photoelastic coefficient
            ring_detuning: Ring detuning from resonance (radians)
            
        Returns:
            dict: S-parameters and modulator metrics
        """
        # SAW-induced strain (proportional to sqrt of power)
        strain_amplitude = 1e-6 * jnp.sqrt(acoustic_power_mW)
        
        # Index change from photoelastic effect
        delta_n = -0.5 * n_eff**3 * photoelastic_coeff * strain_amplitude
        
        # Phase modulation per pass
        interaction_length = interaction_length_um * 1e-6  # m
        delta_phi_per_pass = 2 * jnp.pi * delta_n * interaction_length / (wl * 1e-6)
        
        # Multi-pass enhancement
        delta_phi_total = delta_phi_per_pass * num_passes
        
        # Enhancement in dB
        enhancement_dB = 20 * jnp.log10(num_passes) if num_passes > 1 else 0
        
        # Frequency shift (single sideband)
        freq_shift_MHz = acoustic_frequency_MHz
        
        # Sideband power ratio
        J1_squared = (delta_phi_total / 2)**2  # Small modulation approximation
        sideband_power_ratio = J1_squared
        
        # If ring is used for IM
        # Intensity modulation from phase-to-IM conversion in ring
        ring_slope = 1.0  # Normalized slope at quadrature
        intensity_mod_depth = ring_slope * delta_phi_total * jnp.cos(ring_detuning)
        
        # S-parameters (optical carrier with phase modulation)
        phase = 2 * jnp.pi * n_eff * interaction_length / (wl * 1e-6)
        phase_mod = delta_phi_total * jnp.sin(0)  # At t=0
        
        S21 = jnp.exp(1j * (phase + phase_mod))
        
        # Modulation bandwidth (limited by acoustic propagation)
        acoustic_velocity = 5000  # m/s typical for SiN
        transit_time_ns = interaction_length * 1e6 / acoustic_velocity * 1e3
        bandwidth_MHz = 1000 / transit_time_ns
        
        return {
            # S-parameters
            "S21": S21,
            "S11": jnp.array(0.0 + 0j),
            # Modulation metrics
            "phase_modulation_rad": delta_phi_total,
            "enhancement_dB": enhancement_dB,
            "sideband_power_ratio": sideband_power_ratio,
            "frequency_shift_MHz": freq_shift_MHz,
            "intensity_mod_depth": intensity_mod_depth,
            # Bandwidth
            "bandwidth_MHz": bandwidth_MHz,
            "transit_time_ns": transit_time_ns,
        }
    
    return saw_sin_modulator_model


# Test code
if __name__ == "__main__":
    # Create component
    c = saw_sin_modulator()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=1.55, acoustic_power_mW=10, num_passes=1)
    
    print("\n--- SAW SiN Modulator Performance ---")
    print(f"  Phase modulation: {result['phase_modulation_rad']*1000:.2f} mrad")
    print(f"  Frequency shift: {result['frequency_shift_MHz']:.0f} MHz")
    print(f"  Bandwidth: {result['bandwidth_MHz']:.1f} MHz")
    
    # Multi-pass enhancement
    print("\n--- Multi-pass Enhancement ---")
    for passes in [1, 2, 4, 8]:
        result = model(num_passes=passes)
        print(f"  {passes} passes: Δφ = {result['phase_modulation_rad']*1000:.2f} mrad, +{result['enhancement_dB']:.1f} dB")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2602.06732) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
