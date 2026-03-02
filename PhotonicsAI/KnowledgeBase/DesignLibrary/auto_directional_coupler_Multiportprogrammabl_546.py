
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Multiportprogrammabl_546(
    length: float = 220.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Multi-port programmablesiliconphotonics using low-loss phase change material Sb_2Se_3
    Source: https://arxiv.org/abs/2511.18205
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
