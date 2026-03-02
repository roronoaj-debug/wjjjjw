
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_IntegratedSiliconNit_771(
    length: float = 1200.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: IntegratedSiliconNitride Devices via InverseDesign
    Source: https://arxiv.org/abs/2505.02662
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
