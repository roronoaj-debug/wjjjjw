
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_Secondharmonicgenera_803(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Second harmonic generation insiliconnitridewaveguidesintegrated with MoS_2monolayers: the importance of a full vectorial modeling
    Source: https://arxiv.org/abs/2501.10575
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
