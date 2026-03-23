"""
Name: lnoi_mmi_splitter

Description: Multimode interferometer (MMI) beam splitter on thin-film lithium niobate 
on insulator (LNOI) platform at telecom wavelength. Combines low propagation loss of 
LNOI with compact MMI design for high-performance electro-optic PICs.

ports:
  - o1: Input port
  - o2: Output port 1
  - o3: Output port 2

NodeLabels:
  - LNOI_MMI
  - Beam_Splitter
  - EO_Compatible

Bandwidth:
  - C-band (1550 nm)
  - Broadband operation

Args:
  - mmi_width: MMI width in µm
  - mmi_length: MMI length in µm
  - taper_length: Taper length in µm

Reference:
  - Paper: "Statistical Characterization of MMI Beam Splitters on Thin Film Lithium 
            Niobate on Insulator (LNOI) Platform at Telecom Wavelength"
  - IEEE Conference 2023
  - Authors: Alain Monney et al.
"""

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import numpy as jnp

# Paper-extracted parameters from IEEE/LNOI platform
PAPER_PARAMS = {
    # Platform
    "platform": "LNOI (Thin-film LN on Insulator)",
    "material": "Lithium Niobate (X-cut)",
    "substrate": "SiO2 on Si",
    
    # Typical LNOI parameters
    "film_thickness_nm": 400,  # Typical
    "waveguide_width_nm": 800,
    "etch_depth_nm": 200,  # Partial etch
    
    # MMI typical specs
    "mmi_type": "1x2 or 2x2",
    "splitting_ratio": "50:50",
    "insertion_loss_dB": "<0.5 typical",
    "imbalance_dB": "<0.3",
    
    # Electro-optic compatibility
    "eo_coefficient_pm_V": 31,  # r33
    "modulation": "Compatible with traveling-wave electrodes",
    
    # Fabrication
    "fabrication": "E-beam or DUV lithography + dry etching",
    
    # Applications
    "applications": [
        "High-speed modulators",
        "Coherent receivers",
        "Quantum photonics",
        "Microwave photonics",
    ],
}


@gf.cell
def lnoi_mmi_splitter(
    mmi_width: float = 6.0,
    mmi_length: float = 25.0,
    taper_width: float = 1.5,
    taper_length: float = 5.0,
    waveguide_width: float = 0.8,
    gap_outputs: float = 2.0,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """
    1x2 MMI beam splitter on LNOI platform.
    
    Based on IEEE characterization of LNOI MMI splitters
    demonstrating low-loss telecom operation.
    
    Args:
        mmi_width: MMI multimode region width in µm
        mmi_length: MMI length in µm
        taper_width: Taper end width in µm
        taper_length: Input/output taper length in µm
        waveguide_width: Access waveguide width in µm
        gap_outputs: Gap between output ports in µm
        cross_section: Cross-section specification
        
    Returns:
        gf.Component: LNOI MMI beam splitter
    """
    c = gf.Component()
    
    # Use gdsfactory's MMI component
    mmi = c << gf.components.mmi1x2(
        width=waveguide_width,
        width_taper=taper_width,
        length_taper=taper_length,
        length_mmi=mmi_length,
        width_mmi=mmi_width,
        gap_mmi=gap_outputs,
        cross_section=cross_section,
    )
    
    # Add ports
    c.add_port("o1", port=mmi.ports["o1"])
    c.add_port("o2", port=mmi.ports["o2"])
    c.add_port("o3", port=mmi.ports["o3"])
    
    # Add info
    c.info["platform"] = "LNOI"
    c.info["splitting_ratio"] = "50:50"
    c.info["mmi_length_um"] = mmi_length
    
    return c


def get_model():
    """
    Returns SAX-compatible analytical model for the LNOI MMI splitter.
    
    The model includes:
    - MMI self-imaging
    - LNOI material properties
    - Wavelength dependence
    """
    
    def lnoi_mmi_model(
        wl: float = 1.55,
        mmi_width_um: float = 6.0,
        mmi_length_um: float = 25.0,
        n_lnoi: float = 2.14,  # LN ordinary index
        n_oxide: float = 1.44,
        etch_depth_ratio: float = 0.5,  # Partial etch
        insertion_loss_dB: float = 0.3,
        imbalance_dB: float = 0.2,
    ) -> dict:
        """
        Analytical model for LNOI MMI beam splitter.
        
        Args:
            wl: Wavelength in µm
            mmi_width_um: MMI width in µm
            mmi_length_um: MMI length in µm
            n_lnoi: LN refractive index
            n_oxide: Cladding refractive index
            etch_depth_ratio: Ratio of etched depth
            insertion_loss_dB: Total insertion loss in dB
            imbalance_dB: Power imbalance between outputs in dB
            
        Returns:
            dict: S-parameters and MMI metrics
        """
        # Effective index for LNOI rib waveguide
        n_eff = n_lnoi * etch_depth_ratio + n_oxide * (1 - etch_depth_ratio)
        n_eff = 1.9  # Approximate for 400nm LNOI
        
        # MMI beat length
        W_eff = mmi_width_um + wl / (n_lnoi * jnp.pi)  # Effective width
        L_pi = 4 * n_eff * W_eff**2 / (3 * wl)
        
        # For 1x2 MMI, optimal length ≈ 3/4 * L_pi
        L_optimal = 0.75 * L_pi
        length_error = (mmi_length_um - L_optimal) / L_optimal
        
        # Splitting efficiency
        eta_split = 1 - 0.5 * length_error**2
        eta_split = jnp.clip(eta_split, 0.8, 1.0)
        
        # Loss
        loss = 10 ** (-insertion_loss_dB / 20)
        
        # Imbalance
        imbalance_linear = 10 ** (imbalance_dB / 20)
        
        # Power splitting
        P_total = loss**2 * eta_split
        P_out1 = P_total / (1 + imbalance_linear) * imbalance_linear
        P_out2 = P_total / (1 + imbalance_linear)
        
        # Field transmission
        S21 = jnp.sqrt(P_out1) * jnp.exp(1j * jnp.pi / 4)
        S31 = jnp.sqrt(P_out2) * jnp.exp(1j * jnp.pi / 4)
        
        # Reflection (minimal)
        S11 = 0.01
        
        # Phase from MMI propagation
        phase_mmi = 2 * jnp.pi * n_eff * mmi_length_um / wl
        
        # Bandwidth estimate
        # MMI has wide bandwidth, limited by beat length dispersion
        bandwidth_nm = 100 / (1 + jnp.abs(length_error) * 10)
        
        return {
            # S-parameters
            "S21": S21,
            "S31": S31,
            "S11": S11,
            # Power splitting
            "output1_power": P_out1,
            "output2_power": P_out2,
            "total_transmission": P_out1 + P_out2,
            # Metrics
            "insertion_loss_dB": -10 * jnp.log10(P_out1 + P_out2 + 1e-10),
            "imbalance_dB": 10 * jnp.log10(P_out1 / (P_out2 + 1e-10)),
            "splitting_efficiency": eta_split,
            # Design
            "L_pi_um": L_pi,
            "L_optimal_um": L_optimal,
            "length_error_percent": length_error * 100,
            # Bandwidth
            "bandwidth_nm": bandwidth_nm,
        }
    
    return lnoi_mmi_model


# Test code
if __name__ == "__main__":
    # Create component
    c = lnoi_mmi_splitter()
    print(f"Component: {c.name}")
    print(f"Ports: {list(c.ports.keys())}")
    
    # Test model
    model = get_model()
    
    print("\n--- LNOI MMI 1x2 Splitter ---")
    result = model(wl=1.55, mmi_width_um=6.0, mmi_length_um=25.0)
    print(f"  Output 1 power: {result['output1_power']*100:.1f}%")
    print(f"  Output 2 power: {result['output2_power']*100:.1f}%")
    print(f"  Insertion loss: {result['insertion_loss_dB']:.2f} dB")
    print(f"  Imbalance: {result['imbalance_dB']:.2f} dB")
    
    # Wavelength dependence
    print("\n--- Wavelength Response ---")
    for wl in [1.50, 1.53, 1.55, 1.57, 1.60]:
        result = model(wl=wl)
        loss = result['insertion_loss_dB']
        imb = result['imbalance_dB']
        print(f"  λ={wl} µm: Loss={loss:.2f} dB, Imbalance={imb:.2f} dB")
    
    # Design optimization
    print("\n--- Design Analysis ---")
    result = model(wl=1.55, mmi_width_um=6.0)
    print(f"  Beat length (L_π): {result['L_pi_um']:.1f} µm")
    print(f"  Optimal MMI length: {result['L_optimal_um']:.1f} µm")
    print(f"  Estimated bandwidth: {result['bandwidth_nm']:.0f} nm")
    
    # Paper parameters
    print("\n--- Paper Parameters (IEEE LNOI MMI) ---")
    for key, value in PAPER_PARAMS.items():
        print(f"  {key}: {value}")
