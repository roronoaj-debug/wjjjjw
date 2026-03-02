
import gdsfactory as gf

@gf.cell
def auto_mmi2x2_Analyzingandgenerati_587(
    length_mmi: float = 25.0,
    width_mmi: float = 6.0,
    gap_mmi: float = 0.25,
    width_taper: float = 1.0,
    length_taper: float = 5.0,
) -> gf.Component:
    """Auto-generated 2x2 MMI from: Analyzing and generatingmultimodeoptical fields using self-configuring networks
    Source: https://arxiv.org/abs/2002.12270
    """
    c = gf.Component()
    ref = c << gf.components.mmi2x2(
        length_mmi=length_mmi,
        width_mmi=width_mmi,
        gap_mmi=gap_mmi,
        width_taper=width_taper,
        length_taper=length_taper,
    )
    c.add_ports(ref.ports)
    return c
