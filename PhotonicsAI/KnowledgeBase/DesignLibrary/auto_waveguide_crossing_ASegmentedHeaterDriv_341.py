
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_ASegmentedHeaterDriv_341(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: A Segmented Heater-Driven, Low-Loss, ReconfigurablePhotonicPhase-Change Material-Based Phase Shifter
    Source: https://arxiv.org/abs/2512.18800
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
