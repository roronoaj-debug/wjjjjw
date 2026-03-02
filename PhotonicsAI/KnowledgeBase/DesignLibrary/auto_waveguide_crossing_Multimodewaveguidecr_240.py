
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_Multimodewaveguidecr_240(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Multimodewaveguidecrossingbased on square Maxwell's fisheye lens
    Source: https://arxiv.org/abs/1906.04366
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
