
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Metasurfacepolarizat_390(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Metasurfacepolarizationsplitter
    Source: https://arxiv.org/abs/1610.04040
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
