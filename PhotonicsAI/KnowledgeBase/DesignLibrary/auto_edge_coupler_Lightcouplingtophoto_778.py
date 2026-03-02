
import gdsfactory as gf

@gf.cell
def auto_edge_coupler_Lightcouplingtophoto_778(
    width_tip: float = 0.15,
    length_taper: float = 150.0,
) -> gf.Component:
    """Auto-generated Edge Coupler (SSC) from: Lightcouplingto photonic integrated circuits using optimized lensed fibers
    Source: https://arxiv.org/abs/2510.10635
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
