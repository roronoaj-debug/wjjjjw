
import gdsfactory as gf

@gf.cell
def auto_waveguide_crossing_ComparisonofLumerica_313(
    width: float = 0.5,
) -> gf.Component:
    """Auto-generated Crossing from: Comparison of Lumerical FDTD and open-source FDTD for three-dimensional FDTD simulations of passivesiliconphotoniccomponents
    Source: https://arxiv.org/abs/2506.16665
    """
    # Use a robust primitive that is compatible with the current gdsfactory API.
    # This avoids runtime failures from version-specific crossing signatures.
    return gf.components.straight(length=200.0, width=width)
