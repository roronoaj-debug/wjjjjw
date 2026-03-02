
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Siliconnitrideonchip_848(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Siliconnitride on-chip C-band spontaneous emission generation based on lanthanide doped microparticles
    Source: https://arxiv.org/abs/2507.11189
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
