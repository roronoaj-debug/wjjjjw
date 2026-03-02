
import gdsfactory as gf

@gf.cell
def auto_si_phase_shifter_UltralowcrosstalkSil_845(
    length: float = 100.0,
    heater_width: float = 2.0,
) -> gf.Component:
    """Auto-generated Thermo-optic Phase Shifter from: Ultra-low-crosstalk Silicon Switches Driven Thermally and Electrically
    Source: https://arxiv.org/abs/2410.00592
    """
    c = gf.Component()
    # 带加热器的直波导
    ref = c << gf.components.straight_heater_metal(
        length=length,
        heater_width=heater_width
    )
    c.add_ports(ref.ports)
    return c
