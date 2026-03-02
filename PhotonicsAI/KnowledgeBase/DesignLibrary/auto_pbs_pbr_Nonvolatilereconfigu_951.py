
import gdsfactory as gf

@gf.cell
def auto_pbs_pbr_Nonvolatilereconfigu_951(
    length: float = 2.0,
) -> gf.Component:
    """Auto-generated PBS/PBR from: Nonvolatile reconfigurablepolarizationrotatorat datacom wavelengths based on a Sb2Se3/Si waveguide
    Source: https://arxiv.org/abs/2407.04477
    """
    c = gf.Component()
    # 示例使用非对称定向耦合器作为PBS
    ref = c << gf.components.coupler_asymmetric(length=length)
    c.add_ports(ref.ports)
    return c
