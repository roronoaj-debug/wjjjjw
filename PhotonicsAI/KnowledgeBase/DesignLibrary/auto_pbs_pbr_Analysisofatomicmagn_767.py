
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Analysisofatomicmagn_767(
    length: float = 795.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Analysis of atomic magnetometry using metasurface optics for balanced polarimetry
    Source: https://arxiv.org/abs/2210.04952
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
