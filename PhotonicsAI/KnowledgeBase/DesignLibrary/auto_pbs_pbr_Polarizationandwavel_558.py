
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Polarizationandwavel_558(
    length: float = 3.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Polarizationand wavelength agnostic nanophotonicbeamsplitter
    Source: https://arxiv.org/abs/1807.05952
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
