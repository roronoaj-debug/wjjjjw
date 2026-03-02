
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_Demonstrationofonchi_498(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Demonstration of on-chip all-optical switching of magnetization in integratedphotonics
    Source: https://arxiv.org/abs/2511.02440
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
