
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Secondorderadddropfi_816(
    length: float = 50.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Second order add/drop filter with a single ring resonator
    Source: https://arxiv.org/abs/2304.11146
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
