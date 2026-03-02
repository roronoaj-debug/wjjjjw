
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Siliconbaseddecoderf_257(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Silicon-based decoder forpolarization-encoding quantum key distribution
    Source: https://arxiv.org/abs/2212.04019
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
