
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_Onchipprocessingofop_392(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: On-chip processing of optical orbital angular momentum
    Source: https://arxiv.org/abs/2510.16507
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
