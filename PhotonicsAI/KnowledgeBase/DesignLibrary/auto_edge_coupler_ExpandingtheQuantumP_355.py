
import gdsfactory as gf

@gf.cell
def auto_edge_coupler_ExpandingtheQuantumP_355(
    width_tip: float = 0.15,
    length_taper: float = 150.0,
) -> gf.Component:
    """Auto-generated Edge Coupler (SSC) from: Expanding the QuantumPhotonicToolbox in AlGaAsOI
    Source: https://arxiv.org/abs/2205.06912
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
