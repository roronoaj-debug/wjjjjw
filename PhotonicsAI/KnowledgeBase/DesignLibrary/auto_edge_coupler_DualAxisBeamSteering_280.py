
import gdsfactory as gf

@gf.cell
def auto_edge_coupler_DualAxisBeamSteering_280(
    width_tip: float = 0.15,
    length_taper: float = 150.0,
) -> gf.Component:
    """Auto-generated Edge Coupler (SSC) from: Dual-Axis Beam-Steering OPA with purely Passive Phase Shifters
    Source: https://arxiv.org/abs/2412.06801
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
