
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_UltralowlossCMOSComp_444(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Ultra-low-lossCMOS-CompatibleWaveguideCrossingArrays Based on Multimode Bloch Waves and Imaginary Coupling
    Source: https://arxiv.org/abs/1311.4277
    """
    c = gf.Component()
    ref = c << gf.components.crossing(width=width)
    c.add_ports(ref.ports)
    return c
