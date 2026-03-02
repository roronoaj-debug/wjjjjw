
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_OpticalReadingofNano_112(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Optical Reading of Nanoscale Magnetic Bits in an IntegratedPhotonicPlatform
    Source: https://arxiv.org/abs/2208.02560
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
