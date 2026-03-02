
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Broadbandsiliconpola_706(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Broadbandsiliconpolarization beam splitter based on Floquet engineering
    Source: https://arxiv.org/abs/2601.11955
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
