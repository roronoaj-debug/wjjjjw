"""
Name: si3n4_squeezed_ring

Description: Silicon nitride (Si₃N₄) microring resonator for single-mode coherent-squeezed 
light generation via four-wave mixing. This component utilizes the inherent χ⁽³⁾ Kerr 
nonlinearity of Si₃N₄ to generate squeezed light at the pump frequency through FWM. 
The design features an overcoupled resonator with high Q-factor for efficient squeezing.

ports:
  - o1: Input port (pump input)
  - o2: Output port (squeezed light output)

NodeLabels:
  - Si3N4SqzRing

Bandwidth:
  - C-band (1550 nm)

Args:
  - radius: Ring radius in µm (default: 211.0)
  - width: Waveguide width in µm (default: 1.6)
  - height: Waveguide height in nm (default: 800)
  - gap: Coupling gap in µm (default: 0.52)
  - kappa: External coupling rate in MHz (default: 515)
  - gamma: Internal loss rate in MHz (default: 192)
  - wavelength: Operating wavelength in nm (default: 1550)

Reference:
  - Paper: "Chip-integrated single-mode coherent-squeezed light source using 
            four-wave mixing in microresonators"
  - arXiv: 2502.16278
  - Authors: P. Tritschler, T. Ohms, et al.
  - Year: 2025
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import jax.numpy as jnp

# Paper-extracted parameters from arXiv:2502.16278
PAPER_PARAMS = {
    # Waveguide geometry
    "waveguide_width_um": 1.6,  # µm
    "waveguide_height_nm": 800,  # nm
    "radius_um": 211.0,  # µm
    "gap_um": 0.52,  # µm
    
    # Resonator characteristics
    "kappa_MHz": 515,  # External coupling rate
    "gamma_MHz": 192,  # Internal loss rate
    "Q_factor": 1.7e6,  # Quality factor
    "D2_MHz": 7.76,  # Second-order dispersion (anomalous)
    
    # Nonlinear parameters
    "g_opt_Hz": 1.4,  # Optical Kerr gain
    "g_th_Hz": 127,  # Thermal gain
    "P_th_mW": 7.89,  # Threshold power for FWM
    
    # Performance
    "squeezing_dB": -4.7,  # On-chip squeezing at 7.59 mW
    "anti_squeezing_dB": 6.89,  # Anti-squeezing
    "pump_wavelength_nm": 1550,  # C-band
    "detection_efficiency": 0.29,  # System efficiency (29%)
    
    # Material
    "material": "Si3N4",
    "n_eff": 1.9,  # Effective refractive index
}


@gf.cell
def si3n4_squeezed_ring(
    radius: float = 211.0,
    width: float = 1.6,
    height: float = 0.8,
    gap: float = 0.52,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    Si₃N₄ microring resonator for squeezed light generation via FWM.
    
    Based on arXiv:2502.16278 demonstrating -4.7 dB on-chip squeezing
    using χ⁽³⁾ nonlinearity at the injection locking point.
    
    Args:
        radius: Ring radius in µm
        width: Waveguide width in µm
        height: Waveguide height in µm
        gap: Coupling gap between bus waveguide and ring in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: Ring resonator component with ports o1 (input) and o2 (output)
    """
    c = gf.Component()
    
    # Create bus waveguide (straight section for coupling)
    bus_length = 2 * radius + 100  # Ensure enough length
    bus = c << gf.components.straight(length=bus_length, width=width, cross_section=cross_section)
    bus.movex(-bus_length / 2)
    
    # Create ring resonator
    ring = c << gf.components.ring(
        radius=radius,
        width_ring=width,
        cross_section=cross_section,
    )
    ring.movey(radius + gap + width)
    
    # Add ports
    c.add_port("o1", port=bus.ports["o1"])
    c.add_port("o2", port=bus.ports["o2"])
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the Si₃N₄ squeezed light ring.
    
    The model includes:
    - Ring resonator transmission with overcoupled design
    - Squeezing calculation based on FWM theory from arXiv:2502.16278
    - Power-dependent nonlinear effects
    """
    
    def si3n4_squeezed_ring_model(
        wl: float = 1.55,
        radius: float = 211.0,
        width: float = 1.6,
        gap: float = 0.52,
        n_eff: float = 1.9,
        kappa_MHz: float = 515.0,
        gamma_MHz: float = 192.0,
        P_in_mW: float = 7.59,
        P_th_mW: float = 7.89,
    ) -> dict:
        """
        Analytical model for squeezed light generation in Si₃N₄ microring.
        
        Args:
            wl: Wavelength in µm
            radius: Ring radius in µm
            width: Waveguide width in µm
            gap: Coupling gap in µm
            n_eff: Effective refractive index
            kappa_MHz: External coupling rate (MHz)
            gamma_MHz: Internal loss rate (MHz)
            P_in_mW: Input pump power (mW)
            P_th_mW: FWM threshold power (mW)
            
        Returns:
            dict: S-parameters and squeezing metrics
        """
        # Physical constants
        c = 3e8  # Speed of light (m/s)
        
        # Ring parameters
        L = 2 * jnp.pi * radius * 1e-6  # Ring length in meters
        
        # Calculate coupling coefficients
        # Overcoupled regime: kappa > gamma
        Gamma = kappa_MHz + gamma_MHz  # Total loss rate (MHz)
        kappa_norm = kappa_MHz / Gamma
        
        # Ring transmission (simple model)
        # t = through coupling, k = cross coupling
        k = jnp.sqrt(kappa_norm)  # Field coupling coefficient
        t = jnp.sqrt(1 - kappa_norm)
        
        # Round-trip phase
        phi = 2 * jnp.pi * n_eff * L / (wl * 1e-6)
        
        # Loss per round trip (from gamma)
        alpha_rt = 1 - gamma_MHz / (2 * Gamma)
        
        # Through transmission (all-pass approximation for simplicity)
        numerator = t - alpha_rt * jnp.exp(1j * phi)
        denominator = 1 - t * alpha_rt * jnp.exp(1j * phi)
        S21 = numerator / denominator
        
        # Squeezing calculation from paper theory (Eq. 3)
        # V_s/V_vac = 1 - (8 * eta * kappa/Gamma) * (P_in/P_th)^2 * [sqrt(1 + (P_th/2P_in)^2) - 1]
        eta = 1.0  # On-chip efficiency (before outcoupling losses)
        power_ratio = P_in_mW / P_th_mW
        
        factor = 1 + (P_th_mW / (2 * P_in_mW))**2
        squeezing_linear = 1 - 8 * eta * kappa_norm * power_ratio**2 * (jnp.sqrt(factor) - 1)
        
        # Convert to dB
        squeezing_dB = 10 * jnp.log10(jnp.abs(squeezing_linear))
        
        return {
            "S11": jnp.array(0.0, dtype=complex),
            "S12": S21,
            "S21": S21,
            "S22": jnp.array(0.0, dtype=complex),
            "squeezing_dB": squeezing_dB,
            "Q_factor": 2 * jnp.pi * c / (wl * 1e-6) / (Gamma * 1e6),
        }
    
    return si3n4_squeezed_ring_model


# Test code
if __name__ == "__main__":
    # Create and visualize component
    c = si3n4_squeezed_ring()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    result = model(wl=1.55, P_in_mW=7.59)
    print(f"\nModel results at 1550 nm, 7.59 mW pump:")
    print(f"  |S21|: {abs(result['S21']):.4f}")
    print(f"  Squeezing: {result['squeezing_dB']:.2f} dB")
    print(f"  Q-factor: {result['Q_factor']:.2e}")
    
    # Show paper parameters
    print("\n--- Paper Parameters (arXiv:2502.16278) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
