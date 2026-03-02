
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Highlyefficientbroad_134(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Highly-efficient broadband TE/TMpolarizationbeamsplitter
    Source: https://arxiv.org/abs/2104.07558
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
