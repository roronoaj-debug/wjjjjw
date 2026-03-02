
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_UltralowVLSiliconEle_429(
    length: float = 0.6,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Ultralow-VπLSiliconElectro-OpticDirectionalCouplerSwitch with a Liquid Crystal Cladding
    Source: https://arxiv.org/abs/2507.14729
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
