
import gdsfactory as gf

@gf.cell
def auto_directional_coupler_LaserStructuredOptic_593(
    length: float = 20.0,
    gap: float = 0.2,
) -> gf.Component:
    """Auto-generated Directional Coupler from: Laser Structured Optical Interposer for Ultra-dense Vertical Coupling of Multi-core Fibers toSiliconPhotonic Chip
    Source: https://arxiv.org/abs/2512.01972
    """
    c = gf.Component()
    ref = c << gf.components.coupler(length=length, gap=gap)
    c.add_ports(ref.ports)
    return c
