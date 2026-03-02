
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Experimentalstudyofa_839(
    length: float = 10.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Experimental study of a tunable hybrid III-V-on-siliconlaser for spectral characterization of fiber Bragg grating sensors
    Source: https://arxiv.org/abs/2405.07581
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
