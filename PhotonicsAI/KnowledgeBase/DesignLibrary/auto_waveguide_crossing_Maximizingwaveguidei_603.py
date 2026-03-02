
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_Maximizingwaveguidei_603(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Maximizing waveguide integration density with multi-plane photonics
    Source: https://arxiv.org/abs/1708.09438
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
