
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Integratedpolarizati_342(
    length: float = 0.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Integratedpolarization-entangledphotonsource for wavelength-multiplexed quantum networks
    Source: https://arxiv.org/abs/2511.22680
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
