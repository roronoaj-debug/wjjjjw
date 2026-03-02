
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_BroadbandandUltraCom_837(
    length: float = 1.44,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Broadband and Ultra-Compact AdiabaticCouplerBased on Linearly TaperedSiliconWaveguides
    Source: https://arxiv.org/abs/2504.20512
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
