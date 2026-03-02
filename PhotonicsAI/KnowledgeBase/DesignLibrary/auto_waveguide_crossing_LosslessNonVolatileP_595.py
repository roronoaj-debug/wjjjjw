
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_LosslessNonVolatileP_595(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Lossless, Non-Volatile Post-Fabrication Trimming of PICs via On-Chip High-Temperature Annealing of UndercutWaveguides
    Source: https://arxiv.org/abs/2506.18633
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
