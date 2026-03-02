
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Alowlossandbroadband_193(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: A low-loss and broadband all-fiber acousto-optic circulator
    Source: https://arxiv.org/abs/2405.12903
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
