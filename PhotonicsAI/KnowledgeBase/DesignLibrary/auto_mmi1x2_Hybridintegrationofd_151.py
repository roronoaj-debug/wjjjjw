
import gdsfactory as gf

@gf.cell
def auto_mmi1x2_Hybridintegrationofd_151(
    length_mmi: float = 10.0,
    width_mmi: float = 4.0,
    gap_mmi: float = 0.25,
    width_taper: float = 1.0,
    length_taper: float = 5.0,
) -> gf.Component:
    """Auto-generated 1x2 MMI from: Hybrid integration of deterministic quantum dots-based single-photonsources with CMOS-compatiblesiliconcarbidephotonics
    Source: https://arxiv.org/abs/2203.12202
    """
    c = gf.Component()
    ref = c << gf.components.mmi1x2(
        length_mmi=length_mmi,
        width_mmi=width_mmi,
        gap_mmi=gap_mmi,
        width_taper=width_taper,
        length_taper=length_taper,
    )
    c.add_ports(ref.ports)
    return c
