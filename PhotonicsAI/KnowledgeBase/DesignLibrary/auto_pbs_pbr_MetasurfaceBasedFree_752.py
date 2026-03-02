
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_MetasurfaceBasedFree_752(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Metasurface-Based Free-Space Multi-portBeamSplitterwith Arbitrary Power Ratio
    Source: https://arxiv.org/abs/2212.01009
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
