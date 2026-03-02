
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_LightProALinearPhoto_948(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: LightPro: A Linear Photonic Processor with Full Programmability
    Source: https://arxiv.org/abs/2510.27013
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
