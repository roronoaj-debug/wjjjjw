
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Broadbandsiliconpola_746(
    length: float = 20.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Broadbandsiliconpolarizationbeamsplitterbased on Floquet engineering
    Source: https://arxiv.org/abs/2601.11955
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
