
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_Lowlossmultilevelope_202(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Low-loss multilevel operation using lossy PCM-integrated silicon photonics
    Source: https://arxiv.org/abs/2402.08803
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
