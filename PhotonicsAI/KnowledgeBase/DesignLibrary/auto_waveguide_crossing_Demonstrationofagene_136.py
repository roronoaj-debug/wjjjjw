
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_Demonstrationofagene_136(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Demonstration of a genetic-algorithm-optimized cavity-basedwaveguidecrossing
    Source: https://arxiv.org/abs/1712.03743
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
