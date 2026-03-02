
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_DesignofSiliconPhoto_506(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Design ofSiliconPhotonicmicroring resonators with complexwaveguidecross-sections and minimal non-linearity
    Source: https://arxiv.org/abs/2506.22077
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
