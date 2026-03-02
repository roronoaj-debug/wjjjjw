
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_3times3Slotwaveguide_552(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: 3\times3 Slotwaveguidecrossingbased on Maxwell's fisheye lens
    Source: https://arxiv.org/abs/1909.01252
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
