
import gdsfactory as gf

@gf.cell
def auto_si_phase_shifter_Efficientthermooptic_400(
    length: float = 1550.0,
    heater_width: float = 2.0,
) -> gf.Component:
    """Auto-generated Thermo-optic Phase Shifter from: Efficientthermo-optic micro-ring phase shifter made of PECVDsilicon-rich amorphoussiliconcarbide
    Source: https://arxiv.org/abs/2209.13033
    """
    c = gf.Component()
    # 带加热器的直波导
    ref = c << gf.components.straight_heater_metal(
        length=length,
        heater_width=heater_width
    )
    c.add_ports(ref.ports)
    return c
