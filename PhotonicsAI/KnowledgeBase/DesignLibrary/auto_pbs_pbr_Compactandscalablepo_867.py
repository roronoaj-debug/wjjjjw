
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Compactandscalablepo_867(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Compact and scalable polarimetric self-coherent receiver using dielectric metasurface
    Source: https://arxiv.org/abs/2301.01942
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
