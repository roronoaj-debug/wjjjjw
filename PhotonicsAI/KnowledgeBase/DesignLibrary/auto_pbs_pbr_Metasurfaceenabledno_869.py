
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Metasurfaceenabledno_869(
    length: float = 1500.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Metasurface-enabled non-orthogonal four-output polarization splitter for non-redundant full-Stokes imaging
    Source: https://arxiv.org/abs/2405.10634
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
