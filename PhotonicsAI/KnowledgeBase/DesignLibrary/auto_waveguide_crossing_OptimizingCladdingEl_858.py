
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_OptimizingCladdingEl_858(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Optimizing Cladding Elasticity to Enhance Sensitivity inSiliconPhotonicUltrasound Sensors
    Source: https://arxiv.org/abs/2410.18642
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
