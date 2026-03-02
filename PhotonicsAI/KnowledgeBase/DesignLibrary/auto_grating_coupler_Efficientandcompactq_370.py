
import gdsfactory as gf

@gf.cell
def auto_grating_coupler_Efficientandcompactq_370(
    period: float = 0.63,
    fill_factor: float = 0.5,
) -> gf.Component:
    """Auto-generated Grating Coupler from: Efficientand compact quantum network node based on a parabolic mirror on an opticalchip
    Source: https://arxiv.org/abs/2601.13420
    """
    c = gf.Component()
    # 聚焦型光栅耦合器
    ref = c << gf.components.grating_coupler_elliptical(
        period=period,
        fill_factor=fill_factor
    )
    c.add_ports(ref.ports)
    return c
