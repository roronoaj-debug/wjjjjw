
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_SiliconphotonicMEMSs_262(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Siliconphotonic MEMS switches based on splitwaveguidecrossings
    Source: https://arxiv.org/abs/2305.17366
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
