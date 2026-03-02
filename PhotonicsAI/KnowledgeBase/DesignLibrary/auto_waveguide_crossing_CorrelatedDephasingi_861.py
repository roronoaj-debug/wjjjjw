
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_CorrelatedDephasingi_861(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Correlated Dephasing in a Piezoelectrically TransducedSiliconPhononicWaveguide
    Source: https://arxiv.org/abs/2502.16426
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
