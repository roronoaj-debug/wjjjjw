
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_CMOSphotonicintegrat_774(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: CMOSphotonicintegrated source of ultrabroadbandpolarization-entangledphotons
    Source: https://arxiv.org/abs/2402.09307
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
