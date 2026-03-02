
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_ProgrammablePhotonic_662(
    length: float = 50.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Programmable Photonic Circuit for Optical Logic Operations and 2-Bit Decoding
    Source: https://arxiv.org/abs/2509.20825
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
