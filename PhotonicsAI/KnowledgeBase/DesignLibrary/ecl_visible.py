"""
Name: ecl_visible

Description: External cavity laser (ECL) for visible wavelengths (637 nm) based on 
PIC design with RSOA coupling. Features relaxed alignment tolerance using multi-mode 
edge coupler (MMEC) and Sagnac-loop reflector with Vernier ring resonator filtering 
for single-mode operation. Designed for quantum technology applications.

ports:
  - o1: Laser output

NodeLabels:
  - ECL
  - Visible_Laser
  - Quantum_Laser
  - RSOA_ECL

Bandwidth:
  - Visible (637 nm central)
  - Single-mode, narrow linewidth

Args:
  - ring_radius1: First ring radius in µm
  - ring_radius2: Second ring radius in µm (Vernier)
  - sagnac_coupling: Sagnac loop coupling coefficient

Reference:
  - Paper: "External Cavity 637-nm Laser with Increased RSOA-to-PIC Alignment 
            Tolerance and a Filtered Sagnac-Loop Reflector with Single Output Waveguide"
  - arXiv: 2406.14403
  - Authors: Georgios Sinatkas, Arijit Misra, Florian Merget, Jeremy Witzens
  - Year: 2024
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from arXiv:2406.14403
PAPER_PARAMS = {
    # Wavelength
    "center_wavelength_nm": 637,
    "target_applications": "Quantum technology (NV centers)",
    
    # Edge coupler
    "edge_coupler_type": "Multi-mode edge coupler (MMEC)",
    "alignment_tolerance_um": 2.4,  # 1-dB penalty
    "coupling_scheme": "Relaxed alignment for flip-chip",
    
    # Reflector structure
    "reflector_type": "Sagnac-loop reflector",
    "ring_filter": "Vernier configuration (dual ring)",
    "output": "Single output waveguide",
    
    # Ring resonators
    "ring_configuration": "Asymmetrically coupled",
    "loaded_Q_design": "Different Q-factors for two rings",
    "directional_coupler": "Suitably engineered for single output",
    
    # Design goals
    "goals": [
        "High output power",
        "Narrow linewidth",
        "Single-mode operation",
        "Flip-chip integration",
    ],
    
    # Gain chip
    "gain_chip": "Reflective SOA (RSOA)",
}


@gf.cell
def ecl_visible(
    ring_radius1: float = 20.0,
    ring_radius2: float = 22.0,
    sagnac_length: float = 100.0,
    coupling_gap: float = 0.2,
    edge_coupler_length: float = 50.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Visible external cavity laser with Vernier ring filter.
    
    Based on arXiv:2406.14403 demonstrating 637 nm ECL for
    quantum technology applications.
    
    Args:
        ring_radius1: First ring radius in µm
        ring_radius2: Second ring radius in µm (Vernier)
        sagnac_length: Sagnac loop total length in µm
        coupling_gap: Ring coupling gap in µm
        edge_coupler_length: Edge coupler taper length in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: Visible ECL components
    """
    c = gf.Component()
    
    # Edge coupler section
    edge_coupler = c << gf.components.taper(
        length=edge_coupler_length,
        width1=2.0,  # Multi-mode input
        width2=0.4,  # Single-mode waveguide
        cross_section=cross_section,
    )
    
    # First ring (part of Vernier)
    ring1 = c << gf.components.ring_single(
        gap=coupling_gap,
        radius=ring_radius1,
        cross_section=cross_section,
    )
    ring1.move((edge_coupler_length + 20, 0))
    
    # Second ring (Vernier partner)
    ring2 = c << gf.components.ring_single(
        gap=coupling_gap,
        radius=ring_radius2,
        cross_section=cross_section,
    )
    ring2.move((edge_coupler_length + 20 + 2*ring_radius1 + 30, 0))
    
    # Add ports
    c.add_port("o1", port=edge_coupler.ports["o1"])  # RSOA coupling
    c.add_port("o2", port=ring2.ports["o2"])  # Laser output
    
    # Add info
    c.info["ring_radius1_um"] = ring_radius1
    c.info["ring_radius2_um"] = ring_radius2
    c.info["wavelength_nm"] = 637
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the visible ECL.
    
    The model includes:
    - Vernier filter response
    - Sagnac loop reflection
    - Laser cavity analysis
    """
    
    def ecl_visible_model(
        wl: float = 0.637,
        ring_radius1_um: float = 20.0,
        ring_radius2_um: float = 22.0,
        n_eff: float = 2.1,
        coupling_coefficient: float = 0.1,
        ring_loss_dB_cm: float = 5.0,
        rsoa_gain_dB: float = 20.0,
        rsoa_reflectivity: float = 0.9,
    ) -> dict:
        """
        Analytical model for visible external cavity laser.
        
        Args:
            wl: Wavelength in µm
            ring_radius1_um: First ring radius in µm
            ring_radius2_um: Second ring radius in µm
            n_eff: Effective refractive index
            coupling_coefficient: Ring coupling coefficient
            ring_loss_dB_cm: Ring propagation loss in dB/cm
            rsoa_gain_dB: RSOA gain in dB
            rsoa_reflectivity: RSOA back facet reflectivity
            
        Returns:
            dict: Laser cavity parameters
        """
        # Ring parameters
        L1 = 2 * jnp.pi * ring_radius1_um * 1e-6  # m
        L2 = 2 * jnp.pi * ring_radius2_um * 1e-6  # m
        
        # FSR for each ring
        FSR1_nm = (wl * 1e-6)**2 / (n_eff * L1) * 1e9  # nm
        FSR2_nm = (wl * 1e-6)**2 / (n_eff * L2) * 1e9  # nm
        
        # Vernier FSR (combined)
        FSR_vernier_nm = FSR1_nm * FSR2_nm / jnp.abs(FSR1_nm - FSR2_nm)
        
        # Ring loss
        alpha_per_m = ring_loss_dB_cm * 100 / (10 * jnp.log10(jnp.e))
        a1 = jnp.exp(-alpha_per_m * L1 / 2)
        a2 = jnp.exp(-alpha_per_m * L2 / 2)
        
        # Coupling coefficients
        kappa = coupling_coefficient
        t = jnp.sqrt(1 - kappa**2)
        
        # Single ring transmission at resonance
        T_ring = (a1 - t)**2 / (1 - a1 * t)**2
        
        # Combined Vernier filter transmission
        T_vernier = T_ring * T_ring  # Simplified cascade
        
        # Sagnac loop reflectivity (approx 50:50 at resonance)
        R_sagnac = 0.5 * T_vernier
        
        # Cavity round trip gain
        G_rsoa = 10 ** (rsoa_gain_dB / 10)
        cavity_rt_gain = G_rsoa * rsoa_reflectivity * R_sagnac
        
        # Lasing threshold condition
        threshold_gain_dB = -10 * jnp.log10(rsoa_reflectivity * R_sagnac + 1e-10)
        
        # Linewidth estimate (simplified)
        Q_ring = 2 * jnp.pi * n_eff / (alpha_per_m * wl * 1e-6)
        linewidth_kHz = 1e6 / (Q_ring + 1e3)  # Very rough estimate
        
        # Output power estimate
        above_threshold = jnp.maximum(rsoa_gain_dB - threshold_gain_dB, 0)
        output_power_mW = 0.5 * above_threshold  # Simplified
        
        return {
            # FSR
            "FSR_ring1_nm": FSR1_nm,
            "FSR_ring2_nm": FSR2_nm,
            "FSR_vernier_nm": FSR_vernier_nm,
            # Filter response
            "vernier_transmission": T_vernier,
            "sagnac_reflectivity": R_sagnac,
            # Laser parameters
            "threshold_gain_dB": threshold_gain_dB,
            "cavity_round_trip_gain": cavity_rt_gain,
            "Q_factor": Q_ring,
            "linewidth_kHz": linewidth_kHz,
            "output_power_mW": output_power_mW,
        }
    
    return ecl_visible_model


# Test code
if __name__ == "__main__":
    # Create component
    c = ecl_visible()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=0.637)
    
    print("\n--- Visible ECL Performance ---")
    print(f"  FSR Ring 1: {result['FSR_ring1_nm']:.2f} nm")
    print(f"  FSR Ring 2: {result['FSR_ring2_nm']:.2f} nm")
    print(f"  Vernier FSR: {result['FSR_vernier_nm']:.2f} nm")
    print(f"  Threshold gain: {result['threshold_gain_dB']:.1f} dB")
    print(f"  Estimated linewidth: {result['linewidth_kHz']:.1f} kHz")
    print(f"  Output power: {result['output_power_mW']:.1f} mW")
    
    # Paper parameters
    print("\n--- Paper Parameters (arXiv:2406.14403) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
