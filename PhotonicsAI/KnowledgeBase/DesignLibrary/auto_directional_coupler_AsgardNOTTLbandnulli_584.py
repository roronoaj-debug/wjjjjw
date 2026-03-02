
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_AsgardNOTTLbandnulli_584(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Asgard/NOTT: L-band nulling interferometry at the VLTI -- III. The mid-infrared integrated optics beam combiner for NOTT
    Source: https://arxiv.org/abs/2511.19790
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
