
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Polarizationbasedmod_116(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Polarization based modulation ofsplittingratioin femtosecond laser direct writtendirectionalcouplers
    Source: https://arxiv.org/abs/2311.11743
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
