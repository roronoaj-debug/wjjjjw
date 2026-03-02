
import gdsfactory as gf

@gf.cell
def auto_edge_coupler_ThreeWaveInteraction_511(
    width_tip: float = 0.15,
    length_taper: float = 1546.0,
) -> gf.Component:
    """Auto-generated Edge Coupler (SSC) from: Three-Wave Interaction GratingCouplerwith Sub-Decibel Insertion Loss at Normal Incidence
    Source: https://arxiv.org/abs/2506.19242
    """
    c = gf.Component()
    # 倒锥形耦合器 (Inverse Taper)
    ref = c << gf.components.taper(
        width1=width_tip,
        width2=0.5,
        length=length_taper
    )
    c.add_ports(ref.ports)
    return c
