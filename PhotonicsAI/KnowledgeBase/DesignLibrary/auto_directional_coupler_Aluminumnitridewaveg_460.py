
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Aluminumnitridewaveg_460(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Aluminum nitride waveguide beam splitters for integrated quantum photonic circuits
    Source: https://arxiv.org/abs/2208.01377
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
