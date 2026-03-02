
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Freespaceopticsintwo_456(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Free space optics in two dimensions: optical elements forsiliconphotonics without lateral confinement
    Source: https://arxiv.org/abs/2512.20731
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
