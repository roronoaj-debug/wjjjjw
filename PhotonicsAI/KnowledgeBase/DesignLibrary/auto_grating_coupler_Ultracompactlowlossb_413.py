
import gdsfactory as gf

@gf.cell
def auto_grating_coupler_Ultracompactlowlossb_413(
    period: float = 0.63,
    fill_factor: float = 0.5,
) -> gf.Component:
    """Auto-generated Grating Coupler from: Ultra-compact low-loss broadband waveguide taper in silicon-on-insulator
    Source: https://arxiv.org/abs/1705.01698
    """
    c = gf.Component()
    # 聚焦型光栅耦合器
    ref = c << gf.components.grating_coupler_elliptical(
        period=period,
        fill_factor=fill_factor
    )
    c.add_ports(ref.ports)
    return c
