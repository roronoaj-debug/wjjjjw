
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_HighFidelityIntegrat_481(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: High-Fidelity Integrated Quantum Photonic Logic Via RobustDirectionalCouplers
    Source: https://arxiv.org/abs/2502.20069
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
