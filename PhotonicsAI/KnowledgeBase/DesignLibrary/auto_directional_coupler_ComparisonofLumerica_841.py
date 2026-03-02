
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_ComparisonofLumerica_841(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Comparison of Lumerical FDTD and Tidy3D for three-dimensional FDTD simulations of passivesiliconphotonic components
    Source: https://arxiv.org/abs/2506.16665
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
