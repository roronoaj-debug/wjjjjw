
import gdsfactory as gf

@gf.cell
def auto_grating_coupler_LaserStructuredOptic_650(
    period: float = 0.63,
    fill_factor: float = 0.5,
) -> gf.Component:
    """Auto-generated Grating Coupler from: Laser Structured Optical Interposer for Ultra-dense Vertical Coupling of Multi-core Fibers toSiliconPhotonic Chip
    Source: https://arxiv.org/abs/2512.01972
    """
    c = gf.Component()
    # 聚焦型光栅耦合器
    ref = c << gf.components.grating_coupler_elliptical(
        period=period,
        fill_factor=fill_factor
    )
    c.add_ports(ref.ports)
    return c
