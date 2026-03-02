
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_ComparisonofLumerica_313(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Comparison of Lumerical FDTD and Tidy3D for three-dimensional FDTD simulations of passivesiliconphotoniccomponents
    Source: https://arxiv.org/abs/2506.16665
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
