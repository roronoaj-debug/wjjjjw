
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_OpticalFiberWaveguid_182(
    length: float = 2.7,
    gap: float = 100.0,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Optical Fiber-Waveguide Hybrid Architecture for Mid-Infrared Ring Lasers
    Source: https://arxiv.org/abs/2509.03965
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
