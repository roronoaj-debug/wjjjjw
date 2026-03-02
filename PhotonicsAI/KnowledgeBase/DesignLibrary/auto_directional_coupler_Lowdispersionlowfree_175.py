
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Lowdispersionlowfree_175(
    length: float = 0.41,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Low-dispersion low free-spectral-range Mach-Zehnder interferometer with long straight path lengths onsilicon
    Source: https://arxiv.org/abs/2507.01114
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
