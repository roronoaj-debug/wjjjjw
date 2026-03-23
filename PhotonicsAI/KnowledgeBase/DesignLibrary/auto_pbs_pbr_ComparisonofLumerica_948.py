
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_ComparisonofLumerica_948(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Comparison of Lumerical FDTD and open-source FDTD for three-dimensional FDTD simulations of passivesiliconphotoniccomponents
    Source: https://arxiv.org/abs/2506.16665
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
