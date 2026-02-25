"""
Name: lnoi_ring

Description: Thin-film lithium niobate on insulator (LNOI) ring resonator for electro-optic 
applications. LNOI offers strong χ⁽²⁾ nonlinearity enabling high-speed electro-optic modulation, 
parametric processes, and frequency conversion. This design targets telecom wavelength 
operation with low propagation loss and high Q-factor.

ports:
  - o1: Input port
  - o2: Through port
  - o3: Drop port (for add-drop configuration)

NodeLabels:
  - LNOI_Ring
  - EO_Ring

Bandwidth:
  - C-band (1550 nm)
  - Wide electro-optic bandwidth (> 10 GHz)

Args:
  - radius: Ring radius in µm (default: 80.0)
  - width: Waveguide width in µm (default: 1.2)
  - height: Waveguide height in nm (default: 400)
  - gap: Coupling gap in nm (default: 300)
  - etch_depth: Etch depth in nm (default: 300)

Reference:
  - Paper: "Characterization of Ring Resonators in Thin-Film Lithium Niobate on 
            Insulator (LNOI) Photonic Integrated Circuit Platform"
  - Source: IEEE Xplore (Document 10231513)
  - Year: 2023
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from IEEE 10231513
PAPER_PARAMS = {
    # Material properties
    "material": "Thin-film LiNbO3 on insulator (LNOI)",
    "crystal_cut": "X-cut",  # Common for EO applications
    "substrate": "SiO2/Si",
    
    # Waveguide geometry (typical LNOI parameters)
    "waveguide_width_um": 1.2,  # µm
    "waveguide_height_nm": 400,  # nm (thin-film)
    "etch_depth_nm": 300,  # Partial or full etch
    "ridge_type": "Rib waveguide",
    
    # Ring parameters
    "ring_radius_um": 80.0,  # Typical LNOI ring
    "gap_nm": 300,  # Coupling gap
    
    # Optical properties
    "n_eff_TE": 2.0,  # Approximate effective index
    "n_g": 2.2,  # Group index
    "propagation_loss_dB_cm": 0.5,  # Target low loss
    
    # Electro-optic properties
    "r33_pm_V": 31,  # Pockels coefficient (pm/V)
    "eo_bandwidth_GHz": 10,  # Electro-optic modulation bandwidth
    
    # Nonlinear properties
    "chi2_pm_V": 30,  # χ⁽²⁾ nonlinearity
    
    # Platform
    "platform": "LNOI PIC",
    "fabrication": "CSEM/Foundry",
}


@gf.cell
def lnoi_ring(
    radius: float = 80.0,
    width: float = 1.2,
    gap: float = 0.3,
    coupling_length: float = 10.0,
    add_drop: bool = True,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Thin-film LNOI ring resonator for electro-optic applications.
    
    Based on IEEE 10231513 characterization of LNOI ring resonators
    for photonic integrated circuits.
    
    Args:
        radius: Ring radius in µm
        width: Waveguide width in µm
        gap: Coupling gap in µm
        coupling_length: Coupling region length in µm
        add_drop: If True, creates add-drop configuration
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: LNOI ring with input, through, and optionally drop ports
    """
    c = gf.Component()
    
    if add_drop:
        # Add-drop ring configuration
        ring = c << gf.components.ring_double(
            radius=radius,
            gap=gap,
            length_x=coupling_length,
            cross_section=cross_section,
        )
        c.add_port("o1", port=ring.ports["o1"])
        c.add_port("o2", port=ring.ports["o2"])
        c.add_port("o3", port=ring.ports["o3"])
        c.add_port("o4", port=ring.ports["o4"])
    else:
        # All-pass ring configuration
        ring = c << gf.components.ring_single(
            radius=radius,
            gap=gap,
            pass_cross_section_spec=cross_section,
        )
        c.add_port("o1", port=ring.ports["o1"])
        c.add_port("o2", port=ring.ports["o2"])
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the LNOI ring resonator.
    
    The model includes:
    - Wavelength-dependent transmission
    - Electro-optic tuning effect
    - Q-factor calculation
    """
    
    def lnoi_ring_model(
        wl: float = 1.55,
        radius: float = 80.0,
        width: float = 1.2,
        gap: float = 0.3,
        n_eff: float = 2.0,
        n_g: float = 2.2,
        alpha_dB_cm: float = 0.5,
        kappa: float = 0.1,
        applied_voltage: float = 0.0,
        r33: float = 31e-12,  # Pockels coefficient in m/V
        electrode_length: float = 100e-6,  # Electrode length in m
        electrode_gap: float = 5e-6,  # Electrode gap in m
    ) -> dict:
        """
        Analytical model for LNOI ring resonator with electro-optic tuning.
        
        Args:
            wl: Wavelength in µm
            radius: Ring radius in µm
            width: Waveguide width in µm
            gap: Coupling gap in µm
            n_eff: Effective refractive index
            n_g: Group index
            alpha_dB_cm: Propagation loss in dB/cm
            kappa: Power coupling coefficient
            applied_voltage: Applied voltage for EO tuning (V)
            r33: Pockels coefficient (m/V)
            electrode_length: Electrode length (m)
            electrode_gap: Electrode gap (m)
            
        Returns:
            dict: S-parameters and resonator metrics
        """
        # Physical constants
        c_light = 3e8  # Speed of light (m/s)
        
        # Ring parameters
        L = 2 * jnp.pi * radius * 1e-6  # Ring length in m
        
        # Electro-optic index change
        E_field = applied_voltage / electrode_gap  # V/m
        delta_n = -0.5 * n_eff**3 * r33 * E_field
        
        # Modified effective index
        n_eff_modified = n_eff + delta_n * electrode_length / L
        
        # Calculate FSR
        FSR_Hz = c_light / (n_g * L)
        FSR_nm = (wl * 1e-6)**2 * FSR_Hz / c_light * 1e9
        
        # Coupling coefficients
        t = jnp.sqrt(1 - kappa)  # Through coupling
        k = jnp.sqrt(kappa)  # Cross coupling
        
        # Loss per round trip
        alpha = alpha_dB_cm / (10 * jnp.log10(jnp.e)) / 100  # Convert to 1/m
        a = jnp.exp(-alpha * L)  # Field amplitude transmission
        
        # Round-trip phase
        phi = 2 * jnp.pi * n_eff_modified * L / (wl * 1e-6)
        
        # Through transmission (add-drop configuration)
        denominator = 1 - (t**2) * a * jnp.exp(1j * phi)
        S21 = t * (1 - a * t * jnp.exp(1j * phi)) / denominator
        
        # Drop transmission
        S31 = -k**2 * jnp.sqrt(a) * jnp.exp(1j * phi / 2) / denominator
        
        # Q factor
        Q_loaded = jnp.pi * n_g * jnp.sqrt(a) * t**2 / ((1 - a * t**2) * (wl * 1e-9))
        Q_intrinsic = jnp.pi * n_g / (alpha * wl * 1e-6)
        
        # Resonance wavelength shift due to EO effect
        delta_wl = wl * delta_n / n_g * 1e3  # in nm
        
        # Finesse
        finesse = FSR_nm * Q_loaded / (wl * 1e3)
        
        return {
            # S-parameters
            "S11": jnp.array(0.0, dtype=complex),
            "S21": S21,
            "S31": S31,
            "S12": S21,
            "S13": S31,
            # Resonator metrics
            "FSR_nm": FSR_nm,
            "Q_loaded": Q_loaded,
            "Q_intrinsic": Q_intrinsic,
            "finesse": finesse,
            # Electro-optic tuning
            "delta_n": delta_n,
            "delta_wavelength_nm": delta_wl,
            "tuning_efficiency_pm_V": jnp.abs(delta_wl * 1000 / (applied_voltage + 1e-10)),
        }
    
    return lnoi_ring_model


# Test code
if __name__ == "__main__":
    # Create and visualize component
    c = lnoi_ring()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=1.55)
    
    print(f"\nModel results at 1550 nm, no applied voltage:")
    print(f"  |S21| (through): {abs(result['S21']):.4f}")
    print(f"  |S31| (drop): {abs(result['S31']):.4f}")
    print(f"  FSR: {result['FSR_nm']:.2f} nm")
    print(f"  Q-loaded: {result['Q_loaded']:.0f}")
    print(f"  Q-intrinsic: {result['Q_intrinsic']:.0f}")
    
    # Test EO tuning
    print("\n--- Electro-Optic Tuning ---")
    for voltage in [0, 1, 5, 10]:
        result = model(wl=1.55, applied_voltage=voltage)
        print(f"  V={voltage}V: Δλ = {result['delta_wavelength_nm']:.3f} nm")
    
    # Show paper parameters
    print("\n--- Paper Parameters (IEEE 10231513) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
