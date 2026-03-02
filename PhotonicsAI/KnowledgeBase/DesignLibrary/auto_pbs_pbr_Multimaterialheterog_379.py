
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Multimaterialheterog_379(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Multi-material heterogeneous integration on a 3-DPhotonic-CMOS platform
    Source: https://arxiv.org/abs/2304.06796
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
