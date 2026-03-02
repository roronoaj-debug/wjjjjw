
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_PreparingsingleSiVce_840(
    length: float = 30.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Preparing single SiV^{-}center in nanodiamonds for external, optical coupling with access to all degrees of freedom
    Source: https://arxiv.org/abs/1908.01591
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
