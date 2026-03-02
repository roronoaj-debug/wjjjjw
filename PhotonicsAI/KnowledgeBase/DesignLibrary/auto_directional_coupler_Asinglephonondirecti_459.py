
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Asinglephonondirecti_459(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: A single-phonondirectionalcoupler
    Source: https://arxiv.org/abs/2312.04414
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
