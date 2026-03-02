
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_2Dsemiconductorsasin_627(
    length: float = 20.0,
    gap: float = 2.0,
) -> gf.Component:
    """Auto-generated Directional Coupler from: 2D semiconductors as integrated light sources for plasmonicwaveguides
    Source: https://arxiv.org/abs/2506.21806
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
