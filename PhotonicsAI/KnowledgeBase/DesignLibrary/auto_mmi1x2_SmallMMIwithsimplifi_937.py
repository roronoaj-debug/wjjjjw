
import gdsfactory as gf

@gf.cell
def auto_mmi1x2_SmallMMIwithsimplifi_937(
    length_mmi: float = 10.0,
    width_mmi: float = 4.0,
    gap_mmi: float = 0.25,
    width_taper: float = 1.0,
    length_taper: float = 5.0,
) -> gf.Component:
    """Auto-generated 1x2 MMI from: SmallMMIwith simplified coherent coupling branches used to develop a lower footprint power splitter on SOI platform
    Source: https://arxiv.org/abs/1909.09538
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
